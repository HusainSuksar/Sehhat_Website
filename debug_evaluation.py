#!/usr/bin/env python3
"""
Debug script to check EvaluationForm with ID 22
"""

import os
import sys
import django
from django.db.models import Q

# Add the project directory to the Python path
sys.path.append('/workspace')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from evaluation.models import EvaluationForm
from accounts.models import User

def debug_evaluation_form():
    """Debug the EvaluationForm with ID 22"""
    
    print("=== EvaluationForm Debug ===")
    
    # Check if form 22 exists
    try:
        form = EvaluationForm.objects.get(id=22)
        print(f"✅ Form 22 exists: {form.title}")
        print(f"   - Created by: {form.created_by}")
        print(f"   - Target role: {form.target_role}")
        print(f"   - Is active: {form.is_active}")
        print(f"   - Created at: {form.created_at}")
    except EvaluationForm.DoesNotExist:
        print("❌ Form 22 does not exist!")
        
        # Show all available forms
        forms = EvaluationForm.objects.all()
        print(f"\nAvailable forms ({forms.count()} total):")
        for form in forms:
            print(f"   - ID {form.id}: {form.title} (created by {form.created_by}, target: {form.target_role})")
    
    # Check user permissions
    print("\n=== User Permissions Debug ===")
    
    # Get all users and their roles
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    
    for user in users:
        print(f"   - {user.username}: role={user.role}, is_admin={user.is_admin}")
    
    # Test queryset filtering for different user types
    print("\n=== Queryset Filtering Test ===")
    
    for user in users[:5]:  # Test first 5 users
        print(f"\nTesting user: {user.username} (role: {user.role})")
        
        if user.is_admin:
            queryset = EvaluationForm.objects.all()
        elif user.role == 'aamil' or user.role == 'moze_coordinator':
            queryset = EvaluationForm.objects.filter(
                Q(created_by=user) | Q(target_role="moze_coordinator") | Q(target_role="aamil")
            )
        else:
            queryset = EvaluationForm.objects.filter(
                Q(target_role="student") | Q(created_by=user)
            )
        
        print(f"   Forms visible to {user.username}: {queryset.count()}")
        form_ids = list(queryset.values_list('id', flat=True))
        print(f"   Form IDs: {form_ids}")
        
        if 22 in form_ids:
            print(f"   ✅ User {user.username} CAN see form 22")
        else:
            print(f"   ❌ User {user.username} CANNOT see form 22")

if __name__ == "__main__":
    debug_evaluation_form()