"""
API Views for the Araz app
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.db import transaction
from datetime import datetime, timedelta

from .models import (
    DuaAraz, Petition, PetitionCategory, PetitionComment, ArazComment,
    PetitionAttachment, ArazAttachment, ArazStatusHistory, PetitionAssignment,
    PetitionUpdate, PetitionStatus, ArazNotification
)
from .serializers import (
    DuaArazSerializer, DuaArazCreateSerializer, PetitionSerializer, PetitionCreateSerializer,
    PetitionCategorySerializer, PetitionCommentSerializer, ArazCommentSerializer,
    PetitionAttachmentSerializer, ArazAttachmentSerializer, ArazStatusHistorySerializer,
    PetitionAssignmentSerializer, PetitionUpdateSerializer, PetitionStatusSerializer,
    ArazNotificationSerializer, ArazStatsSerializer, PetitionStatsSerializer,
    ArazSearchSerializer, PetitionSearchSerializer
)
from accounts.serializers import UserSerializer

User = get_user_model()


class ArazAccessMixin:
    """Mixin for Araz-specific access control"""
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admins can see all Araz
            return DuaAraz.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            # Aamils and coordinators can see Araz in their managed Moze centers
            # and their own submissions
            return DuaAraz.objects.filter(
                Q(patient_user=user) |
                Q(assigned_doctor__user=user)
            ).distinct()
        elif user.role == 'doctor':
            # Doctors can see Araz assigned to them or where they're preferred
            return DuaAraz.objects.filter(
                Q(assigned_doctor__user=user) |
                Q(preferred_doctor__user=user) |
                Q(patient_user=user)
            ).distinct()
        else:
            # Regular users can only see their own Araz
            return DuaAraz.objects.filter(patient_user=user)


class PetitionAccessMixin:
    """Mixin for Petition-specific access control"""
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admins can see all petitions
            return Petition.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            # Aamils and coordinators can see petitions in their managed Moze centers
            # and their own submissions
            managed_mozes = []
            if hasattr(user, 'managed_mozes'):
                managed_mozes.extend(user.managed_mozes.all())
            if hasattr(user, 'coordinated_mozes'):
                managed_mozes.extend(user.coordinated_mozes.all())
            
            queryset = Petition.objects.filter(
                Q(created_by=user) |
                Q(moze__in=managed_mozes) |
                Q(assignments__assigned_to=user, assignments__is_active=True)
            ).distinct()
            return queryset
        else:
            # Regular users can only see their own petitions and assigned ones
            return Petition.objects.filter(
                Q(created_by=user) |
                Q(assignments__assigned_to=user, assignments__is_active=True)
            ).distinct()


# DuaAraz API Views
class DuaArazListCreateAPIView(ArazAccessMixin, generics.ListCreateAPIView):
    """List and create DuaAraz requests"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'urgency_level', 'request_type', 'priority', 'assigned_doctor']
    search_fields = ['patient_name', 'patient_its_id', 'ailment', 'symptoms']
    ordering_fields = ['created_at', 'updated_at', 'urgency_level', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method == 'POST':
            return DuaArazCreateSerializer
        return DuaArazSerializer


class DuaArazDetailAPIView(ArazAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete specific DuaAraz requests"""
    serializer_class = DuaArazSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Get araz ID from URL kwargs to avoid recursion
            try:
                araz_id = self.kwargs.get('pk')
                if araz_id:
                    user = self.request.user
                    # Check if user has permission without calling get_object()
                    if user.is_admin or user.is_superuser:
                        return [permissions.IsAuthenticated()]
                    
                    # Get araz without triggering permission check
                    try:
                        araz = DuaAraz.objects.get(pk=araz_id)
                        if (araz.patient_user == user or 
                            (araz.assigned_doctor and araz.assigned_doctor.user == user)):
                            return [permissions.IsAuthenticated()]
                    except DuaAraz.DoesNotExist:
                        pass
                
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
            except (ValueError, TypeError):
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        
        return super().get_permissions()
    
    def perform_update(self, serializer):
        """Handle status changes and create history records"""
        old_instance = self.get_object()
        old_status = old_instance.status
        
        instance = serializer.save()
        
        # Create status history if status changed
        if old_status != instance.status:
            ArazStatusHistory.objects.create(
                araz=instance,
                old_status=old_status,
                new_status=instance.status,
                changed_by=self.request.user,
                change_reason=f"Status changed via API by {self.request.user.get_full_name()}"
            )
            
            # Create notification for patient if status changed
            if instance.patient_user and instance.patient_user != self.request.user:
                ArazNotification.objects.create(
                    araz=instance,
                    recipient=instance.patient_user,
                    message=f"Your Araz request status has been updated to {instance.get_status_display()}",
                    notification_type='status_update'
                )


class DuaArazSearchAPIView(APIView):
    """Advanced search for DuaAraz requests"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ArazSearchSerializer(data=request.data)
        if serializer.is_valid():
            # Get base queryset with permissions
            user = request.user
            if user.is_admin or user.is_superuser:
                queryset = DuaAraz.objects.all()
            elif user.role in ['aamil', 'moze_coordinator', 'doctor']:
                queryset = DuaAraz.objects.filter(
                    Q(patient_user=user) |
                    Q(assigned_doctor__user=user) |
                    Q(preferred_doctor__user=user)
                ).distinct()
            else:
                queryset = DuaAraz.objects.filter(patient_user=user)
            
            # Apply search filters
            filters = Q()
            
            query = serializer.validated_data.get('query')
            if query:
                filters &= (
                    Q(patient_name__icontains=query) |
                    Q(patient_its_id__icontains=query) |
                    Q(ailment__icontains=query) |
                    Q(symptoms__icontains=query)
                )
            
            for field in ['status', 'urgency_level', 'request_type', 'priority', 'assigned_doctor']:
                value = serializer.validated_data.get(field)
                if value:
                    filters &= Q(**{field: value})
            
            date_from = serializer.validated_data.get('date_from')
            date_to = serializer.validated_data.get('date_to')
            if date_from:
                filters &= Q(created_at__gte=date_from)
            if date_to:
                filters &= Q(created_at__lte=date_to)
            
            is_overdue = serializer.validated_data.get('is_overdue')
            if is_overdue is not None:
                # Calculate overdue based on urgency level
                now = timezone.now()
                overdue_conditions = Q()
                
                # Emergency: > 1 day
                overdue_conditions |= Q(
                    urgency_level='emergency',
                    created_at__lt=now - timedelta(days=1),
                    status__in=['submitted', 'under_review', 'approved', 'scheduled', 'in_progress']
                )
                
                # High: > 3 days
                overdue_conditions |= Q(
                    urgency_level='high',
                    created_at__lt=now - timedelta(days=3),
                    status__in=['submitted', 'under_review', 'approved', 'scheduled', 'in_progress']
                )
                
                # Medium: > 7 days
                overdue_conditions |= Q(
                    urgency_level='medium',
                    created_at__lt=now - timedelta(days=7),
                    status__in=['submitted', 'under_review', 'approved', 'scheduled', 'in_progress']
                )
                
                # Low: > 14 days
                overdue_conditions |= Q(
                    urgency_level='low',
                    created_at__lt=now - timedelta(days=14),
                    status__in=['submitted', 'under_review', 'approved', 'scheduled', 'in_progress']
                )
                
                if is_overdue:
                    filters &= overdue_conditions
                else:
                    filters &= ~overdue_conditions
            
            # Apply filters and get results
            araz_list = queryset.filter(filters).order_by('-created_at')[:50]  # Limit results
            serializer = DuaArazSerializer(araz_list, many=True, context={'request': request})
            
            return Response({
                'count': araz_list.count(),
                'results': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Petition API Views
class PetitionListCreateAPIView(PetitionAccessMixin, generics.ListCreateAPIView):
    """List and create petitions"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'moze']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.request.method == 'POST':
            return PetitionCreateSerializer
        return PetitionSerializer


class PetitionDetailAPIView(PetitionAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete specific petitions"""
    serializer_class = PetitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Get petition ID from URL kwargs to avoid recursion
            try:
                petition_id = self.kwargs.get('pk')
                if petition_id:
                    user = self.request.user
                    # Check if user has permission without calling get_object()
                    if user.is_admin or user.is_superuser:
                        return [permissions.IsAuthenticated()]
                    
                    # Get petition without triggering permission check
                    try:
                        petition = Petition.objects.get(pk=petition_id)
                        if (petition.created_by == user or 
                            petition.assignments.filter(assigned_to=user, is_active=True).exists()):
                            return [permissions.IsAuthenticated()]
                    except Petition.DoesNotExist:
                        pass
                
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
            except (ValueError, TypeError):
                return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        
        return super().get_permissions()
    
    def perform_update(self, serializer):
        """Handle status changes and create update records"""
        old_instance = self.get_object()
        old_status = old_instance.status
        
        instance = serializer.save()
        
        # Create update record if status changed
        if old_status != instance.status:
            PetitionUpdate.objects.create(
                petition=instance,
                status=instance.status,
                description=f"Status changed from {old_status} to {instance.status}",
                created_by=self.request.user
            )
            
            # Set resolved_at timestamp if status is resolved
            if instance.status == 'resolved' and not instance.resolved_at:
                instance.resolved_at = timezone.now()
                instance.save(update_fields=['resolved_at'])


class PetitionSearchAPIView(APIView):
    """Advanced search for petitions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PetitionSearchSerializer(data=request.data)
        if serializer.is_valid():
            # Get base queryset with permissions
            user = request.user
            if user.is_admin or user.is_superuser:
                queryset = Petition.objects.all()
            elif user.role in ['aamil', 'moze_coordinator']:
                managed_mozes = []
                if hasattr(user, 'managed_mozes'):
                    managed_mozes.extend(user.managed_mozes.all())
                if hasattr(user, 'coordinated_mozes'):
                    managed_mozes.extend(user.coordinated_mozes.all())
                
                queryset = Petition.objects.filter(
                    Q(created_by=user) |
                    Q(moze__in=managed_mozes) |
                    Q(assignments__assigned_to=user, assignments__is_active=True)
                ).distinct()
            else:
                queryset = Petition.objects.filter(
                    Q(created_by=user) |
                    Q(assignments__assigned_to=user, assignments__is_active=True)
                ).distinct()
            
            # Apply search filters
            filters = Q()
            
            query = serializer.validated_data.get('query')
            if query:
                filters &= (
                    Q(title__icontains=query) |
                    Q(description__icontains=query)
                )
            
            for field in ['status', 'priority', 'category', 'created_by', 'moze']:
                value = serializer.validated_data.get(field)
                if value:
                    filters &= Q(**{field: value})
            
            assigned_to = serializer.validated_data.get('assigned_to')
            if assigned_to:
                filters &= Q(assignments__assigned_to=assigned_to, assignments__is_active=True)
            
            date_from = serializer.validated_data.get('date_from')
            date_to = serializer.validated_data.get('date_to')
            if date_from:
                filters &= Q(created_at__gte=date_from)
            if date_to:
                filters &= Q(created_at__lte=date_to)
            
            is_overdue = serializer.validated_data.get('is_overdue')
            if is_overdue is not None:
                now = timezone.now()
                overdue_conditions = Q()
                
                # High priority: > 3 days
                overdue_conditions |= Q(
                    priority='high',
                    created_at__lt=now - timedelta(days=3),
                    status__in=['pending', 'in_progress']
                )
                
                # Medium priority: > 7 days
                overdue_conditions |= Q(
                    priority='medium',
                    created_at__lt=now - timedelta(days=7),
                    status__in=['pending', 'in_progress']
                )
                
                # Low priority: > 14 days
                overdue_conditions |= Q(
                    priority='low',
                    created_at__lt=now - timedelta(days=14),
                    status__in=['pending', 'in_progress']
                )
                
                if is_overdue:
                    filters &= overdue_conditions
                else:
                    filters &= ~overdue_conditions
            
            # Apply filters and get results
            petitions = queryset.filter(filters).order_by('-created_at')[:50]  # Limit results
            serializer = PetitionSerializer(petitions, many=True, context={'request': request})
            
            return Response({
                'count': petitions.count(),
                'results': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Category API Views
class PetitionCategoryListCreateAPIView(generics.ListCreateAPIView):
    """List and create petition categories"""
    queryset = PetitionCategory.objects.filter(is_active=True)
    serializer_class = PetitionCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_permissions(self):
        """Only admins can create categories"""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class PetitionCategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete petition categories"""
    queryset = PetitionCategory.objects.all()
    serializer_class = PetitionCategorySerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


# Comment API Views
class ArazCommentListCreateAPIView(generics.ListCreateAPIView):
    """List and create Araz comments"""
    serializer_class = ArazCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter comments based on Araz access permissions"""
        araz_id = self.kwargs.get('araz_id')
        araz = get_object_or_404(DuaAraz, id=araz_id)
        
        # Check if user can access this Araz
        user = self.request.user
        if (user.is_admin or user.is_superuser or 
            araz.patient_user == user or 
            (araz.assigned_doctor and araz.assigned_doctor.user == user)):
            
            # Show internal comments only to authorized users
            if user.role in ['admin', 'doctor'] or user.is_admin or user.is_superuser:
                return araz.comments.all()
            else:
                return araz.comments.filter(is_internal=False)
        else:
            return ArazComment.objects.none()
    
    def perform_create(self, serializer):
        """Create comment with proper associations"""
        araz_id = self.kwargs.get('araz_id')
        araz = get_object_or_404(DuaAraz, id=araz_id)
        serializer.save(author=self.request.user, araz=araz)


class PetitionCommentListCreateAPIView(generics.ListCreateAPIView):
    """List and create petition comments"""
    serializer_class = PetitionCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter comments based on petition access permissions"""
        petition_id = self.kwargs.get('petition_id')
        petition = get_object_or_404(Petition, id=petition_id)
        
        # Check if user can access this petition
        user = self.request.user
        if (user.is_admin or user.is_superuser or 
            petition.created_by == user or 
            petition.assignments.filter(assigned_to=user, is_active=True).exists()):
            
            # Show internal comments only to authorized users
            if user.role in ['admin', 'aamil', 'moze_coordinator'] or user.is_admin or user.is_superuser:
                return petition.comments.all()
            else:
                return petition.comments.filter(is_internal=False)
        else:
            return PetitionComment.objects.none()
    
    def perform_create(self, serializer):
        """Create comment with proper associations"""
        petition_id = self.kwargs.get('petition_id')
        petition = get_object_or_404(Petition, id=petition_id)
        serializer.save(user=self.request.user, petition=petition)


# Assignment API Views
class PetitionAssignmentCreateAPIView(generics.CreateAPIView):
    """Assign petition to a user"""
    serializer_class = PetitionAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Only admins, aamils, and coordinators can assign petitions"""
        user = self.request.user
        if user.is_admin or user.is_superuser or user.role in ['aamil', 'moze_coordinator']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
    
    def perform_create(self, serializer):
        """Create assignment with proper associations"""
        petition_id = self.kwargs.get('petition_id')
        petition = get_object_or_404(Petition, id=petition_id)
        
        # Deactivate existing assignments
        petition.assignments.update(is_active=False)
        
        # Create new assignment
        assigned_to_id = self.request.data.get('assigned_to_id')
        assigned_to = get_object_or_404(User, id=assigned_to_id)
        
        serializer.save(
            petition=petition,
            assigned_to=assigned_to,
            assigned_by=self.request.user
        )


# Statistics API Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def araz_stats_api(request):
    """Get Araz statistics"""
    user = request.user
    
    # Get base queryset based on permissions
    if user.is_admin or user.is_superuser:
        queryset = DuaAraz.objects.all()
    elif user.role in ['aamil', 'moze_coordinator', 'doctor']:
        queryset = DuaAraz.objects.filter(
            Q(patient_user=user) |
            Q(assigned_doctor__user=user) |
            Q(preferred_doctor__user=user)
        ).distinct()
    else:
        queryset = DuaAraz.objects.filter(patient_user=user)
    
    # Calculate statistics
    total_araz = queryset.count()
    pending_araz = queryset.filter(status='submitted').count()
    in_progress_araz = queryset.filter(status__in=['under_review', 'approved', 'scheduled', 'in_progress']).count()
    completed_araz = queryset.filter(status='completed').count()
    emergency_araz = queryset.filter(urgency_level='emergency').count()
    
    # Calculate overdue
    now = timezone.now()
    overdue_araz = queryset.filter(
        Q(urgency_level='emergency', created_at__lt=now - timedelta(days=1)) |
        Q(urgency_level='high', created_at__lt=now - timedelta(days=3)) |
        Q(urgency_level='medium', created_at__lt=now - timedelta(days=7)) |
        Q(urgency_level='low', created_at__lt=now - timedelta(days=14)),
        status__in=['submitted', 'under_review', 'approved', 'scheduled', 'in_progress']
    ).count()
    
    recent_araz = queryset.filter(created_at__gte=now - timedelta(days=7)).count()
    
    # Group by request type
    araz_by_type = dict(queryset.values_list('request_type').annotate(count=Count('id')))
    
    # Group by urgency level
    araz_by_urgency = dict(queryset.values_list('urgency_level').annotate(count=Count('id')))
    
    # Group by status
    araz_by_status = dict(queryset.values_list('status').annotate(count=Count('id')))
    
    stats = {
        'total_araz': total_araz,
        'pending_araz': pending_araz,
        'in_progress_araz': in_progress_araz,
        'completed_araz': completed_araz,
        'emergency_araz': emergency_araz,
        'overdue_araz': overdue_araz,
        'recent_araz': recent_araz,
        'araz_by_type': araz_by_type,
        'araz_by_urgency': araz_by_urgency,
        'araz_by_status': araz_by_status,
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def petition_stats_api(request):
    """Get petition statistics"""
    user = request.user
    
    # Get base queryset based on permissions
    if user.is_admin or user.is_superuser:
        queryset = Petition.objects.all()
    elif user.role in ['aamil', 'moze_coordinator']:
        managed_mozes = []
        if hasattr(user, 'managed_mozes'):
            managed_mozes.extend(user.managed_mozes.all())
        if hasattr(user, 'coordinated_mozes'):
            managed_mozes.extend(user.coordinated_mozes.all())
        
        queryset = Petition.objects.filter(
            Q(created_by=user) |
            Q(moze__in=managed_mozes) |
            Q(assignments__assigned_to=user, assignments__is_active=True)
        ).distinct()
    else:
        queryset = Petition.objects.filter(
            Q(created_by=user) |
            Q(assignments__assigned_to=user, assignments__is_active=True)
        ).distinct()
    
    # Calculate statistics
    total_petitions = queryset.count()
    pending_petitions = queryset.filter(status='pending').count()
    in_progress_petitions = queryset.filter(status='in_progress').count()
    resolved_petitions = queryset.filter(status='resolved').count()
    rejected_petitions = queryset.filter(status='rejected').count()
    
    # Calculate overdue
    now = timezone.now()
    overdue_petitions = queryset.filter(
        Q(priority='high', created_at__lt=now - timedelta(days=3)) |
        Q(priority='medium', created_at__lt=now - timedelta(days=7)) |
        Q(priority='low', created_at__lt=now - timedelta(days=14)),
        status__in=['pending', 'in_progress']
    ).count()
    
    recent_petitions = queryset.filter(created_at__gte=now - timedelta(days=7)).count()
    
    # Group by category
    petitions_by_category = dict(
        queryset.filter(category__isnull=False)
        .values_list('category__name')
        .annotate(count=Count('id'))
    )
    
    # Group by priority
    petitions_by_priority = dict(queryset.values_list('priority').annotate(count=Count('id')))
    
    # Group by status
    petitions_by_status = dict(queryset.values_list('status').annotate(count=Count('id')))
    
    stats = {
        'total_petitions': total_petitions,
        'pending_petitions': pending_petitions,
        'in_progress_petitions': in_progress_petitions,
        'resolved_petitions': resolved_petitions,
        'rejected_petitions': rejected_petitions,
        'overdue_petitions': overdue_petitions,
        'recent_petitions': recent_petitions,
        'petitions_by_category': petitions_by_category,
        'petitions_by_priority': petitions_by_priority,
        'petitions_by_status': petitions_by_status,
    }
    
    return Response(stats)


# Notification API Views
class ArazNotificationListAPIView(generics.ListAPIView):
    """List Araz notifications for the current user"""
    serializer_class = ArazNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter notifications for the current user"""
        return ArazNotification.objects.filter(recipient=self.request.user)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read_api(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(
        ArazNotification, 
        id=notification_id, 
        recipient=request.user
    )
    
    notification.is_read = True
    notification.save()
    
    return Response({'message': 'Notification marked as read'})


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read_api(request):
    """Mark all notifications as read for the current user"""
    ArazNotification.objects.filter(
        recipient=request.user, 
        is_read=False
    ).update(is_read=True)
    
    return Response({'message': 'All notifications marked as read'})


# Dashboard API View
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def araz_dashboard_api(request):
    """Get comprehensive Araz dashboard data"""
    user = request.user
    
    # Get Araz stats using ArazAccessMixin logic
    if user.is_admin or user.is_superuser:
        araz_queryset = DuaAraz.objects.all()
    elif user.role in ['aamil', 'moze_coordinator']:
        araz_queryset = DuaAraz.objects.filter(
            Q(patient_user=user) | Q(assigned_doctor__user=user)
        ).distinct()
    elif user.role == 'doctor':
        araz_queryset = DuaAraz.objects.filter(
            Q(assigned_doctor__user=user) | Q(preferred_doctor__user=user) | Q(patient_user=user)
        ).distinct()
    else:
        araz_queryset = DuaAraz.objects.filter(patient_user=user)
    
    # Calculate Araz stats
    total_araz = araz_queryset.count()
    pending_araz = araz_queryset.filter(status='pending').count()
    in_progress_araz = araz_queryset.filter(status='in_progress').count()
    completed_araz = araz_queryset.filter(status='completed').count()
    emergency_araz = araz_queryset.filter(urgency_level='emergency').count()
    
    araz_stats = {
        'total': total_araz,
        'pending': pending_araz,
        'in_progress': in_progress_araz,
        'completed': completed_araz,
        'emergency': emergency_araz,
    }
    
    # Get Petition stats using PetitionAccessMixin logic
    if user.is_admin or user.is_superuser:
        petition_queryset = Petition.objects.all()
    elif user.role in ['aamil', 'moze_coordinator']:
        petition_queryset = Petition.objects.filter(
            Q(created_by=user) | Q(assignments__assigned_to=user, assignments__is_active=True)
        ).distinct()
    else:
        petition_queryset = Petition.objects.filter(created_by=user)
    
    # Calculate Petition stats
    total_petitions = petition_queryset.count()
    pending_petitions = petition_queryset.filter(status='pending').count()
    in_progress_petitions = petition_queryset.filter(status='in_progress').count()
    completed_petitions = petition_queryset.filter(status='completed').count()
    urgent_petitions = petition_queryset.filter(priority='urgent').count()
    
    petition_stats = {
        'total': total_petitions,
        'pending': pending_petitions,
        'in_progress': in_progress_petitions,
        'completed': completed_petitions,
        'urgent': urgent_petitions,
    }
    
    # Get recent items
    if user.is_admin or user.is_superuser:
        recent_araz = DuaAraz.objects.all()[:5]
        recent_petitions = Petition.objects.all()[:5]
    elif user.role in ['aamil', 'moze_coordinator']:
        recent_araz = DuaAraz.objects.filter(
            Q(patient_user=user) |
            Q(assigned_doctor__user=user)
        ).distinct()[:5]
        
        managed_mozes = []
        if hasattr(user, 'managed_mozes'):
            managed_mozes.extend(user.managed_mozes.all())
        if hasattr(user, 'coordinated_mozes'):
            managed_mozes.extend(user.coordinated_mozes.all())
        
        recent_petitions = Petition.objects.filter(
            Q(created_by=user) |
            Q(moze__in=managed_mozes) |
            Q(assignments__assigned_to=user, assignments__is_active=True)
        ).distinct()[:5]
    else:
        recent_araz = DuaAraz.objects.filter(patient_user=user)[:5]
        recent_petitions = Petition.objects.filter(
            Q(created_by=user) |
            Q(assignments__assigned_to=user, assignments__is_active=True)
        ).distinct()[:5]
    
    # Get unread notifications
    unread_notifications = ArazNotification.objects.filter(
        recipient=user, 
        is_read=False
    ).count()
    
    dashboard_data = {
        'araz_stats': araz_stats,
        'petition_stats': petition_stats,
        'recent_araz': DuaArazSerializer(recent_araz, many=True, context={'request': request}).data,
        'recent_petitions': PetitionSerializer(recent_petitions, many=True, context={'request': request}).data,
        'unread_notifications': unread_notifications,
        'user_permissions': {
            'can_manage_araz': user.is_admin or user.is_superuser or user.role in ['doctor', 'aamil', 'moze_coordinator'],
            'can_manage_petitions': user.is_admin or user.is_superuser or user.role in ['aamil', 'moze_coordinator'],
            'can_create_categories': user.is_admin or user.is_superuser,
        }
    }
    
    return Response(dashboard_data)