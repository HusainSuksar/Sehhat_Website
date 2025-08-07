"""
API Views for the Moze app
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import Moze, UmoorSehhatTeam, MozeComment, MozeSettings
from .serializers import (
    MozeSerializer, MozeCreateSerializer, UmoorSehhatTeamSerializer,
    MozeCommentSerializer, MozeSettingsSerializer, MozeStatsSerializer,
    TeamStatsSerializer, MozeSearchSerializer, TeamSearchSerializer
)


# Custom Permission Classes
class IsAdminOrAamil(permissions.BasePermission):
    """
    Permission for admins and aamils to manage Moze content
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_admin or request.user.role == 'aamil'))


class IsMozeStaffOrAdmin(permissions.BasePermission):
    """
    Permission for Moze staff (aamil, coordinator, team members) and admins
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Get the Moze object
        if hasattr(obj, 'moze'):
            moze = obj.moze
        elif isinstance(obj, Moze):
            moze = obj
        else:
            return False
        
        # Check if user is aamil of this Moze
        if moze.aamil == user:
            return True
        
        # Check if user is coordinator of this Moze
        if moze.moze_coordinator == user:
            return True
        
        # Check if user is team member of this Moze
        if user in moze.team_members.all():
            return True
        
        # Check if user is in Umoor Sehhat team for this Moze
        if moze.umoor_teams.filter(member=user, is_active=True).exists():
            return True
        
        return False


class IsCommentAuthorOrMozeStaff(permissions.BasePermission):
    """
    Permission for comment authors or Moze staff to edit comments
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Comment author can edit their own comments
        if obj.author == user:
            return True
        
        # Moze staff can moderate comments
        moze = obj.moze
        return (moze.aamil == user or 
                moze.moze_coordinator == user or 
                user in moze.team_members.all() or
                moze.umoor_teams.filter(member=user, is_active=True).exists())


# Access Control Mixins
class MozeAccessMixin:
    """
    Mixin to filter Moze data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admin can see all Mozes
            return Moze.objects.all()
        elif user.role == 'aamil':
            # Aamil can see Mozes they manage
            return Moze.objects.filter(aamil=user)
        elif user.role == 'moze_coordinator':
            # Coordinator can see Mozes they coordinate
            return Moze.objects.filter(moze_coordinator=user)
        else:
            # Team members can see Mozes they're part of
            return Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).distinct()


class TeamAccessMixin:
    """
    Mixin to filter team data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return UmoorSehhatTeam.objects.all()
        elif user.role == 'aamil':
            # Aamil can see teams from their Mozes
            return UmoorSehhatTeam.objects.filter(moze__aamil=user)
        elif user.role == 'moze_coordinator':
            # Coordinator can see teams from their Mozes
            return UmoorSehhatTeam.objects.filter(moze__moze_coordinator=user)
        else:
            # Team members can see teams from Mozes they're part of
            moze_ids = Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).values_list('id', flat=True)
            return UmoorSehhatTeam.objects.filter(moze_id__in=moze_ids)


# Moze API Views
class MozeListCreateAPIView(MozeAccessMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'aamil', 'moze_coordinator', 'location']
    search_fields = ['name', 'location', 'address']
    ordering_fields = ['name', 'created_at', 'established_date']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MozeCreateSerializer
        return MozeSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrAamil()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class MozeDetailAPIView(MozeAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MozeSerializer
    permission_classes = [IsMozeStaffOrAdmin]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrAamil()]
        return super().get_permissions()


# Moze Settings API Views
class MozeSettingsListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MozeSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['allow_walk_ins']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return MozeSettings.objects.all()
        elif user.role == 'aamil':
            return MozeSettings.objects.filter(moze__aamil=user)
        elif user.role == 'moze_coordinator':
            return MozeSettings.objects.filter(moze__moze_coordinator=user)
        else:
            moze_ids = Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).values_list('id', flat=True)
            return MozeSettings.objects.filter(moze_id__in=moze_ids)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrAamil()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Ensure the user can manage the Moze
        moze_id = self.request.data.get('moze')
        if moze_id:
            try:
                moze = Moze.objects.get(id=moze_id)
                if not (self.request.user.is_admin or moze.aamil == self.request.user):
                    raise PermissionDenied("You can only create settings for Mozes you manage.")
            except Moze.DoesNotExist:
                raise PermissionDenied("Invalid Moze specified.")
        serializer.save()


class MozeSettingsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MozeSettingsSerializer
    permission_classes = [IsMozeStaffOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return MozeSettings.objects.all()
        elif user.role == 'aamil':
            return MozeSettings.objects.filter(moze__aamil=user)
        elif user.role == 'moze_coordinator':
            return MozeSettings.objects.filter(moze__moze_coordinator=user)
        else:
            moze_ids = Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).values_list('id', flat=True)
            return MozeSettings.objects.filter(moze_id__in=moze_ids)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrAamil()]
        return super().get_permissions()


# Umoor Sehhat Team API Views
class UmoorSehhatTeamListCreateAPIView(TeamAccessMixin, generics.ListCreateAPIView):
    serializer_class = UmoorSehhatTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active', 'moze']
    search_fields = ['member__first_name', 'member__last_name', 'position', 'moze__name']
    ordering_fields = ['created_at', 'member__first_name', 'category']
    ordering = ['category', 'member__first_name']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrAamil()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Ensure the user can manage the Moze
        moze_id = self.request.data.get('moze')
        if moze_id:
            try:
                moze = Moze.objects.get(id=moze_id)
                if not (self.request.user.is_admin or moze.aamil == self.request.user):
                    raise PermissionDenied("You can only add team members to Mozes you manage.")
                
                # Save with the moze
                serializer.save(moze=moze)
            except Moze.DoesNotExist:
                raise PermissionDenied("Invalid Moze specified.")
        else:
            raise PermissionDenied("Moze is required for team members.")


class UmoorSehhatTeamDetailAPIView(TeamAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UmoorSehhatTeamSerializer
    permission_classes = [IsMozeStaffOrAdmin]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrAamil()]
        return super().get_permissions()


# Moze Comments API Views
class MozeCommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MozeCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'moze', 'parent']
    search_fields = ['content', 'author__first_name', 'author__last_name']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return MozeComment.objects.all()
        else:
            # Users can see comments from Mozes they have access to
            accessible_moze_ids = Moze.objects.filter(
                Q(aamil=user) |
                Q(moze_coordinator=user) |
                Q(team_members=user) |
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).values_list('id', flat=True)
            
            return MozeComment.objects.filter(
                moze_id__in=accessible_moze_ids,
                is_active=True
            )
    
    def perform_create(self, serializer):
        # Ensure the user can comment on the Moze
        moze_id = self.request.data.get('moze')
        if moze_id:
            try:
                moze = Moze.objects.get(id=moze_id)
                user = self.request.user
                if not (user.is_admin or 
                       moze.aamil == user or 
                       moze.moze_coordinator == user or 
                       user in moze.team_members.all() or
                       moze.umoor_teams.filter(member=user, is_active=True).exists()):
                    raise PermissionDenied("You can only comment on Mozes you have access to.")
                
                # Save with the moze and author
                serializer.save(author=self.request.user, moze=moze)
            except Moze.DoesNotExist:
                raise PermissionDenied("Invalid Moze specified.")
        else:
            raise PermissionDenied("Moze is required for comments.")


class MozeCommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MozeCommentSerializer
    permission_classes = [IsCommentAuthorOrMozeStaff]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return MozeComment.objects.all()
        else:
            # Users can see comments from Mozes they have access to
            accessible_moze_ids = Moze.objects.filter(
                Q(aamil=user) |
                Q(moze_coordinator=user) |
                Q(team_members=user) |
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).values_list('id', flat=True)
            
            return MozeComment.objects.filter(moze_id__in=accessible_moze_ids)


