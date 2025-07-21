from django.urls import path
from . import views

app_name = 'moze'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.moze_list, name='list'),
    path('<int:pk>/', views.moze_detail, name='detail'),
    path('create/', views.moze_create, name='create'),
    path('<int:pk>/edit/', views.moze_edit, name='edit'),
]