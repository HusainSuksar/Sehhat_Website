#!/usr/bin/env python3
"""
Database Management Utility for Umoor Sehhat on PythonAnywhere
This script helps with common database operations
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings_pythonanywhere')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def print_status(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def check_database_connection():
    """Check if database connection is working"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print_status("Database connection successful")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def show_database_info():
    """Display database information"""
    print_info("Database Information:")
    print(f"  Engine: {connection.settings_dict['ENGINE']}")
    print(f"  Name: {connection.settings_dict['NAME']}")
    print(f"  Host: {connection.settings_dict['HOST']}")
    print(f"  Port: {connection.settings_dict['PORT']}")
    
def count_users():
    """Count users by role"""
    print_info("User Statistics:")
    roles = ['badri_mahal_admin', 'student', 'doctor', 'aamil', 'moze_coordinator', 'user']
    
    for role in roles:
        count = User.objects.filter(role=role).count()
        print(f"  {role}: {count}")
    
    total = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    print(f"  Total Users: {total}")
    print(f"  Superusers: {superusers}")

def list_admin_users():
    """List all admin users"""
    print_info("Admin Users:")
    admins = User.objects.filter(role='badri_mahal_admin')
    
    if not admins:
        print("  No admin users found")
    else:
        for admin in admins:
            print(f"  - {admin.username} ({admin.first_name} {admin.last_name}) - {admin.email}")

def reset_test_users():
    """Reset test users"""
    print_info("Resetting test users...")
    
    # Delete non-superuser accounts
    deleted_count = User.objects.filter(is_superuser=False).count()
    User.objects.filter(is_superuser=False).delete()
    
    print_status(f"Deleted {deleted_count} test users")
    
    # Recreate test users
    from create_test_users import create_test_users, create_additional_test_data
    
    try:
        users = create_test_users()
        create_additional_test_data()
        print_status(f"Created {len(users)} new test users")
    except Exception as e:
        print_error(f"Failed to create test users: {e}")

def backup_database():
    """Create a database backup"""
    print_info("Creating database backup...")
    
    import subprocess
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    
    try:
        # This would work on a server with mysqldump
        # On PythonAnywhere, you'd use their backup tools
        print_info(f"Backup would be saved as: {backup_file}")
        print_info("On PythonAnywhere, use the MySQL console or backup tools in the dashboard")
    except Exception as e:
        print_error(f"Backup failed: {e}")

def show_recent_activity():
    """Show recent user activity"""
    print_info("Recent User Activity:")
    
    recent_users = User.objects.order_by('-last_login')[:10]
    
    for user in recent_users:
        last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
        print(f"  {user.username} ({user.role}) - Last login: {last_login}")

def main():
    """Main menu"""
    print("=" * 60)
    print("🗄️  UMOOR SEHHAT DATABASE MANAGEMENT UTILITY")
    print("=" * 60)
    
    if not check_database_connection():
        print_error("Cannot connect to database. Check your configuration.")
        sys.exit(1)
    
    while True:
        print("\n📋 Available Operations:")
        print("1. Show database info")
        print("2. Count users by role")
        print("3. List admin users")
        print("4. Reset test users")
        print("5. Show recent activity")
        print("6. Backup database")
        print("7. Run Django shell")
        print("8. Run migrations")
        print("9. Collect static files")
        print("0. Exit")
        
        choice = input("\nSelect an option (0-9): ").strip()
        
        if choice == '1':
            show_database_info()
        elif choice == '2':
            count_users()
        elif choice == '3':
            list_admin_users()
        elif choice == '4':
            confirm = input("⚠️  This will delete all test users. Continue? (y/N): ")
            if confirm.lower() == 'y':
                reset_test_users()
        elif choice == '5':
            show_recent_activity()
        elif choice == '6':
            backup_database()
        elif choice == '7':
            print_info("Starting Django shell...")
            execute_from_command_line(['manage.py', 'shell', '--settings=umoor_sehhat.settings_pythonanywhere'])
        elif choice == '8':
            print_info("Running migrations...")
            execute_from_command_line(['manage.py', 'migrate', '--settings=umoor_sehhat.settings_pythonanywhere'])
        elif choice == '9':
            print_info("Collecting static files...")
            execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--settings=umoor_sehhat.settings_pythonanywhere'])
        elif choice == '0':
            print_status("Goodbye!")
            break
        else:
            print_error("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()