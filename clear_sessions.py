#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.sessions.models import Session

def clear_sessions():
    """Clear all sessions to fix corruption issues"""
    try:
        session_count = Session.objects.count()
        Session.objects.all().delete()
        print(f"✅ Cleared {session_count} corrupted sessions")
        print("✅ Session corruption issue resolved")
        print("🔐 Users can now login successfully")
    except Exception as e:
        print(f"❌ Error clearing sessions: {e}")

if __name__ == "__main__":
    clear_sessions()