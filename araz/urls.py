from django.urls import path
from . import views

app_name = 'araz'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Araz URLs (updated from petition)
    path('araiz/', views.PetitionListView.as_view(), name='araz_list'),
    path('araiz/<int:pk>/', views.PetitionDetailView.as_view(), name='araz_detail'),
    path('araiz/create/', views.PetitionCreateView.as_view(), name='araz_create'),
    path('araiz/<int:pk>/edit/', views.PetitionUpdateView.as_view(), name='araz_update'),
    
    # Araz actions (updated from petition)
    path('araiz/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('araiz/<int:pk>/assign/', views.assign_petition, name='assign_araz'),
    path('araiz/<int:pk>/status/', views.update_petition_status, name='update_status'),
    
    # Analytics and reports
    path('analytics/', views.petition_analytics, name='analytics'),
    path('export/', views.export_petitions, name='export_araiz'),
    
    # Bulk operations
    path('bulk-update/', views.bulk_update_status, name='bulk_update_status'),
    
    # User-specific views
    path('my-assignments/', views.my_assignments, name='my_assignments'),
    
    # Keep old petition URLs for backward compatibility
    path('petitions/', views.PetitionListView.as_view(), name='petition_list'),
    path('petitions/<int:pk>/', views.PetitionDetailView.as_view(), name='petition_detail'),
    path('petitions/create/', views.PetitionCreateView.as_view(), name='petition_create'),
    path('petitions/<int:pk>/edit/', views.PetitionUpdateView.as_view(), name='petition_update'),
]
