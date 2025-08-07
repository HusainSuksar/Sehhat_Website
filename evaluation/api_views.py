"""
API Views for the Evaluation app
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils import timezone

from .models import (
    EvaluationCriteria, EvaluationAnswerOption, EvaluationForm, EvaluationSubmission,
    EvaluationResponse, EvaluationSession, CriteriaRating, Evaluation,
    EvaluationTemplate, TemplateCriteria, EvaluationReport, EvaluationHistory
)
from .serializers import (
    EvaluationCriteriaSerializer, EvaluationAnswerOptionSerializer, EvaluationFormSerializer,
    EvaluationSubmissionSerializer, EvaluationResponseSerializer, EvaluationSessionSerializer,
    CriteriaRatingSerializer, EvaluationSerializer, EvaluationCreateSerializer,
    EvaluationTemplateSerializer, TemplateCriteriaSerializer, EvaluationReportSerializer,
    EvaluationHistorySerializer, EvaluationStatsSerializer, CriteriaStatsSerializer,
    EvaluationSearchSerializer
)


# Custom Permission Classes
class IsAdminOrEvaluator(permissions.BasePermission):
    """
    Permission for admins and authorized evaluators to manage evaluations
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_admin or 
                 request.user.role in ['aamil', 'moze_coordinator', 'doctor']))


class IsEvaluationStaffOrAdmin(permissions.BasePermission):
    """
    Permission for evaluation staff (admin, aamil, coordinators, doctors) and admins
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Admin can access everything
        if user.is_admin or user.is_superuser:
            return True
        
        # Get the evaluation or related object
        if hasattr(obj, 'evaluator'):
            # For Evaluation, EvaluationSubmission objects
            return obj.evaluator == user or user.role in ['aamil', 'moze_coordinator']
        elif hasattr(obj, 'created_by'):
            # For EvaluationForm, EvaluationTemplate, etc.
            return obj.created_by == user or user.role in ['aamil', 'moze_coordinator']
        elif hasattr(obj, 'moze'):
            # For objects related to Moze
            moze = obj.moze
            return (moze.aamil == user or 
                   moze.moze_coordinator == user or 
                   user in moze.team_members.all())
        
        return False


# Access Control Mixins
class EvaluationAccessMixin:
    """
    Mixin to filter evaluation data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            # Admin can see all evaluations
            return Evaluation.objects.all()
        elif user.role == 'aamil':
            # Aamil can see evaluations for their Mozes
            return Evaluation.objects.filter(moze__aamil=user)
        elif user.role == 'moze_coordinator':
            # Coordinator can see evaluations for their Mozes
            return Evaluation.objects.filter(moze__moze_coordinator=user)
        elif user.role == 'doctor':
            # Doctors can see evaluations they conducted or for Mozes they're associated with
            return Evaluation.objects.filter(
                Q(evaluator=user) |
                Q(moze__team_members=user) |
                Q(moze__umoor_teams__member=user, moze__umoor_teams__is_active=True)
            ).distinct()
        else:
            # Regular users can only see evaluations they conducted
            return Evaluation.objects.filter(evaluator=user)


class FormAccessMixin:
    """
    Mixin to filter form data based on user role
    """
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationForm.objects.all()
        elif user.role in ['aamil', 'moze_coordinator', 'doctor']:
            # Staff can see all active forms plus ones they created
            return EvaluationForm.objects.filter(
                Q(is_active=True) | Q(created_by=user)
            ).distinct()
        else:
            # Regular users can see forms targeted to them or all users
            return EvaluationForm.objects.filter(
                is_active=True,
                target_role__in=['all', user.role]
            )


# Evaluation Criteria API Views
class EvaluationCriteriaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationCriteriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'question_type', 'is_active', 'is_required']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'weight', 'order', 'created_at']
    ordering = ['category', 'order', 'name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            return EvaluationCriteria.objects.all()
        else:
            # Regular users can only see active criteria
            return EvaluationCriteria.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrEvaluator()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class EvaluationCriteriaDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationCriteriaSerializer
    permission_classes = [IsEvaluationStaffOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            return EvaluationCriteria.objects.all()
        else:
            return EvaluationCriteria.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrEvaluator()]
        return super().get_permissions()


# Evaluation Answer Options API Views
class EvaluationAnswerOptionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationAnswerOptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['criteria', 'is_active']
    ordering_fields = ['criteria', 'order', 'weight']
    ordering = ['criteria', 'order']
    
    def get_queryset(self):
        return EvaluationAnswerOption.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrEvaluator()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save()


class EvaluationAnswerOptionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationAnswerOptionSerializer
    permission_classes = [IsAdminOrEvaluator]
    queryset = EvaluationAnswerOption.objects.all()


# Evaluation Form API Views
class EvaluationFormListCreateAPIView(FormAccessMixin, generics.ListCreateAPIView):
    serializer_class = EvaluationFormSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['evaluation_type', 'target_role', 'is_active', 'is_anonymous']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'due_date']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrEvaluator()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EvaluationFormDetailAPIView(FormAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationFormSerializer
    permission_classes = [IsEvaluationStaffOrAdmin]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrEvaluator()]
        return super().get_permissions()


