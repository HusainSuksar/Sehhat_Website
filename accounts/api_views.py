"""
API Views for the accounts app
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import User, UserProfile, AuditLog
from .serializers import (
    UserSerializer, UserProfileSerializer, LoginSerializer,
    ITSSyncSerializer, PasswordChangeSerializer, UserSearchSerializer,
    AuditLogSerializer
)
from .services import mock_its_service


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with ITS ID support
    """
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class LoginAPIView(APIView):
    """
    API view for user login (alternative to JWT)
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    API view for user logout
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileAPIView(APIView):
    """
    API view for current user profile (me endpoint)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        """Update current user profile"""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Partially update current user profile"""
        return self.put(request)


class UserListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'jamaat', 'city', 'country']
    search_fields = ['first_name', 'last_name', 'username', 'email', 'its_id']
    ordering_fields = ['date_joined', 'last_login', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method == 'POST':
            # Only admins can create users
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting specific users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Custom permissions for different actions"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Check if user is trying to edit their own profile or if they're admin
            try:
                user_id = self.kwargs.get('pk')
                if user_id and int(user_id) == self.request.user.id:
                    permission_classes = [permissions.IsAuthenticated]
                else:
                    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
            except (ValueError, TypeError):
                permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserSearchAPIView(APIView):
    """
    Advanced user search API
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserSearchSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data.get('query', '')
            role = serializer.validated_data.get('role')
            jamaat = serializer.validated_data.get('jamaat')
            city = serializer.validated_data.get('city')
            is_active = serializer.validated_data.get('is_active')
            
            # Build search query
            search_query = Q()
            
            if query:
                search_query &= (
                    Q(first_name__icontains=query) |
                    Q(last_name__icontains=query) |
                    Q(username__icontains=query) |
                    Q(email__icontains=query) |
                    Q(its_id__icontains=query) |
                    Q(arabic_full_name__icontains=query)
                )
            
            if role:
                search_query &= Q(role=role)
            
            if jamaat:
                search_query &= Q(jamaat__icontains=jamaat)
            
            if city:
                search_query &= Q(city__icontains=city)
            
            if is_active is not None:
                search_query &= Q(is_active=is_active)
            
            users = User.objects.filter(search_query)[:20]  # Limit to 20 results
            serializer = UserSerializer(users, many=True)
            
            return Response({
                'count': users.count(),
                'results': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ITSSyncAPIView(APIView):
    """
    API view for syncing user data from ITS API
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ITSSyncSerializer(data=request.data)
        if serializer.is_valid():
            its_id = serializer.validated_data['its_id']
            force_update = serializer.validated_data['force_update']
            
            try:
                # Check if user already exists
                user = User.objects.filter(its_id=its_id).first()
                
                # Fetch data from ITS API (mock)
                its_data = mock_its_service.fetch_user_data(its_id)
                
                if not its_data:
                    return Response(
                        {'error': 'User not found in ITS system'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                if user and not force_update:
                    return Response(
                        {'message': 'User already exists', 'user': UserSerializer(user).data},
                        status=status.HTTP_200_OK
                    )
                
                # Create or update user with ITS data
                if user:
                    # Update existing user
                    for field, value in its_data.items():
                        if hasattr(user, field) and field not in ['sync_timestamp', 'data_source']:
                            setattr(user, field, value)
                    
                    user.its_last_sync = timezone.now()
                    user.its_sync_status = 'synced'
                    user.save()
                    
                    message = 'User updated successfully'
                else:
                    # Create new user
                    username = its_data.get('email', '').split('@')[0] or f"user_{its_id}"
                    
                    user = User.objects.create_user(
                        username=username,
                        email=its_data.get('email', ''),
                        first_name=its_data.get('first_name', ''),
                        last_name=its_data.get('last_name', ''),
                        its_id=its_id,
                        arabic_full_name=its_data.get('arabic_full_name', ''),
                        prefix=its_data.get('prefix', ''),
                        age=its_data.get('age'),
                        gender=its_data.get('gender', ''),
                        marital_status=its_data.get('marital_status', ''),
                        misaq=its_data.get('misaq', ''),
                        occupation=its_data.get('occupation', ''),
                        qualification=its_data.get('qualification', ''),
                        idara=its_data.get('idara', ''),
                        category=its_data.get('category', ''),
                        organization=its_data.get('organization', ''),
                        mobile_number=its_data.get('mobile_number', ''),
                        whatsapp_number=its_data.get('whatsapp_number', ''),
                        address=its_data.get('address', ''),
                        jamaat=its_data.get('jamaat', ''),
                        jamiaat=its_data.get('jamiaat', ''),
                        nationality=its_data.get('nationality', ''),
                        vatan=its_data.get('vatan', ''),
                        city=its_data.get('city', ''),
                        country=its_data.get('country', ''),
                        hifz_sanad=its_data.get('hifz_sanad', ''),
                        its_last_sync=timezone.now(),
                        its_sync_status='synced'
                    )
                    
                    message = 'User created successfully'
                
                return Response({
                    'message': message,
                    'user': UserSerializer(user).data
                }, status=status.HTTP_201_CREATED if message == 'User created successfully' else status.HTTP_200_OK)
                
            except Exception as e:
                return Response(
                    {'error': f'Sync failed: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    """
    API view for changing password
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuditLogListAPIView(generics.ListAPIView):
    """
    API view for listing audit logs
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_api(request):
    """
    API endpoint for user statistics
    """
    from django.db.models import Count
    
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'users_by_role': User.objects.values('role').annotate(count=Count('role')),
        'recent_registrations': User.objects.filter(
            date_joined__gte=timezone.now().replace(day=1)
        ).count(),
        'its_synced_users': User.objects.filter(its_sync_status='synced').count(),
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_its_sync_api(request):
    """
    API endpoint for bulk ITS synchronization
    """
    its_ids = request.data.get('its_ids', [])
    
    if not its_ids or not isinstance(its_ids, list):
        return Response(
            {'error': 'its_ids must be a list of ITS IDs'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    results = []
    for its_id in its_ids:
        try:
            # Simulate sync for each ITS ID
            its_data = mock_its_service.fetch_user_data(its_id)
            if its_data:
                results.append({
                    'its_id': its_id,
                    'status': 'success',
                    'data': its_data
                })
            else:
                results.append({
                    'its_id': its_id,
                    'status': 'not_found',
                    'error': 'User not found in ITS system'
                })
        except Exception as e:
            results.append({
                'its_id': its_id,
                'status': 'error',
                'error': str(e)
            })
    
    return Response({
        'message': f'Processed {len(its_ids)} ITS IDs',
        'results': results
    })