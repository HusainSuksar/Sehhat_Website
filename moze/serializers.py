"""
Serializers for the Moze app
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Moze, UmoorSehhatTeam, MozeComment, MozeSettings

User = get_user_model()


# Basic User serializer for nested relationships
class UserBasicSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name', 'role']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return obj.get_full_name()


# Moze Settings Serializer
class MozeSettingsSerializer(serializers.ModelSerializer):
    working_hours_display = serializers.SerializerMethodField()
    is_currently_open = serializers.SerializerMethodField()
    next_working_day = serializers.SerializerMethodField()
    
    class Meta:
        model = MozeSettings
        fields = [
            'id', 'allow_walk_ins', 'appointment_duration', 'working_hours_start',
            'working_hours_end', 'working_hours_display', 'working_days', 
            'emergency_contact', 'special_instructions', 'is_currently_open',
            'next_working_day', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_working_hours_display(self, obj):
        return f"{obj.working_hours_start.strftime('%H:%M')} - {obj.working_hours_end.strftime('%H:%M')}"
    
    def get_is_currently_open(self, obj):
        now = timezone.now()
        current_time = now.time()
        current_weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        if current_weekday in obj.working_days:
            return obj.working_hours_start <= current_time <= obj.working_hours_end
        return False
    
    def get_next_working_day(self, obj):
        if not obj.working_days:
            return None
        
        current_weekday = timezone.now().weekday()
        working_days = sorted(obj.working_days)
        
        # Find next working day
        for day in working_days:
            if day > current_weekday:
                return day
        
        # If no working day found this week, return first working day of next week
        return working_days[0]


# Umoor Sehhat Team Serializer
class UmoorSehhatTeamSerializer(serializers.ModelSerializer):
    member = UserBasicSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='member'
    )
    moze_name = serializers.SerializerMethodField()
    category_display = serializers.SerializerMethodField()
    days_since_joined = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UmoorSehhatTeam
        fields = [
            'id', 'moze', 'moze_name', 'category', 'category_display', 'member', 'member_id',
            'photo', 'photo_url', 'contact_number', 'position', 'is_active',
            'days_since_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_moze_name(self, obj):
        return obj.moze.name
    
    def get_category_display(self, obj):
        return obj.get_category_display()
    
    def get_days_since_joined(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


# Moze Comment Serializer (with nested replies)
class MozeCommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source='author', required=False
    )
    moze_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    days_since_posted = serializers.SerializerMethodField()
    is_reply = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = MozeComment
        fields = [
            'id', 'moze', 'moze_name', 'content', 'author', 'author_id', 'parent', 'is_active',
            'replies', 'reply_count', 'days_since_posted', 'is_reply',
            'can_edit', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_moze_name(self, obj):
        return obj.moze.name
    
    def get_replies(self, obj):
        if obj.parent is None:  # Only get replies for top-level comments
            replies = obj.get_replies()
            return MozeCommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def get_reply_count(self, obj):
        return obj.get_replies().count()
    
    def get_days_since_posted(self, obj):
        return (timezone.now().date() - obj.created_at.date()).days
    
    def get_is_reply(self, obj):
        return obj.parent is not None
    
    def get_can_edit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return (obj.author == request.user or 
                   request.user.is_admin or 
                   request.user.role in ['aamil', 'moze_coordinator'])
        return False


# Main Moze Serializer
class MozeSerializer(serializers.ModelSerializer):
    aamil = UserBasicSerializer(read_only=True)
    aamil_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='aamil'), write_only=True, source='aamil'
    )
    moze_coordinator = UserBasicSerializer(read_only=True)
    moze_coordinator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='moze_coordinator'), 
        write_only=True, source='moze_coordinator', required=False, allow_null=True
    )
    team_members = UserBasicSerializer(many=True, read_only=True)
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, 
        source='team_members', required=False
    )
    settings = MozeSettingsSerializer(read_only=True)
    umoor_teams = UmoorSehhatTeamSerializer(many=True, read_only=True)
    recent_comments = serializers.SerializerMethodField()
    
    # Computed fields
    team_count = serializers.SerializerMethodField()
    active_doctors_count = serializers.SerializerMethodField()
    days_since_established = serializers.SerializerMethodField()
    is_currently_open = serializers.SerializerMethodField()
    total_team_members = serializers.SerializerMethodField()
    team_categories_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Moze
        fields = [
            'id', 'name', 'location', 'address', 'aamil', 'aamil_id',
            'team_members', 'team_member_ids', 'moze_coordinator', 'moze_coordinator_id',
            'established_date', 'is_active', 'capacity', 'contact_phone', 'contact_email',
            'settings', 'umoor_teams', 'recent_comments', 'team_count', 
            'active_doctors_count', 'days_since_established', 'is_currently_open',
            'total_team_members', 'team_categories_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_recent_comments(self, obj):
        recent_comments = obj.comments.filter(is_active=True, parent=None)[:3]
        return MozeCommentSerializer(recent_comments, many=True, context=self.context).data
    
    def get_team_count(self, obj):
        return obj.get_team_count()
    
    def get_active_doctors_count(self, obj):
        try:
            return obj.get_active_doctors().count()
        except:
            # Handle case where assigned_doctors relationship doesn't exist
            return 0
    
    def get_days_since_established(self, obj):
        if obj.established_date:
            return (timezone.now().date() - obj.established_date).days
        return None
    
    def get_is_currently_open(self, obj):
        if hasattr(obj, 'settings'):
            serializer = MozeSettingsSerializer(obj.settings)
            return serializer.get_is_currently_open(obj.settings)
        return False
    
    def get_total_team_members(self, obj):
        return obj.umoor_teams.filter(is_active=True).count()
    
    def get_team_categories_count(self, obj):
        categories = obj.umoor_teams.filter(is_active=True).values_list('category', flat=True).distinct()
        return len(categories)


# Create Moze Serializer (simplified for creation)
class MozeCreateSerializer(serializers.ModelSerializer):
    aamil_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='aamil'), source='aamil'
    )
    moze_coordinator_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='moze_coordinator'), 
        source='moze_coordinator', required=False, allow_null=True
    )
    team_member_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, 
        source='team_members', required=False
    )
    
    class Meta:
        model = Moze
        fields = [
            'name', 'location', 'address', 'aamil_id', 'moze_coordinator_id',
            'team_member_ids', 'established_date', 'is_active', 'capacity',
            'contact_phone', 'contact_email'
        ]
    
    def create(self, validated_data):
        team_members_data = validated_data.pop('team_members', [])
        moze = Moze.objects.create(**validated_data)
        
        if team_members_data:
            moze.team_members.set(team_members_data)
        
        # Create default settings
        MozeSettings.objects.create(
            moze=moze,
            working_days=[0, 1, 2, 3, 4, 5]  # Monday to Saturday
        )
        
        return moze


# Statistics Serializers
class MozeStatsSerializer(serializers.Serializer):
    total_mozes = serializers.IntegerField()
    active_mozes = serializers.IntegerField()
    total_team_members = serializers.IntegerField()
    mozes_by_category = serializers.DictField()
    average_capacity = serializers.FloatField()
    mozes_with_coordinators = serializers.IntegerField()


class TeamStatsSerializer(serializers.Serializer):
    total_team_members = serializers.IntegerField()
    active_team_members = serializers.IntegerField()
    members_by_category = serializers.DictField()
    members_by_moze = serializers.DictField()
    average_members_per_moze = serializers.FloatField()


# Search Serializers
class MozeSearchSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    aamil = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    has_coordinator = serializers.BooleanField(required=False)


class TeamSearchSerializer(serializers.Serializer):
    category = serializers.CharField(required=False)
    member_name = serializers.CharField(required=False)
    moze_name = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    position = serializers.CharField(required=False)