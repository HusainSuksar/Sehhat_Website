from django.urls import path
from . import views

app_name = 'mahalshifa'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
