from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def dashboard(request):
    """mahalshifa dashboard view"""
    return HttpResponse("<h1>mahalshifa Dashboard</h1><p>Coming soon...</p>")
