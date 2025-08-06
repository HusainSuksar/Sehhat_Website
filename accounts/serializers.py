"""
Serializers for the accounts app API
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, AuditLog
from .services import mock_its_service


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with all ITS fields
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            # Basic Django User fields
            'id', 'username', 'email', 'first_name', 'last_name', 'is_active',
            'date_joined', 'last_login', 'full_name',
            
            # Role and basic fields
            'role',
            
            # All 21 ITS API fields
            'its_id', 'arabic_full_name', 'prefix', 'age', 'gender',
            'marital_status', 'misaq', 'occupation', 'qualification',
            'idara', 'category', 'organization', 'mobile_number',
            'whatsapp_number', 'address', 'jamaat', 'jamiaat',
            'nationality', 'vatan', 'city', 'country', 'hifz_sanad',
            'photograph',
            
            # Additional fields
            'phone_number', 'profile_photo', 'verified_certificate',
            'specialty', 'college', 'specialization',
            
            # ITS sync metadata
            'its_last_sync', 'its_sync_status',
            
            # Timestamps
            'created_at', 'updated_at',
            
            # Password fields (write-only)
            'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'created_at', 'updated_at', 'full_name']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }
    
    def get_full_name(self, obj):
        """Return the full name of the user"""
        return obj.get_full_name()
    
    def validate_its_id(self, value):
        """Validate ITS ID format"""
        if value and not mock_its_service.validate_its_id(value):
            raise serializers.ValidationError("ITS ID must be exactly 8 digits")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if 'password' in attrs:
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            
            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match")
            
            # Validate password strength
            try:
                validate_password(password)
            except ValidationError as e:
                raise serializers.ValidationError({"password": e.messages})
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user"""
        # Remove password confirmation from validated data
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """Update user instance"""
        # Remove password confirmation from validated data
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    its_id = serializers.CharField(required=False, help_text="Alternative login with ITS ID")
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        its_id = attrs.get('its_id')
        
        if its_id:
            # Try to find user by ITS ID
            try:
                user = User.objects.get(its_id=its_id)
                username = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid ITS ID")
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    attrs['user'] = user
                else:
                    raise serializers.ValidationError("User account is disabled")
            else:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include username/ITS ID and password")
        
        return attrs


class ITSSyncSerializer(serializers.Serializer):
    """
    Serializer for ITS data synchronization
    """
    its_id = serializers.CharField(max_length=8, min_length=8)
    force_update = serializers.BooleanField(default=False)
    
    def validate_its_id(self, value):
        """Validate ITS ID format"""
        if not mock_its_service.validate_its_id(value):
            raise serializers.ValidationError("ITS ID must be exactly 8 digits")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, attrs):
        """Validate new password"""
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError("New passwords do not match")
        
        # Validate password strength
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return attrs


class UserSearchSerializer(serializers.Serializer):
    """
    Serializer for user search parameters
    """
    query = serializers.CharField(max_length=200)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    jamaat = serializers.CharField(max_length=100, required=False)
    city = serializers.CharField(max_length=100, required=False)
    is_active = serializers.BooleanField(required=False)


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']