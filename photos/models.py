from django.db import models
from django.conf import settings
from moze.models import Moze


class Photo(models.Model):
    """Photo model for gallery and documentation"""
    image = models.ImageField(upload_to='photos/%Y/%m/%d/')
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    subject_tag = models.CharField(max_length=100, help_text='Tag to categorize the photo')
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='photos')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_photos')
    
    # Photo metadata
    location = models.CharField(max_length=200, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    photographer = models.CharField(max_length=100, blank=True, null=True)
    
    # Photo categories
    CATEGORY_CHOICES = [
        ('medical', 'Medical/Clinical'),
        ('event', 'Event/Activity'),
        ('infrastructure', 'Infrastructure/Facility'),
        ('team', 'Team/Staff'),
        ('patient', 'Patient Care'),
        ('equipment', 'Medical Equipment'),
        ('documentation', 'Documentation'),
        ('other', 'Other'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    
    # Privacy and access
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    requires_permission = models.BooleanField(default=True, help_text='Requires permission before sharing')
    
    # File information
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text='File size in bytes')
    image_width = models.PositiveIntegerField(blank=True, null=True)
    image_height = models.PositiveIntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Photo'
        verbose_name_plural = 'Photos'
    
    def __str__(self):
        return f"{self.title or 'Photo'} - {self.subject_tag} ({self.moze.name})"
    
    def get_file_size_mb(self):
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return None
    
    def save(self, *args, **kwargs):
        if self.image and hasattr(self.image, 'file'):
            self.file_size = self.image.file.size
            # You could also extract image dimensions here using PIL
        super().save(*args, **kwargs)


class PhotoAlbum(models.Model):
    """Photo album for organizing related photos"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    moze = models.ForeignKey(Moze, on_delete=models.CASCADE, related_name='photo_albums')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_albums')
    photos = models.ManyToManyField(Photo, related_name='albums', blank=True)
    
    cover_photo = models.ForeignKey(
        Photo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='albums_as_cover'
    )
    
    is_public = models.BooleanField(default=False)
    allow_uploads = models.BooleanField(default=True, help_text='Allow team members to upload photos')
    event_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'moze']
        verbose_name = 'Photo Album'
        verbose_name_plural = 'Photo Albums'
    
    def __str__(self):
        return f"{self.name} - {self.moze.name}"
    
    def get_photo_count(self):
        return self.photos.count()


class PhotoComment(models.Model):
    """Comments on photos"""
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.photo}"


class PhotoLike(models.Model):
    """Likes on photos"""
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['photo', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} likes {self.photo}"


class PhotoTag(models.Model):
    """Tags for photos for better organization"""
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Add many-to-many relationship between Photo and PhotoTag
Photo.add_to_class('tags', models.ManyToManyField(PhotoTag, related_name='photos', blank=True))
