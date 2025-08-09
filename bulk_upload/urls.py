from django.urls import path
from . import views

app_name = 'bulk_upload'

urlpatterns = [
    # Main bulk upload views
    path('', views.BulkUploadListView.as_view(), name='list'),
    path('create/', views.bulk_upload_create, name='create'),
    path('<int:pk>/', views.BulkUploadDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', views.bulk_upload_delete, name='delete'),
    
    # Processing and preview
    path('<int:pk>/process/', views.bulk_upload_process, name='process'),
    path('<int:pk>/preview/', views.bulk_upload_preview, name='preview'),
    path('<int:pk>/status/', views.bulk_upload_api_status, name='status'),
    
    # Templates
    path('template/<str:upload_type>/', views.download_template, name='template'),
]