from django import forms
from django.contrib.auth import get_user_model
from .models import PhotoAlbum, Photo, PhotoTag, PhotoComment
from moze.models import Moze

User = get_user_model()


class PhotoAlbumForm(forms.ModelForm):
    """Form for creating and editing photo albums"""
    
    class Meta:
        model = PhotoAlbum
        fields = ['name', 'description', 'moze', 'is_public', 'allow_uploads']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter album name',
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe this photo album...',
                'rows': 4
            }),
            'moze': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_uploads': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_admin:
                self.fields['moze'].queryset = Moze.objects.filter(is_active=True)
            else:
                self.fields['moze'].queryset = Moze.objects.filter(is_active=True)


class PhotoForm(forms.ModelForm):
    """Form for uploading and editing photos"""
    
    class Meta:
        model = Photo
        fields = ['title', 'description', 'album', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter photo title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe this photo...',
                'rows': 3
            }),
            'album': forms.Select(attrs={
                'class': 'form-control'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter albums based on user permissions
            if user.is_admin:
                self.fields['album'].queryset = PhotoAlbum.objects.all()
            else:
                self.fields['album'].queryset = PhotoAlbum.objects.filter(
                    created_by=user
                ).union(
                    PhotoAlbum.objects.filter(allow_uploads=True, is_public=True)
                )


class PhotoUploadForm(forms.Form):
    """Form for uploading multiple photos"""
    
    photos = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'multiple': True,
            'accept': 'image/*'
        }),
        help_text="Select multiple photos to upload"
    )
    
    album = forms.ModelChoiceField(
        queryset=PhotoAlbum.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the album for these photos"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_admin:
                self.fields['album'].queryset = PhotoAlbum.objects.all()
            else:
                self.fields['album'].queryset = PhotoAlbum.objects.filter(
                    created_by=user
                ).union(
                    PhotoAlbum.objects.filter(allow_uploads=True, is_public=True)
                )


class PhotoCommentForm(forms.ModelForm):
    """Form for adding comments to photos"""
    
    class Meta:
        model = PhotoComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add your comment...',
                'rows': 3
            })
        }


class PhotoTagForm(forms.Form):
    """Form for adding tags to photos"""
    
    tags = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas'
        }),
        help_text="Enter tags separated by commas (e.g., nature, landscape, event)"
    )


class PhotoFilterForm(forms.Form):
    """Form for filtering photos"""
    
    album = forms.ModelChoiceField(
        queryset=PhotoAlbum.objects.all(),
        required=False,
        empty_label="All Albums",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tag = forms.ModelChoiceField(
        queryset=PhotoTag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search photos...'
        })
    )
