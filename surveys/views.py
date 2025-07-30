from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
import json
import csv

from .models import Survey, SurveyResponse, SurveyReminder, SurveyAnalytics
from .forms import SurveyForm, SurveyResponseForm, SurveyReminderForm
from accounts.models import User


class SurveyAccessMixin(UserPassesTestMixin):
    """Mixin to check if user has access to survey management"""
    def test_func(self):
        return (self.request.user.role == "admin" or 
                self.request.user.role == "aamil" or 
                self.request.user.role == "moze_coordinator")


@login_required
def survey_dashboard(request):
    """Survey dashboard with analytics and management"""
    user = request.user
    
    # Get user's accessible surveys
    if user.role == "admin":
        surveys = Survey.objects.all()
    elif user.role == "aamil" or user.role == "moze_coordinator":
        surveys = Survey.objects.filter(
            Q(created_by=user) | 
            Q(target_role=user.role) |
            Q(target_role="all")
        )
    else:
        surveys = Survey.objects.filter(
            Q(target_role=user.role) |
            Q(target_role="all"),
            is_active=True
        )
    
    # Statistics
    total_surveys = surveys.count()
    active_surveys = surveys.filter(is_active=True).count()
    my_responses = SurveyResponse.objects.filter(respondent=user).count()
    pending_surveys = surveys.filter(
        is_active=True
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
    ).exclude(
        id__in=SurveyResponse.objects.filter(respondent=user).values('survey_id')
    ).count()
    
    # Recent surveys
    recent_surveys = surveys.filter(is_active=True).order_by('-created_at')[:5]
    
    # Analytics for admins/coordinators
    analytics_data = {}
    if user.role == "admin" or user.role == "aamil" or user.role == "moze_coordinator":
        created_surveys = surveys.filter(created_by=user)
        analytics_data = {
            'created_surveys': created_surveys.count(),
            'total_responses': SurveyResponse.objects.filter(survey__in=created_surveys).count(),
            'completion_rate': 0,
        }
        
        if created_surveys.exists():
            total_invited = 0
            total_responses = 0
            for survey in created_surveys:
                if survey.target_role == "all":
                    target_count = User.objects.count()
                else:
                    target_count = User.objects.filter(role=survey.target_role).count()
                response_count = survey.responses.count()
                total_invited += target_count
                total_responses += response_count
            
            if total_invited > 0:
                analytics_data['completion_rate'] = round((total_responses / total_invited) * 100, 1)
    
    context = {
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'my_responses': my_responses,
        'pending_surveys': pending_surveys,
        'recent_surveys': recent_surveys,
        'analytics_data': analytics_data,
        'user_role': user.get_role_display(),
    }
    
    return render(request, 'surveys/dashboard.html', context)


class SurveyListView(LoginRequiredMixin, ListView):
    """List all available surveys"""
    model = Survey
    template_name = 'surveys/survey_list.html'
    context_object_name = 'surveys'
    paginate_by = 12
    
    def get_queryset(self):
        user = self.request.user
        
        # Base queryset based on user role
        if user.role == "admin":
            queryset = Survey.objects.all()
        elif user.role == "aamil" or user.role == "moze_coordinator":
            queryset = Survey.objects.filter(
                Q(created_by=user) | 
                Q(target_role=user.role) |
                Q(target_role="all")
            )
        else:
            queryset = Survey.objects.filter(
                Q(target_role=user.role) |
                Q(target_role="all"),
                is_active=True
            )
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'completed':
            queryset = queryset.filter(
                Q(end_date__isnull=False) & Q(end_date__lt=timezone.now())
            )
        elif status == 'pending':
            queryset = queryset.exclude(
                id__in=SurveyResponse.objects.filter(respondent=user).values('survey_id')
            )
        
        return queryset.select_related('created_by').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        
        # Add user responses to context
        user_responses = {}
        if self.request.user.is_authenticated:
            responses = SurveyResponse.objects.filter(
                respondent=self.request.user,
                survey__in=context['surveys']
            ).values('survey_id', 'created_at')
            user_responses = {r['survey_id']: r['created_at'] for r in responses}
        
        context['user_responses'] = user_responses
        return context


