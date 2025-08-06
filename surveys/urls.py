from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Dashboard and main views
    path('', views.survey_dashboard, name='dashboard'),
    path('list/', views.SurveyListView.as_view(), name='list'),
    path('<int:pk>/', views.SurveyDetailView.as_view(), name='detail'),
    
    # Survey management
    path('create/', views.SurveyCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.SurveyEditView.as_view(), name='edit'),
    path('manage/', views.SurveyListView.as_view(), name='manage'),
    
    # Taking surveys
    path('<int:pk>/take/', views.take_survey, name='take_survey'),
    
    # Analytics and reports
    path('<int:pk>/analytics/', views.survey_analytics, name='analytics'),
    path('<int:pk>/export/', views.export_survey_results, name='export_results'),
]
