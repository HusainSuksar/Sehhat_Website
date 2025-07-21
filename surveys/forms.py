from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

from .models import Survey, SurveyResponse, SurveyReminder

User = get_user_model()


class SurveyForm(forms.ModelForm):
    """Form for creating and editing surveys"""
    
    class Meta:
        model = Survey
        fields = [
            'title', 'description', 'start_date', 'end_date', 
            'target_role', 'is_anonymous', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter survey title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe the purpose of this survey'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'target_role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default dates
        if not self.instance.pk:
            self.fields['start_date'].initial = timezone.now().date()
            self.fields['end_date'].initial = timezone.now().date() + timezone.timedelta(days=30)
        
        # Set required fields
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        
        # Add help text
        self.fields['target_role'].help_text = 'Select role who should receive this survey'
        self.fields['is_anonymous'].help_text = 'Allow anonymous responses to this survey'
        self.fields['is_active'].help_text = 'Survey is currently active and accepting responses'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError('End date must be after start date.')
            
            if start_date < timezone.now().date():
                raise forms.ValidationError('Start date cannot be in the past.')
        
        return cleaned_data


class SurveyResponseForm(forms.ModelForm):
    """Form for survey responses"""
    
    class Meta:
        model = SurveyResponse
        fields = ['answers']
        widgets = {
            'answers': forms.HiddenInput()
        }
    
    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('survey', None)
        super().__init__(*args, **kwargs)
        
        if self.survey:
            self.generate_question_fields()
    
    def generate_question_fields(self):
        """Dynamically generate form fields based on survey questions"""
        for question in self.survey.questions:
            field_name = f"question_{question['id']}"
            
            if question['type'] == 'text':
                self.fields[field_name] = forms.CharField(
                    label=question['text'],
                    required=question.get('required', False),
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            
            elif question['type'] == 'textarea':
                self.fields[field_name] = forms.CharField(
                    label=question['text'],
                    required=question.get('required', False),
                    widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
                )
            
            elif question['type'] == 'multiple_choice':
                choices = [(option, option) for option in question.get('options', [])]
                self.fields[field_name] = forms.ChoiceField(
                    label=question['text'],
                    choices=choices,
                    required=question.get('required', False),
                    widget=forms.RadioSelect()
                )
            
            elif question['type'] == 'checkbox':
                choices = [(option, option) for option in question.get('options', [])]
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question['text'],
                    choices=choices,
                    required=question.get('required', False),
                    widget=forms.CheckboxSelectMultiple()
                )
            
            elif question['type'] == 'rating':
                choices = [(i, str(i)) for i in range(1, 6)]  # 1-5 rating
                self.fields[field_name] = forms.ChoiceField(
                    label=question['text'],
                    choices=choices,
                    required=question.get('required', False),
                    widget=forms.RadioSelect()
                )
            
            elif question['type'] == 'email':
                self.fields[field_name] = forms.EmailField(
                    label=question['text'],
                    required=question.get('required', False),
                    widget=forms.EmailInput(attrs={'class': 'form-control'})
                )
            
            elif question['type'] == 'number':
                self.fields[field_name] = forms.IntegerField(
                    label=question['text'],
                    required=question.get('required', False),
                    widget=forms.NumberInput(attrs={'class': 'form-control'})
                )


class SurveyReminderForm(forms.ModelForm):
    """Form for creating survey reminders"""
    
    class Meta:
        model = SurveyReminder
        fields = ['max_reminders', 'is_active']
        widgets = {
            'max_reminders': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set defaults
        if not self.instance.pk:
            self.fields['max_reminders'].initial = 3
            self.fields['is_active'].initial = True
        
        # Add help text
        self.fields['max_reminders'].help_text = 'Maximum number of reminders to send'
        self.fields['is_active'].help_text = 'Enable reminders for this survey'


class SurveySearchForm(forms.Form):
    """Form for searching and filtering surveys"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search surveys by title or description...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Surveys'),
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('pending', 'Pending Response'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    target_audience = forms.ChoiceField(
        choices=[
            ('', 'All Audiences'),
            ('aamil', 'Aamils'),
            ('moze_coordinator', 'Moze Coordinators'),
            ('doctor', 'Doctors'),
            ('student', 'Students'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search'].label = 'Search'
        self.fields['status'].label = 'Status'
        self.fields['target_audience'].label = 'Target Audience'