survey_list = SurveyListView.as_view()


class SurveyDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a survey"""
    model = Survey
    template_name = 'surveys/survey_detail.html'
    context_object_name = 'survey'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Survey.objects.all()
        elif user.role == "aamil" or user.role == "moze_coordinator":
            return Survey.objects.filter(
                Q(created_by=user) | 
                Q(target_role=user.role) |
                Q(target_role="all")
            )
        else:
            return Survey.objects.filter(
                Q(target_role=user.role) |
                Q(target_role="all"),
                is_active=True
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey = self.object
        user = self.request.user
        
        # Check if user has already responded
        user_response = SurveyResponse.objects.filter(
            survey=survey,
            respondent=user
        ).first()
        
        context['user_response'] = user_response
        context['can_take_survey'] = (
            not user_response and 
            survey.is_active and 
            (survey.end_date is None or survey.end_date >= timezone.now()) and
            (user.role == survey.target_role or survey.target_role == "all")
        )
        
        # Survey statistics for creators
        if user == survey.created_by or user.role == "admin":
            total_responses = survey.responses.count()
            target_users = User.objects.filter(role__in=survey.target_role).count()
            
            context['survey_stats'] = {
                'total_responses': total_responses,
                'target_users': target_users,
                'completion_rate': round((total_responses / target_users) * 100, 1) if target_users > 0 else 0,
                'recent_responses': survey.responses.select_related('user').order_by('-created_at')[:5]
            }
        
        return context


survey_detail = SurveyDetailView.as_view()


@login_required
def take_survey(request, pk):
    """Take a survey"""
    survey = get_object_or_404(Survey, pk=pk)
    user = request.user
    
    # Check if user can take this survey
    if not (user.role == survey.target_role or survey.target_role == "all"):
        messages.error(request, "You are not eligible to take this survey.")
        return redirect('surveys:detail', pk=pk)
    
    # Check if survey is active and not expired
    if not survey.is_active:
        messages.error(request, "This survey is not currently available.")
        return redirect('surveys:detail', pk=pk)
    
    # Check if survey has expired (only if end_date is set)
    if survey.end_date and survey.end_date < timezone.now():
        messages.error(request, "This survey has expired.")
        return redirect('surveys:detail', pk=pk)
    
    # Check if user has already responded
    if SurveyResponse.objects.filter(survey=survey, respondent=user).exists():
        messages.info(request, "You have already completed this survey.")
        return redirect('surveys:detail', pk=pk)
    
    if request.method == 'POST':
        # Process survey response
        responses = {}
        questions = survey.questions
        
        for question in questions:
            question_id = str(question['id'])
            response_value = None
            
            if question['type'] == 'multiple_choice':
                response_value = request.POST.get(f'question_{question_id}')
            elif question['type'] == 'checkbox':
                response_value = request.POST.getlist(f'question_{question_id}')
            elif question['type'] in ['text', 'textarea', 'email', 'number']:
                response_value = request.POST.get(f'question_{question_id}')
            elif question['type'] == 'rating':
                response_value = request.POST.get(f'question_{question_id}')
            elif question['type'] == 'yes_no':
                response_value = request.POST.get(f'question_{question_id}')
            
            # Validate required questions
            if question.get('required', False) and not response_value:
                messages.error(request, f"Please answer the required question: {question['question']}")
                return render(request, 'surveys/take_survey.html', {
                    'survey': survey,
                    'questions': questions
                })
            
            if response_value:
                responses[question_id] = response_value
        
        # Save response
        survey_response = SurveyResponse.objects.create(
            survey=survey,
            respondent=user,
            answers=responses,
            is_complete=True
        )
        
        # Update analytics
        SurveyAnalytics.objects.update_or_create(
            survey=survey,
            defaults={
                'total_responses': survey.responses.count(),
                'completion_rate': calculate_completion_rate(survey),
                'avg_completion_time': calculate_average_time(survey),
                'last_calculated': timezone.now()
            }
        )
        
        messages.success(request, "Thank you for completing the survey!")
        return redirect('surveys:detail', pk=pk)
    
    context = {
        'survey': survey,
        'questions': survey.questions
    }
    
    return render(request, 'surveys/take_survey.html', context)


class SurveyCreateView(LoginRequiredMixin, SurveyAccessMixin, CreateView):
    """Create a new survey"""
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'
    success_url = reverse_lazy('surveys:list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        # Parse questions from form data
        questions_json = self.request.POST.get('questions_json')
        if questions_json:
            try:
                questions = json.loads(questions_json)
                form.instance.questions = questions
            except json.JSONDecodeError:
                messages.error(self.request, "Invalid question format.")
                return self.form_invalid(form)
        
        messages.success(self.request, f'Survey "{form.instance.title}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Survey'
        context['button_text'] = 'Create Survey'
        return context


survey_create = SurveyCreateView.as_view()


class SurveyEditView(LoginRequiredMixin, SurveyAccessMixin, UpdateView):
    """Edit an existing survey"""
    model = Survey
    form_class = SurveyForm
    template_name = 'surveys/survey_form.html'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Survey.objects.all()
        else:
            return Survey.objects.filter(created_by=user)
    
    def get_success_url(self):
        return reverse_lazy('surveys:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        # Parse questions from form data
        questions_json = self.request.POST.get('questions_json')
        if questions_json:
            try:
                questions = json.loads(questions_json)
                form.instance.questions = questions
            except json.JSONDecodeError:
                messages.error(self.request, "Invalid question format.")
                return self.form_invalid(form)
        
        messages.success(self.request, f'Survey "{form.instance.title}" updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Survey'
        context['button_text'] = 'Update Survey'
        context['existing_questions'] = json.dumps(self.object.questions)
        return context


survey_edit = SurveyEditView.as_view()


@login_required
def survey_analytics(request, pk):
    """Survey analytics and results"""
    survey = get_object_or_404(Survey, pk=pk)
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user == survey.created_by):
        messages.error(request, "You don't have permission to view survey analytics.")
        return redirect('surveys:detail', pk=pk)
    
    # Get all responses
    responses = SurveyResponse.objects.filter(survey=survey).select_related('respondent')
    
    # Basic statistics
    total_responses = responses.count()
    
    # Calculate target users based on survey target_role
    if survey.target_role == 'all':
        target_users = User.objects.count()
    else:
        target_users = User.objects.filter(role=survey.target_role).count()
    
    completion_rate = round((total_responses / target_users) * 100, 1) if target_users > 0 else 0
    
    # Question-wise analysis
    question_analytics = []
    for question in survey.questions:
        question_id = str(question['id'])
        question_responses = []
        
        for response in responses:
            if question_id in response.answers:
                question_responses.append(response.answers[question_id])
        
        # Analyze based on question type
        analysis = analyze_question_responses(question, question_responses)
        question_analytics.append({
            'question': question,
            'analysis': analysis,
            'response_count': len(question_responses)
        })
    
    # Response timeline
    response_timeline = []
    if responses.exists():
        start_date = survey.start_date or survey.created_at.date()
        end_date = survey.end_date.date() if survey.end_date else timezone.now().date()
        
        current_date = start_date
        while current_date <= end_date:
            daily_responses = responses.filter(
                created_at__date=current_date
            ).count()
            response_timeline.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'responses': daily_responses
            })
            current_date += timedelta(days=1)
    
    context = {
        'survey': survey,
        'total_responses': total_responses,
        'target_users': target_users,
        'completion_rate': completion_rate,
        'question_analytics': question_analytics,
        'response_timeline': response_timeline,
        'recent_responses': responses.order_by('-created_at')[:10]
    }
    
    return render(request, 'surveys/survey_analytics.html', context)


@login_required
def export_survey_results(request, pk):
    """Export survey results as CSV"""
    survey = get_object_or_404(Survey, pk=pk)
    user = request.user
    
    # Check permissions
    if not (user.is_admin or user == survey.created_by):
        messages.error(request, "You don't have permission to export survey results.")
        return redirect('surveys:detail', pk=pk)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="survey_{survey.id}_results.csv"'
    
    writer = csv.writer(response)
    
    # Header row
    header = ['Response ID', 'User', 'Role', 'Completed At']
    for question in survey.questions:
        header.append(f"Q{question['id']}: {question['question']}")
    writer.writerow(header)
    
    # Data rows
    for survey_response in survey.responses.select_related('respondent'):
        row = [
            survey_response.id,
            survey_response.respondent.get_full_name() if survey_response.respondent else 'Anonymous',
            survey_response.respondent.get_role_display() if survey_response.respondent else 'Anonymous',
            survey_response.created_at.strftime('%Y-%m-%d %H:%M')
        ]
        
        for question in survey.questions:
            question_id = str(question['id'])
            response_value = survey_response.answers.get(question_id, '')
            if isinstance(response_value, list):
                response_value = ', '.join(response_value)
            row.append(response_value)
        
        writer.writerow(row)
    
    return response


def analyze_question_responses(question, responses):
    """Analyze responses for a specific question"""
    question_type = question['type']
    analysis = {}
    
    if question_type == 'multiple_choice':
        # Count occurrences of each option
        option_counts = {}
        total_responses = len(responses)
        
        for response in responses:
            if response in option_counts:
                option_counts[response] += 1
            else:
                option_counts[response] = 1
        
        # Calculate percentages
        analysis['type'] = 'multiple_choice'
        analysis['options'] = []
        for option in question.get('options', []):
            count = option_counts.get(option, 0)
            percentage = round((count / total_responses) * 100, 1) if total_responses > 0 else 0
            analysis['options'].append({
                'text': option,
                'count': count,
                'percentage': percentage
            })
    
    elif question_type == 'checkbox':
        # Count occurrences of each option
        option_counts = {}
        total_responses = len(responses)
        
        for response in responses:
            if isinstance(response, list):
                for option in response:
                    if option in option_counts:
                        option_counts[option] += 1
                    else:
                        option_counts[option] = 1
        
        analysis['type'] = 'checkbox'
        analysis['options'] = []
        for option in question.get('options', []):
            count = option_counts.get(option, 0)
            percentage = round((count / total_responses) * 100, 1) if total_responses > 0 else 0
            analysis['options'].append({
                'text': option,
                'count': count,
                'percentage': percentage
            })
    
    elif question_type == 'rating':
        # Calculate average rating and distribution
        ratings = []
        for response in responses:
            try:
                rating = int(response)
                ratings.append(rating)
            except (ValueError, TypeError):
                continue
        
        if ratings:
            analysis['type'] = 'rating'
            analysis['average'] = round(sum(ratings) / len(ratings), 1)
            analysis['total_responses'] = len(ratings)
            
            # Rating distribution
            rating_counts = {}
            for rating in ratings:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            
            analysis['distribution'] = []
            for i in range(1, 6):  # Assuming 1-5 rating scale
                count = rating_counts.get(i, 0)
                percentage = round((count / len(ratings)) * 100, 1)
                analysis['distribution'].append({
                    'rating': i,
                    'count': count,
                    'percentage': percentage
                })
    
    elif question_type in ['text', 'textarea']:
        # Text analysis - just count responses
        analysis['type'] = 'text'
        analysis['total_responses'] = len([r for r in responses if r.strip()])
        analysis['responses'] = responses[:10]  # Show first 10 responses
    
    return analysis


def calculate_completion_rate(survey):
    """Calculate completion rate for a survey"""
    total_responses = survey.responses.count()
    target_users = User.objects.filter(role__in=survey.target_role).count()
    return round((total_responses / target_users) * 100, 1) if target_users > 0 else 0


def calculate_average_time(survey):
    """Calculate average time to complete survey"""
    # This would require storing start time as well
    # For now, return a placeholder
    return 5  # minutes
