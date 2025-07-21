from django.urls import path
from . import views

app_name = 'surveys'

urlpatterns = [
    # Dashboard and main views
    path('', views.survey_dashboard, name='dashboard'),
    path('list/', views.survey_list, name='list'),
    path('<int:pk>/', views.survey_detail, name='detail'),
    
    # Survey management
    path('create/', views.survey_create, name='create'),
    path('<int:pk>/edit/', views.survey_edit, name='edit'),
    
    # Taking surveys
    path('<int:pk>/take/', views.take_survey, name='take_survey'),
    
    # Analytics and reports
    path('<int:pk>/analytics/', views.survey_analytics, name='analytics'),
    path('<int:pk>/export/', views.export_survey_results, name='export_results'),
]
