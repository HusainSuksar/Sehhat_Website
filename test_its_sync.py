#!/usr/bin/env python
"""
Test script to verify ITS sync functionality
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from accounts.models import User, UserProfile
from accounts.services import MockITSService
from django.test import RequestFactory, Client
from django.contrib.auth import get_user
import pytest


@pytest.mark.django_db
def test_its_sync():
    """Test ITS sync functionality end-to-end"""
    # 1: Mock ITS Service
    its_service = MockITSService()
    test_its_id = '12345678'
    user_data = its_service.fetch_user_data(test_its_id)
    assert user_data is not None

    # 2: Create or get test user
    test_user, created = User.objects.get_or_create(
        its_id=test_its_id,
        defaults={
            'username': test_its_id,
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com'
        }
    )

    # 3: Apply sync data
    original_email = test_user.email
    original_mobile = test_user.mobile_number

    test_user.first_name = user_data.get('first_name', test_user.first_name)
    test_user.last_name = user_data.get('last_name', test_user.last_name)
    test_user.email = user_data.get('email', test_user.email)
    test_user.mobile_number = user_data.get('contact_number', test_user.mobile_number)
    test_user.address = user_data.get('address', test_user.address)
    test_user.gender = user_data.get('gender', test_user.gender)
    test_user.jamaat = user_data.get('jamaat', test_user.jamaat)
    test_user.occupation = user_data.get('occupation', test_user.occupation)
    test_user.save()

    # Create/update profile
    profile, _ = UserProfile.objects.get_or_create(user=test_user)
    if user_data.get('emergency_contact_name'):
        profile.emergency_contact_name = user_data.get('emergency_contact_name')
    if user_data.get('emergency_contact_number'):
        profile.emergency_contact = user_data.get('emergency_contact_number')
    if user_data.get('address'):
        profile.location = user_data.get('address')[:100]
    profile.save()

    # 4: Test sync view using client to handle CSRF/session
    from accounts.views import sync_its_data
    client = Client(enforce_csrf_checks=False)
    client.force_login(test_user)
    response = client.post('/accounts/sync-its-data/')
    assert response.status_code in (200, 302)
    if response.status_code == 200:
        response_data = json.loads(response.content)
        assert response_data.get('success') is True

    # 5: Verify final state
    test_user.refresh_from_db()
    profile.refresh_from_db()

    assert test_user.email != original_email or test_user.mobile_number != original_mobile
    assert profile.location is not None