from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def dashboard(request):
    """araz dashboard view"""
    return HttpResponse("<h1>araz Dashboard</h1><p>Coming soon...</p>")
