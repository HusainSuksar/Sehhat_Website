import requests
from django.core.management.base import BaseCommand
from accounts.models import User, UserProfile
from datetime import datetime

class Command(BaseCommand):
    help = 'Fetch users from ITS (Beeceptor) and populate User and UserProfile'

    def handle(self, *args, **kwargs):
        API_URL = 'https://umoorsehhat.free.beeceptor.com/users' # Replace with actual URL

        TOKEN = 'testtoken123'  # Or whatever you set in Beeceptor

        headers = {
            'Authorization': f'Bearer {TOKEN}',
            'Accept': 'application/json'
        }

        response = requests.get(API_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            for user_data in data.get('users', []):
                user, created = User.objects.update_or_create(
                    username=user_data['username'],
                    defaults={
                        'role': user_data.get('role'),
                        'its_id': user_data.get('its_id'),
                        'phone_number': user_data.get('phone_number'),
                        'profile_photo': user_data.get('profile_photo'),
                        'arabic_full_name': user_data.get('arabic_full_name'),
                        'age': user_data.get('age'),
                        'college': user_data.get('college'),
                        'specialization': user_data.get('specialization'),
                        # Do NOT set location or date_of_birth here
                    }
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.location = user_data.get('location')
                profile.date_of_birth = (
                    datetime.strptime(user_data['date_of_birth'], '%Y-%m-%d').date()
                    if user_data.get('date_of_birth') else None
                )
                profile.save()
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created user: {user.username}"))
                else:
                    self.stdout.write(f"Updated user: {user.username}")
        else:
            self.stdout.write(self.style.ERROR(f"Failed: {response.status_code} {response.text}"))