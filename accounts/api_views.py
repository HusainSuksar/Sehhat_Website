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
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from .services import MockITSService, ITSService
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

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
            # Specify the backend since we have multiple authentication backends
            user.backend = 'django.contrib.auth.backends.ModelBackend'
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
            its_id = serializer.validated_data.get('its_id') or request.user.its_id
            force_update = serializer.validated_data['force_update']
            
            # If no ITS ID provided and user doesn't have one, return error
            if not its_id:
                return Response(
                    {'error': 'No ITS ID available for synchronization'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
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


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])  # Allow public access for testing
def test_its_api(request):
    """
    Test endpoint for the Mock ITS API
    Handles different actions: fetch_user, search_users, validate_id, create_user
    """
    
    # Handle GET request for API status
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'message': 'Mock ITS API is working',
            'available_actions': ['fetch_user', 'search_users', 'validate_id', 'create_user'],
            'status': 'active'
        })
    
    # Handle POST request for actions
    try:
        data = json.loads(request.body)
        action = data.get('action')
        
        if action == 'fetch_user':
            its_id = data.get('its_id')
            if not its_id:
                return JsonResponse({'success': False, 'error': 'ITS ID is required'})
            
            user_data = MockITSService.fetch_user_data(its_id)
            if user_data:
                return JsonResponse({'success': True, 'data': user_data})
            else:
                return JsonResponse({'success': False, 'error': 'User not found or invalid ITS ID'})
        
        elif action == 'search_users':
            query = data.get('query')
            if not query:
                return JsonResponse({'success': False, 'error': 'Search query is required'})
            
            results = MockITSService.search_users(query, limit=5)
            return JsonResponse({'success': True, 'data': results})
        
        elif action == 'validate_id':
            its_id = data.get('its_id')
            if not its_id:
                return JsonResponse({'success': False, 'error': 'ITS ID is required'})
            
            is_valid = MockITSService.validate_its_id(its_id)
            message = None
            if not is_valid:
                if len(its_id) != 8:
                    message = f"Must be exactly 8 digits (got {len(its_id)})"
                elif not its_id.isdigit():
                    message = "Must contain only digits"
            
            return JsonResponse({
                'success': True,
                'valid': is_valid,
                'its_id': its_id,
                'message': message
            })
        
        elif action == 'create_user':
            its_id = data.get('its_id')
            if not its_id:
                return JsonResponse({'success': False, 'error': 'ITS ID is required'})
            
            # Fetch ITS data
            its_data = MockITSService.fetch_user_data(its_id)
            if not its_data:
                return JsonResponse({'success': False, 'error': 'Invalid ITS ID or user not found'})
            
            # Create or get Django user
            user, created = User.objects.get_or_create(
                its_id=its_id,
                defaults={
                    'username': its_data['email'],
                    'email': its_data['email'],
                    'first_name': its_data['first_name'],
                    'last_name': its_data['last_name'],
                    'mobile_number': its_data['mobile_number'],
                    'qualification': its_data['qualification'],
                    'city': its_data['city'],
                    'organization': its_data['organization'],
                    'role': 'student',
                }
            )
            
            user_data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'city': user.city,
                'mobile_number': user.mobile_number,
            }
            
            return JsonResponse({
                'success': True,
                'created': created,
                'user': user_data
            })
        
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def its_login_api(request):
    """
    ITS Login API endpoint
    Authenticates user through ITS API and creates Django session
    """
    try:
        data = json.loads(request.body)
        its_id = data.get('its_id')
        password = data.get('password')
        
        if not its_id or not password:
            return JsonResponse({
                'success': False,
                'error': 'Both ITS ID and password are required'
            })
        
        # Authenticate with ITS API
        auth_result = MockITSService.authenticate_user(its_id, password)
        
        if not auth_result or not auth_result.get('authenticated'):
            return JsonResponse({
                'success': False,
                'error': 'Invalid ITS credentials. Please check your ITS ID and password.'
            })
        
        # Get user data from ITS
        user_data = auth_result['user_data']
        role = auth_result['role']
        
        # Create or update Django user
        user, created = User.objects.get_or_create(
            its_id=its_id,
            defaults={
                'username': user_data['email'],
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'arabic_full_name': user_data['arabic_full_name'],
                'prefix': user_data['prefix'],
                'age': user_data['age'],
                'gender': user_data['gender'],
                'marital_status': user_data['marital_status'],
                'misaq': user_data['misaq'],
                'occupation': user_data['occupation'],
                'qualification': user_data['qualification'],
                'idara': user_data['idara'],
                'category': user_data['category'],
                'organization': user_data['organization'],
                'mobile_number': user_data['mobile_number'],
                'whatsapp_number': user_data['whatsapp_number'],
                'address': user_data['address'],
                'jamaat': user_data['jamaat'],
                'jamiaat': user_data['jamiaat'],
                'nationality': user_data['nationality'],
                'vatan': user_data['vatan'],
                'city': user_data['city'],
                'country': user_data['country'],
                'hifz_sanad': user_data['hifz_sanad'],
                'profile_photo': user_data['photograph'],
                'role': role,
                'is_active': True,
            }
        )
        
        # Update existing user data with fresh ITS data (sync ALL fields)
        if not created:
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.email = user_data['email']
            user.arabic_full_name = user_data['arabic_full_name']
            user.prefix = user_data['prefix']
            user.age = user_data['age']
            user.gender = user_data['gender']
            user.marital_status = user_data['marital_status']
            user.misaq = user_data['misaq']
            user.occupation = user_data['occupation']
            user.qualification = user_data['qualification']
            user.idara = user_data['idara']
            user.category = user_data['category']
            user.organization = user_data['organization']
            user.mobile_number = user_data['mobile_number']
            user.whatsapp_number = user_data['whatsapp_number']
            user.address = user_data['address']
            user.jamaat = user_data['jamaat']
            user.jamiaat = user_data['jamiaat']
            user.nationality = user_data['nationality']
            user.vatan = user_data['vatan']
            user.city = user_data['city']
            user.country = user_data['country']
            user.hifz_sanad = user_data['hifz_sanad']
            user.profile_photo = user_data['photograph']
            user.role = role  # Update role based on current ITS data
            user.its_last_sync = timezone.now()
            user.save()
        
        # Log the user in (create Django session)
        # Specify the backend since we have multiple authentication backends
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        
        # Determine redirect URL based on user role
        redirect_url = _get_redirect_url_for_role(role)
        
        # Get role display name
        role_display = dict(User.ROLE_CHOICES).get(role, role.title())
        
        return JsonResponse({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': role,
                'role_display': role_display,
                'its_id': its_id,
                'created': created
            },
            'redirect_url': redirect_url,
            'auth_source': 'its_api'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Login failed: {str(e)}'
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_its_data(request):
    """
    Sync user data with ITS API
    Allows users to manually sync their profile data from ITS
    """
    try:
        user = request.user
        
        # Check if user has ITS ID
        if not user.its_id:
            return JsonResponse({
                'success': False,
                'error': 'No ITS ID associated with your account'
            })
        
        # Fetch fresh data from ITS
        its_data = MockITSService.fetch_user_data(user.its_id)
        
        if not its_data:
            return JsonResponse({
                'success': False,
                'error': 'Failed to fetch data from ITS API'
            })
        
        # Update user fields with fresh ITS data
        updated_fields = []
        
        if user.first_name != its_data['first_name']:
            user.first_name = its_data['first_name']
            updated_fields.append('first_name')
            
        if user.last_name != its_data['last_name']:
            user.last_name = its_data['last_name']
            updated_fields.append('last_name')
            
        if user.email != its_data['email']:
            user.email = its_data['email']
            updated_fields.append('email')
            
        if user.mobile_number != its_data['mobile_number']:
            user.mobile_number = its_data['mobile_number']
            updated_fields.append('mobile_number')
            
        if user.qualification != its_data['qualification']:
            user.qualification = its_data['qualification']
            updated_fields.append('qualification')
            
        if user.occupation != its_data['occupation']:
            user.occupation = its_data['occupation']
            updated_fields.append('occupation')
            
        if user.organization != its_data['organization']:
            user.organization = its_data['organization']
            updated_fields.append('organization')
            
        if user.city != its_data['city']:
            user.city = its_data['city']
            updated_fields.append('city')
            
        if user.country != its_data['country']:
            user.country = its_data['country']
            updated_fields.append('country')
        
        # Update sync metadata
        user.its_last_sync = timezone.now()
        user.its_sync_status = 'success'
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Profile synchronized successfully',
            'updated_fields': updated_fields,
            'sync_timestamp': user.its_last_sync.isoformat(),
            'total_updates': len(updated_fields)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Sync failed: {str(e)}'
        })


