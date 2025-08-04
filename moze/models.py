from django.db import models
from django.conf import settings


class Moze(models.Model):
    """Model for Moze (Medical Centers)"""
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    aamil = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='managed_mozes',
        limit_choices_to={'role': 'aamil'}
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='moze_teams',
        blank=True,
        help_text='Team members assigned to this Moze'
    )
    moze_coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_mozes',
        limit_choices_to={'role': 'moze_coordinator'}
    )
    established_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField(default=100, help_text='Maximum patient capacity')
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Moze'
        verbose_name_plural = 'Mozes'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def get_team_count(self):
        return self.team_members.count()
    
    def get_active_doctors(self):
        return self.assigned_doctors.filter(user__is_active=True)


class UmoorSehhatTeam(models.Model):
    """Umoor Sehhat team members with categories"""
    TEAM_CATEGORIES = [
        ('medical', 'Medical'),
        ('sports', 'Sports'),
        ('nazafat', 'Nazafat'),
        ('environment', 'Environment'),
    ]
    
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='umoor_teams')
    category = models.CharField(max_length=20, choices=TEAM_CATEGORIES)
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='umoor_team_memberships')
    photo = models.ImageField(upload_to='team_photos/', blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True)
    position = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['moze', 'member', 'category']
        ordering = ['category', 'member__first_name']
        verbose_name = 'Umoor Sehhat Team Member'
        verbose_name_plural = 'Umoor Sehhat Team Members'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.get_category_display()} ({self.moze.name})"


class MozeComment(models.Model):
    """Threaded comments for Moze dashboard"""
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.moze.name}"
    
    def get_replies(self):
        return self.replies.filter(is_active=True)


class MozeSettings(models.Model):
    """Settings and configuration for individual Mozes"""
    moze = models.OneToOneField(Moze, on_delete=models.CASCADE, related_name='settings')
    allow_walk_ins = models.BooleanField(default=True)
    appointment_duration = models.PositiveIntegerField(default=30, help_text='Default appointment duration in minutes')
    working_hours_start = models.TimeField(default='09:00')
    working_hours_end = models.TimeField(default='17:00')
    working_days = models.JSONField(default=list, help_text='List of working days (0=Monday, 6=Sunday)')
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.moze.name}"
    
    class Meta:
        verbose_name = 'Moze Settings'
        verbose_name_plural = 'Moze Settings'
