from django import forms
from django.contrib.auth import get_user_model
from .models import EvaluationForm, EvaluationCriteria, EvaluationSubmission, EvaluationSession, EvaluationAnswerOption

User = get_user_model()


class EvaluationFormCreateForm(forms.ModelForm):
    """Form for creating evaluation forms"""
    
    class Meta:
        model = EvaluationForm
        fields = [
            'title', 'description', 'evaluation_type', 'target_role',
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
            'evaluation_type': forms.Select(attrs={
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
            'name', 'description', 'question_type', 'is_required',
            'max_score', 'weight', 'category', 'order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the evaluation question...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter the evaluation criteria description...'
            }),
            'question_type': forms.Select(attrs={
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
                'min': '0.1',
                'max': '10.0',
                'step': '0.1'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }


class EvaluationAnswerOptionForm(forms.ModelForm):
    """Form for adding answer options to criteria"""
    
    class Meta:
        model = EvaluationAnswerOption
        fields = ['option_text', 'weight', 'order', 'is_active']
        widgets = {
            'option_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter answer option...'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.0',
                'max': '10.0',
                'step': '0.1',
                'placeholder': 'e.g., 5.0 for Option A, 3.0 for Option B'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class EvaluationSubmissionForm(forms.ModelForm):
    """Form for submitting evaluations with dynamic fields based on criteria"""
    
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
                
                if criteria.question_type == 'rating':
                    self.fields[field_name] = forms.IntegerField(
                        label=criteria.name,
                        min_value=1,
                        max_value=criteria.max_score,
                        required=criteria.is_required,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'min': '1',
                            'max': str(criteria.max_score)
                        })
                    )
                elif criteria.question_type == 'dropdown':
                    # Get answer options for dropdown
                    options = criteria.get_answer_options()
                    choices = [(opt.id, opt.option_text) for opt in options]
                    self.fields[field_name] = forms.ChoiceField(
                        label=criteria.name,
                        choices=choices,
                        required=criteria.is_required,
                        widget=forms.Select(attrs={
                            'class': 'form-control'
                        })
                    )
                elif criteria.question_type == 'multiple_choice':
                    # Get answer options for multiple choice
                    options = criteria.get_answer_options()
                    choices = [(opt.id, opt.option_text) for opt in options]
                    self.fields[field_name] = forms.ChoiceField(
                        label=criteria.name,
                        choices=choices,
                        required=criteria.is_required,
                        widget=forms.RadioSelect(attrs={
                            'class': 'form-check-input'
                        })
                    )
                elif criteria.question_type == 'text':
                    self.fields[field_name] = forms.CharField(
                        label=criteria.name,
                        required=criteria.is_required,
                        widget=forms.Textarea(attrs={
                            'class': 'form-control',
                            'rows': 3
                        })
                    )
                elif criteria.question_type == 'boolean':
                    self.fields[field_name] = forms.BooleanField(
                        label=criteria.name,
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
            'title', 'description', 'form', 'start_date', 'end_date', 'is_active'
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
            'form': forms.Select(attrs={
                'class': 'form-control'
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
        self.fields['form'].queryset = EvaluationForm.objects.filter(
            is_active=True
        )


class EvaluationFilterForm(forms.Form):
    """Form for filtering evaluations"""
    
    evaluation_type = forms.ChoiceField(
        choices=[('', 'All Types')] + EvaluationForm.EVALUATION_TYPE_CHOICES,
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