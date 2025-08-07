"""
URL Configuration for the Evaluation API
"""
from django.urls import path
from . import api_views

urlpatterns = [
    # Dashboard
    path('dashboard/', api_views.evaluation_dashboard_api, name='evaluation_dashboard_api'),
    
    # Evaluation Criteria Management
    path('criteria/', api_views.EvaluationCriteriaListCreateAPIView.as_view(), name='criteria_list_create'),
    path('criteria/<int:pk>/', api_views.EvaluationCriteriaDetailAPIView.as_view(), name='criteria_detail'),
    
    # Answer Options Management
    path('answer-options/', api_views.EvaluationAnswerOptionListCreateAPIView.as_view(), name='answer_option_list_create'),
    path('answer-options/<int:pk>/', api_views.EvaluationAnswerOptionDetailAPIView.as_view(), name='answer_option_detail'),
    
    # Evaluation Forms Management
    path('forms/', api_views.EvaluationFormListCreateAPIView.as_view(), name='form_list_create'),
    path('forms/<int:pk>/', api_views.EvaluationFormDetailAPIView.as_view(), name='form_detail'),
    
    # Evaluation Submissions
    path('submissions/', api_views.EvaluationSubmissionListCreateAPIView.as_view(), name='submission_list_create'),
    path('submissions/<int:pk>/', api_views.EvaluationSubmissionDetailAPIView.as_view(), name='submission_detail'),
    
    # Evaluation Responses
    path('responses/', api_views.EvaluationResponseListCreateAPIView.as_view(), name='response_list_create'),
    path('responses/<int:pk>/', api_views.EvaluationResponseDetailAPIView.as_view(), name='response_detail'),
    
    # Evaluation Sessions
    path('sessions/', api_views.EvaluationSessionListCreateAPIView.as_view(), name='session_list_create'),
    path('sessions/<int:pk>/', api_views.EvaluationSessionDetailAPIView.as_view(), name='session_detail'),
    
    # Main Evaluations (Moze Evaluations)
    path('evaluations/', api_views.EvaluationListCreateAPIView.as_view(), name='evaluation_list_create'),
    path('evaluations/<int:pk>/', api_views.EvaluationDetailAPIView.as_view(), name='evaluation_detail'),
    path('evaluations/search/', api_views.EvaluationSearchAPIView.as_view(), name='evaluation_search'),
    
    # Evaluation Templates
    path('templates/', api_views.EvaluationTemplateListCreateAPIView.as_view(), name='template_list_create'),
    path('templates/<int:pk>/', api_views.EvaluationTemplateDetailAPIView.as_view(), name='template_detail'),
    
    # Evaluation Reports
    path('reports/', api_views.EvaluationReportListCreateAPIView.as_view(), name='report_list_create'),
    path('reports/<int:pk>/', api_views.EvaluationReportDetailAPIView.as_view(), name='report_detail'),
    
    # Evaluation History (Audit Trail)
    path('history/', api_views.EvaluationHistoryListAPIView.as_view(), name='history_list'),
    
    # Statistics
    path('stats/evaluations/', api_views.evaluation_stats_api, name='evaluation_stats_api'),
    path('stats/criteria/', api_views.criteria_stats_api, name='criteria_stats_api'),
]