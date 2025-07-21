from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def dashboard(request):
    """Moze dashboard view"""
    return HttpResponse("<h1>Moze Dashboard</h1><p>Coming soon...</p>")

@login_required
def moze_list(request):
    """List all mozes"""
    return HttpResponse("<h1>Moze List</h1><p>Coming soon...</p>")

@login_required
def moze_detail(request, pk):
    """Moze detail view"""
    return HttpResponse(f"<h1>Moze Detail {pk}</h1><p>Coming soon...</p>")

@login_required
def moze_create(request):
    """Create new moze"""
    return HttpResponse("<h1>Create Moze</h1><p>Coming soon...</p>")

@login_required
def moze_edit(request, pk):
    """Edit moze"""
    return HttpResponse(f"<h1>Edit Moze {pk}</h1><p>Coming soon...</p>")