# Evaluation Submission API Views
class EvaluationSubmissionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['form', 'is_complete', 'target_moze', 'target_user']
    search_fields = ['comments']
    ordering_fields = ['submitted_at', 'total_score']
    ordering = ['-submitted_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationSubmission.objects.all()
        elif user.role in ['aamil', 'moze_coordinator']:
            # Staff can see submissions related to their Mozes
            return EvaluationSubmission.objects.filter(
                Q(evaluator=user) |
                Q(target_moze__aamil=user) |
                Q(target_moze__moze_coordinator=user)
            ).distinct()
        else:
            # Users can see their own submissions
            return EvaluationSubmission.objects.filter(evaluator=user)
    
    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)


class EvaluationSubmissionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationSubmissionSerializer
    permission_classes = [IsEvaluationStaffOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationSubmission.objects.all()
        else:
            return EvaluationSubmission.objects.filter(
                Q(evaluator=user) |
                Q(target_moze__aamil=user) |
                Q(target_moze__moze_coordinator=user)
            ).distinct()


# Evaluation Response API Views
class EvaluationResponseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['submission', 'criteria']
    ordering_fields = ['created_at', 'score']
    ordering = ['created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationResponse.objects.all()
        else:
            # Users can see responses for submissions they have access to
            return EvaluationResponse.objects.filter(submission__evaluator=user)
    
    def perform_create(self, serializer):
        submission = serializer.validated_data.get('submission')
        if submission and submission.evaluator != self.request.user:
            raise PermissionDenied("You can only add responses to your own submissions.")
        serializer.save()


class EvaluationResponseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationResponse.objects.all()
        else:
            return EvaluationResponse.objects.filter(submission__evaluator=user)


# Evaluation Session API Views
class EvaluationSessionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['form', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'start_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            return EvaluationSession.objects.all()
        else:
            # Regular users see active sessions
            return EvaluationSession.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrEvaluator()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EvaluationSessionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationSessionSerializer
    permission_classes = [IsEvaluationStaffOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            return EvaluationSession.objects.all()
        else:
            return EvaluationSession.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrEvaluator()]
        return super().get_permissions()


# Main Evaluation API Views
class EvaluationListCreateAPIView(EvaluationAccessMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'moze', 'evaluation_period', 'overall_grade', 'certification_status',
        'is_draft', 'is_published', 'is_confidential'
    ]
    search_fields = ['moze__name', 'strengths', 'weaknesses', 'recommendations']
    ordering_fields = ['evaluation_date', 'overall_score', 'created_at']
    ordering = ['-evaluation_date', '-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EvaluationCreateSerializer
        return EvaluationSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrEvaluator()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Set evaluator to current user if not provided
        if 'evaluator' not in serializer.validated_data:
            serializer.save(evaluator=self.request.user)
        else:
            serializer.save()


class EvaluationDetailAPIView(EvaluationAccessMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationSerializer
    permission_classes = [IsEvaluationStaffOrAdmin]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrEvaluator()]
        return super().get_permissions()


# Evaluation Template API Views
class EvaluationTemplateListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['evaluation_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            return EvaluationTemplate.objects.all()
        else:
            # Regular users see active templates
            return EvaluationTemplate.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrEvaluator()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EvaluationTemplateDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationTemplateSerializer
    permission_classes = [IsEvaluationStaffOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.role in ['aamil', 'moze_coordinator']:
            return EvaluationTemplate.objects.all()
        else:
            return EvaluationTemplate.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrEvaluator()]
        return super().get_permissions()


# Evaluation Report API Views
class EvaluationReportListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = EvaluationReportSerializer
    permission_classes = [IsAdminOrEvaluator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_published']
    search_fields = ['title', 'summary']
    ordering_fields = ['title', 'generated_at']
    ordering = ['-generated_at']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationReport.objects.all()
        else:
            # Users can see published reports and ones they generated
            return EvaluationReport.objects.filter(
                Q(is_published=True) | Q(generated_by=user)
            )
    
    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)


class EvaluationReportDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EvaluationReportSerializer
    permission_classes = [IsAdminOrEvaluator]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            return EvaluationReport.objects.all()
        else:
            return EvaluationReport.objects.filter(
                Q(is_published=True) | Q(generated_by=user)
            )


# Evaluation History API Views
class EvaluationHistoryListAPIView(generics.ListAPIView):
    serializer_class = EvaluationHistorySerializer
    permission_classes = [IsAdminOrEvaluator]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['evaluation', 'field_name', 'changed_by']
    ordering_fields = ['changed_at']
    ordering = ['-changed_at']
    
    def get_queryset(self):
        return EvaluationHistory.objects.all()


# Search API Views
class EvaluationSearchAPIView(generics.ListAPIView):
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering = ['-evaluation_date']
    
    def get_queryset(self):
        # Use EvaluationAccessMixin logic
        user = self.request.user
        
        if user.is_admin or user.is_superuser:
            queryset = Evaluation.objects.all()
        elif user.role == 'aamil':
            queryset = Evaluation.objects.filter(moze__aamil=user)
        elif user.role == 'moze_coordinator':
            queryset = Evaluation.objects.filter(moze__moze_coordinator=user)
        elif user.role == 'doctor':
            queryset = Evaluation.objects.filter(
                Q(evaluator=user) |
                Q(moze__team_members=user) |
                Q(moze__umoor_teams__member=user, moze__umoor_teams__is_active=True)
            ).distinct()
        else:
            queryset = Evaluation.objects.filter(evaluator=user)
        
        # Apply search filters from query params directly
        moze_name = self.request.query_params.get('moze_name')
        evaluator = self.request.query_params.get('evaluator')
        evaluation_period = self.request.query_params.get('evaluation_period')
        overall_grade = self.request.query_params.get('overall_grade')
        certification_status = self.request.query_params.get('certification_status')
        is_published = self.request.query_params.get('is_published')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if moze_name:
            queryset = queryset.filter(moze__name__icontains=moze_name)
        if evaluator:
            queryset = queryset.filter(
                Q(evaluator__first_name__icontains=evaluator) |
                Q(evaluator__last_name__icontains=evaluator) |
                Q(evaluator__username__icontains=evaluator)
            )
        if evaluation_period:
            queryset = queryset.filter(evaluation_period=evaluation_period)
        if overall_grade:
            queryset = queryset.filter(overall_grade=overall_grade)
        if certification_status:
            queryset = queryset.filter(certification_status=certification_status)
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == 'true')
        if date_from:
            queryset = queryset.filter(evaluation_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(evaluation_date__lte=date_to)
        
        return queryset.distinct().order_by('-evaluation_date')


# Statistics API Views
@api_view(['GET'])
@permission_classes([IsAdminOrEvaluator])
def evaluation_stats_api(request):
    """Get evaluation statistics"""
    user = request.user
    
    # Base queryset based on user role
    if user.is_admin or user.is_superuser:
        evaluations = Evaluation.objects.all()
    elif user.role == 'aamil':
        evaluations = Evaluation.objects.filter(moze__aamil=user)
    elif user.role == 'moze_coordinator':
        evaluations = Evaluation.objects.filter(moze__moze_coordinator=user)
    else:
        evaluations = Evaluation.objects.filter(evaluator=user)
    
    # Calculate stats
    total_evaluations = evaluations.count()
    published_evaluations = evaluations.filter(is_published=True).count()
    draft_evaluations = evaluations.filter(is_draft=True).count()
    
    # Evaluations by grade
    evaluations_by_grade = dict(
        evaluations.exclude(overall_grade__isnull=True)
        .values_list('overall_grade')
        .annotate(count=Count('id'))
    )
    
    # Evaluations by period
    evaluations_by_period = dict(
        evaluations.values_list('evaluation_period')
        .annotate(count=Count('id'))
    )
    
    # Average overall score
    avg_score = evaluations.filter(overall_score__gt=0).aggregate(
        avg=Avg('overall_score')
    )['avg'] or 0
    
    # Mozes needing attention
    mozes_needing_attention = evaluations.filter(
        Q(overall_grade__in=['D', 'E']) | Q(safety_score__lt=60)
    ).values('moze').distinct().count()
    
    stats = {
        'total_evaluations': total_evaluations,
        'published_evaluations': published_evaluations,
        'draft_evaluations': draft_evaluations,
        'evaluations_by_grade': evaluations_by_grade,
        'evaluations_by_period': evaluations_by_period,
        'average_overall_score': round(avg_score, 2),
        'mozes_needing_attention': mozes_needing_attention
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAdminOrEvaluator])
def criteria_stats_api(request):
    """Get criteria statistics"""
    criteria = EvaluationCriteria.objects.all()
    
    # Calculate stats
    total_criteria = criteria.count()
    active_criteria = criteria.filter(is_active=True).count()
    
    # Criteria by category
    criteria_by_category = dict(
        criteria.values_list('category')
        .annotate(count=Count('id'))
    )
    
    # Criteria by type
    criteria_by_type = dict(
        criteria.values_list('question_type')
        .annotate(count=Count('id'))
    )
    
    # Average weight
    avg_weight = criteria.aggregate(avg=Avg('weight'))['avg'] or 0
    
    stats = {
        'total_criteria': total_criteria,
        'active_criteria': active_criteria,
        'criteria_by_category': criteria_by_category,
        'criteria_by_type': criteria_by_type,
        'average_weight': round(avg_weight, 2)
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def evaluation_dashboard_api(request):
    """Get comprehensive dashboard data for evaluation app"""
    user = request.user
    
    if not user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
    dashboard_data = {}
    
    try:
        # Role-specific dashboard data
        if user.is_admin or user.role in ['aamil', 'moze_coordinator', 'doctor']:
            # Staff dashboard - compute stats directly
            if user.is_admin or user.is_superuser:
                evaluations = Evaluation.objects.all()
                forms = EvaluationForm.objects.all()
                criteria = EvaluationCriteria.objects.all()
            elif user.role == 'aamil':
                evaluations = Evaluation.objects.filter(moze__aamil=user)
                forms = EvaluationForm.objects.filter(
                    Q(created_by=user) | Q(is_active=True)
                ).distinct()
                criteria = EvaluationCriteria.objects.filter(is_active=True)
            elif user.role == 'moze_coordinator':
                evaluations = Evaluation.objects.filter(moze__moze_coordinator=user)
                forms = EvaluationForm.objects.filter(
                    Q(created_by=user) | Q(is_active=True)
                ).distinct()
                criteria = EvaluationCriteria.objects.filter(is_active=True)
            elif user.role == 'doctor':
                evaluations = Evaluation.objects.filter(
                    Q(evaluator=user) |
                    Q(moze__team_members=user) |
                    Q(moze__umoor_teams__member=user, moze__umoor_teams__is_active=True)
                ).distinct()
                forms = EvaluationForm.objects.filter(is_active=True)
                criteria = EvaluationCriteria.objects.filter(is_active=True)
            
            # Evaluation stats
            dashboard_data['evaluation_stats'] = {
                'total_evaluations': evaluations.count(),
                'published_evaluations': evaluations.filter(is_published=True).count(),
                'draft_evaluations': evaluations.filter(is_draft=True).count(),
                'average_score': round(
                    evaluations.filter(overall_score__gt=0).aggregate(avg=Avg('overall_score'))['avg'] or 0, 2
                ),
                'evaluations_needing_attention': evaluations.filter(
                    Q(overall_grade__in=['D', 'E']) | Q(safety_score__lt=60)
                ).count()
            }
            
            # Form stats
            dashboard_data['form_stats'] = {
                'total_forms': forms.count(),
                'active_forms': forms.filter(is_active=True).count(),
                'overdue_forms': forms.filter(
                    due_date__lt=timezone.now(), is_active=True
                ).count(),
                'forms_by_type': dict(forms.values_list('evaluation_type').annotate(count=Count('id')))
            }
            
            # Recent activities
            dashboard_data['recent_evaluations'] = EvaluationSerializer(
                evaluations.order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['recent_forms'] = EvaluationFormSerializer(
                forms.filter(is_active=True).order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
        else:
            # Regular user dashboard
            user_submissions = EvaluationSubmission.objects.filter(evaluator=user)
            available_forms = EvaluationForm.objects.filter(
                is_active=True,
                target_role__in=['all', user.role]
            )
            
            dashboard_data['my_submissions'] = EvaluationSubmissionSerializer(
                user_submissions.order_by('-submitted_at')[:10],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['available_forms'] = EvaluationFormSerializer(
                available_forms.order_by('-created_at')[:5],
                many=True, context={'request': request}
            ).data
            
            dashboard_data['submission_stats'] = {
                'total_submissions': user_submissions.count(),
                'completed_submissions': user_submissions.filter(is_complete=True).count(),
                'average_score': round(
                    user_submissions.filter(total_score__gt=0).aggregate(avg=Avg('total_score'))['avg'] or 0, 2
                )
            }
        
        # Common data for all users
        dashboard_data['active_criteria_count'] = EvaluationCriteria.objects.filter(is_active=True).count()
        dashboard_data['active_forms_count'] = EvaluationForm.objects.filter(is_active=True).count()
        
    except Exception as e:
        dashboard_data['error'] = str(e)
    
    return Response(dashboard_data)