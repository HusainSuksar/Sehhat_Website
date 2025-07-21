from django.urls import path
from . import views

app_name = 'moze'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('list/', views.moze_list, name='list'),
    path('<int:pk>/', views.moze_detail, name='detail'),
    
    # CRUD operations
    path('create/', views.moze_create, name='create'),
    path('<int:pk>/edit/', views.moze_edit, name='edit'),
    path('<int:pk>/delete/', views.moze_delete, name='delete'),
    
    # Comments
    path('comment/<int:pk>/delete/', views.comment_delete, name='comment_delete'),
    
    # Analytics and reports
    path('analytics/', views.moze_analytics, name='analytics'),
]