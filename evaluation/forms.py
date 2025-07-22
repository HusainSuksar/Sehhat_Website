from django import forms
from django.contrib.auth import get_user_model
from .models import EvaluationForm, EvaluationCriteria, EvaluationSubmission, EvaluationSession

User = get_user_model()


class EvaluationFormCreateForm(forms.ModelForm):
    """Form for creating evaluation forms"""
    
    class Meta:
        model = EvaluationForm
        fields = [
            'title', 'description', 'form_type', 'target_role',
            'due_date', 'is_anonymous', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter evaluation form title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the purpose of this evaluation...'
            }),
            'form_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'target_role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class EvaluationCriteriaForm(forms.ModelForm):
    """Form for adding criteria to evaluation forms"""
    
    class Meta:
        model = EvaluationCriteria
        fields = [
            'criteria_text', 'criteria_type', 'is_required',
            'max_score', 'weight', 'order'
        ]
        widgets = {
            'criteria_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter the evaluation criteria...'
            }),
            'criteria_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'max_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.1'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class EvaluationSubmissionForm(forms.ModelForm):
    """Form for submitting evaluations"""
    
    class Meta:
        model = EvaluationSubmission
        fields = ['comments']
        widgets = {
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional comments (optional)...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        evaluation_form = kwargs.pop('evaluation_form', None)
        super().__init__(*args, **kwargs)
        
        if evaluation_form:
            # Dynamically add fields for each criteria
            for criteria in evaluation_form.criteria.all():
                field_name = f'criteria_{criteria.id}'
                
                if criteria.criteria_type == 'rating':
                    self.fields[field_name] = forms.IntegerField(
                        label=criteria.criteria_text,
                        min_value=1,
                        max_value=criteria.max_score,
                        required=criteria.is_required,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'min': '1',
                            'max': str(criteria.max_score)
                        })
                    )
                elif criteria.criteria_type == 'text':
                    self.fields[field_name] = forms.CharField(
                        label=criteria.criteria_text,
                        required=criteria.is_required,
                        widget=forms.Textarea(attrs={
                            'class': 'form-control',
                            'rows': 3
                        })
                    )
                elif criteria.criteria_type == 'boolean':
                    self.fields[field_name] = forms.BooleanField(
                        label=criteria.criteria_text,
                        required=criteria.is_required,
                        widget=forms.CheckboxInput(attrs={
                            'class': 'form-check-input'
                        })
                    )


class EvaluationSessionForm(forms.ModelForm):
    """Form for creating evaluation sessions"""
    
    class Meta:
        model = EvaluationSession
        fields = [
            'title', 'description', 'evaluation_forms', 'target_users',
            'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter session title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe this evaluation session...'
            }),
            'evaluation_forms': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '5'
            }),
            'target_users': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': '8'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter active evaluation forms
        self.fields['evaluation_forms'].queryset = EvaluationForm.objects.filter(
            is_active=True
        )
        
        # Filter active users
        self.fields['target_users'].queryset = User.objects.filter(
            is_active=True
        ).exclude(role='student')


class EvaluationFilterForm(forms.Form):
    """Form for filtering evaluations"""
    
    form_type = forms.ChoiceField(
        choices=[('', 'All Types')] + EvaluationForm.FORM_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    target_role = forms.ChoiceField(
        choices=[('', 'All Roles')] + EvaluationForm.TARGET_ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('expired', 'Expired')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search evaluations...'
        })
    )


class BulkEvaluationForm(forms.Form):
    """Form for bulk evaluation operations"""
    
    action = forms.ChoiceField(
        choices=[
            ('activate', 'Activate'),
            ('deactivate', 'Deactivate'),
            ('delete', 'Delete'),
            ('duplicate', 'Duplicate')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    evaluation_forms = forms.ModelMultipleChoiceField(
        queryset=EvaluationForm.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )
