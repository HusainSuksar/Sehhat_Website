from django.urls import path
from . import views

app_name = 'araz'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
