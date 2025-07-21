from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def dashboard(request):
    """photos dashboard view"""
    return HttpResponse("<h1>photos Dashboard</h1><p>Coming soon...</p>")
