from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# Create your views here.

@login_required
def dashboard(request):
    """Doctor dashboard view"""
    return HttpResponse("<h1>Doctor Dashboard</h1><p>Coming soon...</p>")