# Search API Views
class MozeSearchAPIView(generics.ListAPIView):
    serializer_class = MozeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['name']
    
    def get_queryset(self):
        # Use MozeAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            queryset = Moze.objects.all()
        elif user.role == 'aamil':
            queryset = Moze.objects.filter(aamil=user)
        elif user.role == 'moze_coordinator':
            queryset = Moze.objects.filter(moze_coordinator=user)
        else:
            queryset = Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).distinct()
        
        # Apply search filters from query params directly
        name = self.request.query_params.get('name')
        location = self.request.query_params.get('location')
        aamil = self.request.query_params.get('aamil')
        is_active = self.request.query_params.get('is_active')
        has_coordinator = self.request.query_params.get('has_coordinator')
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if aamil:
            queryset = queryset.filter(aamil__username__icontains=aamil)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if has_coordinator is not None:
            has_coord = has_coordinator.lower() == 'true'
            if has_coord:
                queryset = queryset.filter(moze_coordinator__isnull=False)
            else:
                queryset = queryset.filter(moze_coordinator__isnull=True)
        
        return queryset.distinct().order_by('name')


class TeamSearchAPIView(generics.ListAPIView):
    serializer_class = UmoorSehhatTeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['category', 'member__first_name']
    
    def get_queryset(self):
        # Use TeamAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            queryset = UmoorSehhatTeam.objects.all()
        elif user.role == 'aamil':
            queryset = UmoorSehhatTeam.objects.filter(moze__aamil=user)
        elif user.role == 'moze_coordinator':
            queryset = UmoorSehhatTeam.objects.filter(moze__moze_coordinator=user)
        else:
            moze_ids = Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).values_list('id', flat=True)
            queryset = UmoorSehhatTeam.objects.filter(moze_id__in=moze_ids)
        
        # Apply search filters from query params directly
        category = self.request.query_params.get('category')
        member_name = self.request.query_params.get('member_name')
        moze_name = self.request.query_params.get('moze_name')
        is_active = self.request.query_params.get('is_active')
        position = self.request.query_params.get('position')
        
        if category:
            queryset = queryset.filter(category=category)
        if member_name:
            queryset = queryset.filter(
                Q(member__first_name__icontains=member_name) |
                Q(member__last_name__icontains=member_name)
            )
        if moze_name:
            queryset = queryset.filter(moze__name__icontains=moze_name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if position:
            queryset = queryset.filter(position__icontains=position)
        
        return queryset.distinct().order_by('category', 'member__first_name')


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def moze_stats_api(request):
    """Get Moze statistics"""
    user = request.user
    
    if not (user.is_admin or user.role in ['aamil', 'moze_coordinator']):
        raise PermissionDenied("Insufficient permissions to view statistics.")
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        mozes = Moze.objects.all()
    elif user.role == 'aamil':
        mozes = Moze.objects.filter(aamil=user)
    elif user.role == 'moze_coordinator':
        mozes = Moze.objects.filter(moze_coordinator=user)
    else:
        mozes = Moze.objects.none()
    
    # Calculate stats
    total_mozes = mozes.count()
    active_mozes = mozes.filter(is_active=True).count()
    total_team_members = UmoorSehhatTeam.objects.filter(moze__in=mozes, is_active=True).count()
    
    # Mozes by category (based on team categories present)
    mozes_by_category = {}
    for moze in mozes:
        categories = moze.umoor_teams.filter(is_active=True).values_list('category', flat=True).distinct()
        for category in categories:
            mozes_by_category[category] = mozes_by_category.get(category, 0) + 1
    
    # Average capacity
    avg_capacity = mozes.aggregate(avg=Avg('capacity'))['avg'] or 0
    
    # Mozes with coordinators
    mozes_with_coordinators = mozes.filter(moze_coordinator__isnull=False).count()
    
    stats = {
        'total_mozes': total_mozes,
        'active_mozes': active_mozes,
        'total_team_members': total_team_members,
        'mozes_by_category': mozes_by_category,
        'average_capacity': round(avg_capacity, 2),
        'mozes_with_coordinators': mozes_with_coordinators
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_stats_api(request):
    """Get team statistics"""
    user = request.user
    
    if not (user.is_admin or user.role in ['aamil', 'moze_coordinator']):
        raise PermissionDenied("Insufficient permissions to view team statistics.")
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        teams = UmoorSehhatTeam.objects.all()
        mozes = Moze.objects.all()
    elif user.role == 'aamil':
        teams = UmoorSehhatTeam.objects.filter(moze__aamil=user)
        mozes = Moze.objects.filter(aamil=user)
    elif user.role == 'moze_coordinator':
        teams = UmoorSehhatTeam.objects.filter(moze__moze_coordinator=user)
        mozes = Moze.objects.filter(moze_coordinator=user)
    else:
        teams = UmoorSehhatTeam.objects.none()
        mozes = Moze.objects.none()
    
    # Calculate stats
    total_team_members = teams.count()
    active_team_members = teams.filter(is_active=True).count()
    
    # Members by category
    members_by_category = dict(teams.filter(is_active=True).values_list('category').annotate(count=Count('id')))
    
    # Members by moze
    members_by_moze = dict(teams.filter(is_active=True).values_list('moze__name').annotate(count=Count('id')))
    
    # Average members per moze
    avg_members_per_moze = 0
    if mozes.count() > 0:
        avg_members_per_moze = active_team_members / mozes.count()
    
    stats = {
        'total_team_members': total_team_members,
        'active_team_members': active_team_members,
        'members_by_category': members_by_category,
        'members_by_moze': members_by_moze,
        'average_members_per_moze': round(avg_members_per_moze, 2)
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def moze_dashboard_api(request):
    """Get comprehensive dashboard data for Moze app"""
    user = request.user
    
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
    dashboard_data = {}
    
    try:
        # Role-specific dashboard data
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            # Staff dashboard - compute stats directly
            if user.is_admin or user.is_superuser:
                mozes = Moze.objects.all()
                teams = UmoorSehhatTeam.objects.all()
                comments = MozeComment.objects.all()
            elif user.role == 'aamil':
                mozes = Moze.objects.filter(aamil=user)
                teams = UmoorSehhatTeam.objects.filter(moze__aamil=user)
                comments = MozeComment.objects.filter(moze__aamil=user)
            elif user.role == 'moze_coordinator':
                mozes = Moze.objects.filter(moze_coordinator=user)
                teams = UmoorSehhatTeam.objects.filter(moze__moze_coordinator=user)
                comments = MozeComment.objects.filter(moze__moze_coordinator=user)
            
            # Moze stats
            dashboard_data['moze_stats'] = {
                'total_mozes': mozes.count(),
                'active_mozes': mozes.filter(is_active=True).count(),
                'total_team_members': teams.filter(is_active=True).count(),
                'mozes_with_coordinators': mozes.filter(moze_coordinator__isnull=False).count(),
                'average_capacity': round(mozes.aggregate(avg=Avg('capacity'))['avg'] or 0, 2)
            }
            
            # Team stats
            dashboard_data['team_stats'] = {
                'total_team_members': teams.count(),
                'active_team_members': teams.filter(is_active=True).count(),
                'members_by_category': dict(teams.filter(is_active=True).values_list('category').annotate(count=Count('id')))
            }
            
            # Recent activities
            dashboard_data['recent_mozes'] = MozeSerializer(
                mozes.order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['recent_team_members'] = UmoorSehhatTeamSerializer(
                teams.filter(is_active=True).order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['recent_comments'] = MozeCommentSerializer(
                comments.filter(is_active=True).order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
        else:
            # Regular team member dashboard
            accessible_mozes = Moze.objects.filter(
                Q(team_members=user) | 
                Q(umoor_teams__member=user, umoor_teams__is_active=True)
            ).distinct()
            
            dashboard_data['my_mozes'] = MozeSerializer(
                accessible_mozes,
                many=True, context={'request': request}
            ).data
            
            dashboard_data['my_team_memberships'] = UmoorSehhatTeamSerializer(
                UmoorSehhatTeam.objects.filter(member=user, is_active=True),
                many=True, context={'request': request}
            ).data
        
        # Common data for all users
        dashboard_data['open_mozes'] = []
        for moze in Moze.objects.filter(is_active=True)[:5]:
            if hasattr(moze, 'settings'):
                settings_serializer = MozeSettingsSerializer(moze.settings)
                if settings_serializer.get_is_currently_open(moze.settings):
                    dashboard_data['open_mozes'].append({
                        'id': moze.id,
                        'name': moze.name,
                        'location': moze.location
                    })
        
    except Exception as e:
        dashboard_data['error'] = str(e)
    
    return Response(dashboard_data)