from django.urls import path
from . import views

app_name = 'moze'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('list/', views.MozeListView.as_view(), name='list'),
    path('<int:pk>/', views.MozeDetailView.as_view(), name='detail'),
    path('<int:moze_id>/profile/', views.moze_profile_dashboard, name='profile_dashboard'),
    
    # CRUD operations
    path('create/', views.MozeCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.MozeEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.moze_delete, name='delete'),
    
    # Comments
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    # Analytics and reports
    path('analytics/', views.moze_analytics, name='analytics'),
]