def _get_redirect_url_for_role(role):
    """
    Determine redirect URL based on user role
    """
    role_redirects = {
        'doctor': '/doctordirectory/',  # Fixed: removed 'dashboard/' since it's mapped to root
        'badri_mahal_admin': '/accounts/user-management/',
        'aamil': '/moze/',  # Fixed: removed 'dashboard/' 
        'moze_coordinator': '/moze/',  # Fixed: removed 'dashboard/'
        'student': '/students/',  # Fixed: removed 'dashboard/'
    }
    
    # Default redirect for any other roles
    return role_redirects.get(role, '/accounts/profile/')


@csrf_exempt
@require_http_methods(["POST"])
def lookup_its_id(request):
    """
    API endpoint to lookup patient information by ITS ID
    """
    try:
        data = json.loads(request.body)
        its_id = data.get('its_id', '').strip()
        
        if not its_id:
            return JsonResponse({
                'success': False,
                'message': 'ITS ID is required'
            })
        
        # Validate ITS ID format
        if len(its_id) != 8 or not its_id.isdigit():
            return JsonResponse({
                'success': False,
                'message': 'ITS ID must be exactly 8 digits'
            })
        
        # First, check if user already exists in database
        existing_user = User.objects.filter(its_id=its_id).first()
        
        if existing_user:
            # Get patient profile if exists
            patient_profile = existing_user.patient_profile.first()
            
            user_data = {
                'its_id': existing_user.its_id,
                'first_name': existing_user.first_name,
                'last_name': existing_user.last_name,
                'username': existing_user.username,
                'email': existing_user.email,
                'phone_number': existing_user.phone_number,
                'gender': existing_user.gender,
                'age': existing_user.age,
                'patient_id': patient_profile.id if patient_profile else None,
                'is_existing_user': True
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Patient found in system',
                'user_data': user_data
            })
        
        # If not found locally, fetch from ITS API
        its_data = ITSService.fetch_user_data(its_id)
        
        if its_data:
            user_data = {
                'its_id': its_id,
                'first_name': its_data.get('first_name', ''),
                'last_name': its_data.get('last_name', ''),
                'username': its_id,  # Use ITS ID as username for new users
                'email': its_data.get('email', ''),
                'phone_number': its_data.get('mobile_number', ''),
                'gender': its_data.get('gender', ''),
                'age': its_data.get('age', ''),
                'patient_id': None,  # Will be created when appointment is submitted
                'is_existing_user': False
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Patient information retrieved from ITS',
                'user_data': user_data
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'No patient found with ITS ID: {its_id}'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        })


@login_required
def doctor_services_api(request, doctor_id):
    """API endpoint to get services for a specific doctor"""
    try:
        from doctordirectory.models import Doctor, Service
        
        # Get the doctor
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        
        # Get services for this doctor
        services = Service.objects.filter(doctor=doctor, is_active=True).values(
            'id', 'name', 'description', 'price', 'duration'
        )
        
        return JsonResponse({
            'success': True,
            'doctor': {
                'id': doctor.id,
                'name': doctor.name,
                'specialty': doctor.specialty
            },
            'services': list(services)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching doctor services: {str(e)}',
            'services': []
        })