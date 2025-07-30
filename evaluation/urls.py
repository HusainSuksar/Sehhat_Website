from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Evaluation Form URLs (only existing views)
    path('forms/', views.EvaluationFormListView.as_view(), name='form_list'),
    path('forms/<int:pk>/', views.EvaluationFormDetailView.as_view(), name='form_detail'),
    path('forms/create/', views.EvaluationFormCreateView.as_view(), name='form_create'),
    path('forms/<int:pk>/update/', views.EvaluationFormUpdateView.as_view(), name='form_update'),
    
    # Evaluation actions (only existing views)
    path('forms/<int:pk>/evaluate/', views.evaluate_form, name='evaluate_form'),
    
    # Submission management (only existing views)
    path('submissions/<int:pk>/', views.submission_detail, name='submission_detail'),
    
    # Analytics and reports (only existing views)
    path('analytics/', views.evaluation_analytics, name='analytics'),
    path('export/', views.export_evaluations, name='export_evaluations'),
    
    # Session management (only existing views)
    path('sessions/create/', views.create_evaluation_session, name='create_session'),
    
    # User-specific views (only existing views)
    path('my-evaluations/', views.my_evaluations, name='my_evaluations'),
]
