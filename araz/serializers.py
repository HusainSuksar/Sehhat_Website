"""
Serializers for the Araz app API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    DuaAraz, Petition, PetitionCategory, PetitionComment, ArazComment,
    PetitionAttachment, ArazAttachment, ArazStatusHistory, PetitionAssignment,
    PetitionUpdate, PetitionStatus, ArazNotification
)
from accounts.serializers import UserSerializer
from doctordirectory.models import Doctor

User = get_user_model()


class DoctorBasicSerializer(serializers.ModelSerializer):
    """Basic doctor information for Araz serializers"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = ['id', 'user', 'full_name', 'specialty', 'license_number']
        
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else 'Unknown Doctor'


class ArazAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for Araz attachments"""
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ArazAttachment
        fields = [
            'id', 'file', 'file_url', 'original_filename', 
            'uploaded_by', 'uploaded_at', 'file_size'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at', 'file_size']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class ArazCommentSerializer(serializers.ModelSerializer):
    """Serializer for Araz comments"""
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = ArazComment
        fields = [
            'id', 'content', 'author', 'is_internal',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class ArazStatusHistorySerializer(serializers.ModelSerializer):
    """Serializer for Araz status history"""
    changed_by = UserSerializer(read_only=True)
    old_status_display = serializers.SerializerMethodField()
    new_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ArazStatusHistory
        fields = [
            'id', 'old_status', 'old_status_display', 'new_status', 
            'new_status_display', 'changed_by', 'change_reason', 'changed_at'
        ]
        read_only_fields = ['id', 'changed_by', 'changed_at']
    
    def get_old_status_display(self, obj):
        return dict(DuaAraz.STATUS_CHOICES).get(obj.old_status, obj.old_status)
    
    def get_new_status_display(self, obj):
        return dict(DuaAraz.STATUS_CHOICES).get(obj.new_status, obj.new_status)


class ArazNotificationSerializer(serializers.ModelSerializer):
    """Serializer for Araz notifications"""
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = ArazNotification
        fields = [
            'id', 'message', 'notification_type', 'recipient',
            'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'recipient', 'created_at']


class DuaArazSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for DuaAraz model"""
    patient_user = UserSerializer(read_only=True)
    preferred_doctor = DoctorBasicSerializer(read_only=True)
    assigned_doctor = DoctorBasicSerializer(read_only=True)
    comments = ArazCommentSerializer(many=True, read_only=True)
    attachments = ArazAttachmentSerializer(many=True, read_only=True)
    status_history = ArazStatusHistorySerializer(many=True, read_only=True)
    notifications = ArazNotificationSerializer(many=True, read_only=True)
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    urgency_level_display = serializers.CharField(source='get_urgency_level_display', read_only=True)
    request_type_display = serializers.CharField(source='get_request_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    preferred_contact_method_display = serializers.CharField(source='get_preferred_contact_method_display', read_only=True)
    
    # Computed fields
    days_since_created = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = DuaAraz
        fields = [
            # Basic info
            'id', 'patient_its_id', 'patient_name', 'patient_phone', 'patient_email',
            'patient_user',
            
            # Request details
            'ailment', 'symptoms', 'urgency_level', 'urgency_level_display',
            'request_type', 'request_type_display',
            
            # Medical history
            'previous_medical_history', 'current_medications', 'allergies',
            
            # Preferences
            'preferred_doctor', 'preferred_location', 'preferred_time',
            'preferred_contact_method', 'preferred_contact_method_display',
            
            # Status and processing
            'status', 'status_display', 'priority', 'priority_display',
            'assigned_doctor', 'assigned_date', 'scheduled_date',
            
            # Notes and feedback
            'admin_notes', 'patient_feedback',
            
            # Timestamps
            'created_at', 'updated_at',
            
            # Computed fields
            'days_since_created', 'is_overdue',
            
            # Related data
            'comments', 'attachments', 'status_history', 'notifications'
        ]
        read_only_fields = [
            'id', 'patient_user', 'assigned_date', 'created_at', 'updated_at',
            'days_since_created', 'is_overdue', 'comments', 'attachments',
            'status_history', 'notifications'
        ]
    
    def get_days_since_created(self, obj):
        """Calculate days since the Araz was created"""
        return (timezone.now() - obj.created_at).days
    
    def get_is_overdue(self, obj):
        """Check if the Araz is overdue based on urgency level"""
        days_since = self.get_days_since_created(obj)
        
        overdue_thresholds = {
            'emergency': 1,
            'high': 3,
            'medium': 7,
            'low': 14
        }
        
        threshold = overdue_thresholds.get(obj.urgency_level, 7)
        return days_since > threshold and obj.status not in ['completed', 'cancelled', 'rejected']
    
    def validate_patient_its_id(self, value):
        """Validate ITS ID format and existence in ITS API"""
        if value and value.strip():
            value = value.strip()
            
            # Check format first
            if len(value) != 8 or not value.isdigit():
                raise serializers.ValidationError("ITS ID must be exactly 8 digits")
            
            # Validate against ITS API
            from accounts.services import MockITSService
            user_data = MockITSService.fetch_user_data(value)
            if not user_data:
                raise serializers.ValidationError(
                    f"ITS ID '{value}' not found in ITS system. Please check the ID and try again."
                )
                
        return value
    
    def validate_preferred_time(self, value):
        """Validate preferred time is not in the past"""
        if value and value < timezone.now():
            raise serializers.ValidationError("Preferred time cannot be in the past")
        return value


class DuaArazCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new DuaAraz requests"""
    preferred_doctor_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = DuaAraz
        fields = [
            'patient_its_id', 'patient_name', 'patient_phone', 'patient_email',
            'ailment', 'symptoms', 'urgency_level', 'request_type',
            'previous_medical_history', 'current_medications', 'allergies',
            'preferred_doctor_id', 'preferred_location', 'preferred_time',
            'preferred_contact_method'
        ]
    
    def validate_preferred_doctor_id(self, value):
        """Validate preferred doctor exists"""
        if value:
            try:
                Doctor.objects.get(id=value)
            except Doctor.DoesNotExist:
                raise serializers.ValidationError("Invalid doctor ID")
        return value
    
    def create(self, validated_data):
        """Create a new DuaAraz request"""
        preferred_doctor_id = validated_data.pop('preferred_doctor_id', None)
        
        # Set patient_user if authenticated user is making the request
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['patient_user'] = request.user
            # Auto-fill patient details from user profile if not provided
            if not validated_data.get('patient_name'):
                validated_data['patient_name'] = request.user.get_full_name()
            if not validated_data.get('patient_email'):
                validated_data['patient_email'] = request.user.email
            if not validated_data.get('patient_phone') and hasattr(request.user, 'mobile_number'):
                validated_data['patient_phone'] = request.user.mobile_number
        
        # Set preferred doctor
        if preferred_doctor_id:
            try:
                validated_data['preferred_doctor'] = Doctor.objects.get(id=preferred_doctor_id)
            except Doctor.DoesNotExist:
                pass
        
        return super().create(validated_data)


class PetitionCategorySerializer(serializers.ModelSerializer):
    """Serializer for petition categories"""
    petition_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PetitionCategory
        fields = [
            'id', 'name', 'description', 'color', 'is_active',
            'created_at', 'petition_count'
        ]
        read_only_fields = ['id', 'created_at', 'petition_count']
    
    def get_petition_count(self, obj):
        """Get count of petitions in this category"""
        return obj.petitions.count()


class PetitionAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for petition attachments"""
    uploaded_by = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PetitionAttachment
        fields = [
            'id', 'file', 'file_url', 'filename',
            'uploaded_by', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class PetitionCommentSerializer(serializers.ModelSerializer):
    """Serializer for petition comments"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PetitionComment
        fields = [
            'id', 'content', 'user', 'is_internal', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class PetitionAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for petition assignments"""
    assigned_to = UserSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)
    
    class Meta:
        model = PetitionAssignment
        fields = [
            'id', 'assigned_to', 'assigned_by', 'assigned_at',
            'notes', 'is_active'
        ]
        read_only_fields = ['id', 'assigned_by', 'assigned_at']


class PetitionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for petition updates"""
    created_by = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PetitionUpdate
        fields = [
            'id', 'status', 'status_display', 'description',
            'created_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class PetitionSerializer(serializers.ModelSerializer):
    """Comprehensive serializer for Petition model"""
    created_by = UserSerializer(read_only=True)
    category = PetitionCategorySerializer(read_only=True)
    comments = PetitionCommentSerializer(many=True, read_only=True)
    attachments = PetitionAttachmentSerializer(many=True, read_only=True)
    assignments = PetitionAssignmentSerializer(many=True, read_only=True)
    updates = PetitionUpdateSerializer(many=True, read_only=True)
    
    # Display fields
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Computed fields
    days_since_created = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    current_assignee = serializers.SerializerMethodField()
    
    class Meta:
        model = Petition
        fields = [
            # Basic info
            'id', 'title', 'description', 'category', 'created_by', 'is_anonymous',
            
            # Status and priority
            'status', 'status_display', 'priority', 'priority_display',
            
            # Location
            'moze',
            
            # Timestamps
            'created_at', 'updated_at', 'resolved_at',
            
            # Computed fields
            'days_since_created', 'is_overdue', 'current_assignee',
            
            # Related data
            'comments', 'attachments', 'assignments', 'updates'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at', 'resolved_at',
            'days_since_created', 'is_overdue', 'current_assignee',
            'comments', 'attachments', 'assignments', 'updates'
        ]
    
    def get_days_since_created(self, obj):
        """Calculate days since the petition was created"""
        return (timezone.now() - obj.created_at).days
    
    def get_is_overdue(self, obj):
        """Check if the petition is overdue based on priority"""
        days_since = self.get_days_since_created(obj)
        
        overdue_thresholds = {
            'high': 3,
            'medium': 7,
            'low': 14
        }
        
        threshold = overdue_thresholds.get(obj.priority, 7)
        return days_since > threshold and obj.status not in ['resolved', 'rejected']
    
    def get_current_assignee(self, obj):
        """Get current active assignee"""
        active_assignment = obj.assignments.filter(is_active=True).first()
        if active_assignment:
            return UserSerializer(active_assignment.assigned_to).data
        return None


class PetitionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new petitions"""
    category_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Petition
        fields = [
            'title', 'description', 'category_id', 'priority',
            'is_anonymous', 'moze'
        ]
    
    def validate_category_id(self, value):
        """Validate category exists and is active"""
        if value:
            try:
                category = PetitionCategory.objects.get(id=value, is_active=True)
            except PetitionCategory.DoesNotExist:
                raise serializers.ValidationError("Invalid or inactive category")
        return value
    
    def create(self, validated_data):
        """Create a new petition"""
        category_id = validated_data.pop('category_id', None)
        
        # Set created_by from request user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        # Set category
        if category_id:
            try:
                validated_data['category'] = PetitionCategory.objects.get(id=category_id)
            except PetitionCategory.DoesNotExist:
                pass
        
        return super().create(validated_data)


class PetitionStatusSerializer(serializers.ModelSerializer):
    """Serializer for petition statuses"""
    
    class Meta:
        model = PetitionStatus
        fields = ['id', 'name', 'color', 'is_final', 'order']
        read_only_fields = ['id']


# Statistics serializers
class ArazStatsSerializer(serializers.Serializer):
    """Serializer for Araz statistics"""
    total_araz = serializers.IntegerField()
    pending_araz = serializers.IntegerField()
    in_progress_araz = serializers.IntegerField()
    completed_araz = serializers.IntegerField()
    emergency_araz = serializers.IntegerField()
    overdue_araz = serializers.IntegerField()
    recent_araz = serializers.IntegerField()
    
    # By request type
    araz_by_type = serializers.DictField()
    
    # By urgency level
    araz_by_urgency = serializers.DictField()
    
    # By status
    araz_by_status = serializers.DictField()


class PetitionStatsSerializer(serializers.Serializer):
    """Serializer for petition statistics"""
    total_petitions = serializers.IntegerField()
    pending_petitions = serializers.IntegerField()
    in_progress_petitions = serializers.IntegerField()
    resolved_petitions = serializers.IntegerField()
    rejected_petitions = serializers.IntegerField()
    overdue_petitions = serializers.IntegerField()
    recent_petitions = serializers.IntegerField()
    
    # By category
    petitions_by_category = serializers.DictField()
    
    # By priority
    petitions_by_priority = serializers.DictField()
    
    # By status
    petitions_by_status = serializers.DictField()


# Search serializers
class ArazSearchSerializer(serializers.Serializer):
    """Serializer for Araz search parameters"""
    query = serializers.CharField(max_length=200, required=False)
    status = serializers.ChoiceField(choices=DuaAraz.STATUS_CHOICES, required=False)
    urgency_level = serializers.CharField(max_length=20, required=False)
    request_type = serializers.ChoiceField(choices=DuaAraz.REQUEST_TYPES, required=False)
    priority = serializers.CharField(max_length=20, required=False)
    assigned_doctor = serializers.IntegerField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    is_overdue = serializers.BooleanField(required=False)


class PetitionSearchSerializer(serializers.Serializer):
    """Serializer for petition search parameters"""
    query = serializers.CharField(max_length=200, required=False)
    status = serializers.ChoiceField(choices=Petition.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Petition.PRIORITY_CHOICES, required=False)
    category = serializers.IntegerField(required=False)
    created_by = serializers.IntegerField(required=False)
    assigned_to = serializers.IntegerField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    is_overdue = serializers.BooleanField(required=False)
    moze = serializers.IntegerField(required=False)