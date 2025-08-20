#!/usr/bin/env python
"""
Migration Fix Script for Windows
Resets database and creates fresh migrations
"""

import os
import sys
import shutil
import glob

def main():
    print("=" * 80)
    print("UMOOR SEHHAT - MIGRATION FIX SCRIPT")
    print("=" * 80)
    print("\nThis script will:")
    print("1. Backup your current database")
    print("2. Delete all migration files (keeping __init__.py)")
    print("3. Create a fresh database with new migrations")
    print("4. Generate test data")
    
    confirm = input("\nWARNING: This will delete your current database! Continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    # Step 1: Backup database
    print("\n[1/6] Backing up database...")
    if os.path.exists('db.sqlite3'):
        backup_name = 'db.sqlite3.backup'
        counter = 1
        while os.path.exists(backup_name):
            backup_name = f'db.sqlite3.backup{counter}'
            counter += 1
        shutil.copy2('db.sqlite3', backup_name)
        print(f"✓ Database backed up to {backup_name}")
    else:
        print("✓ No existing database found")
    
    # Step 2: Delete old database
    print("\n[2/6] Removing old database...")
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("✓ Old database removed")
    
    # Step 3: Delete migration files
    print("\n[3/6] Cleaning migration files...")
    apps = [
        'accounts', 'moze', 'mahalshifa', 'doctordirectory', 
        'appointments', 'surveys', 'photos', 'evaluation', 
        'araz', 'students', 'guardian', 'services', 'bulk_upload'
    ]
    
    for app in apps:
        migration_dir = os.path.join(app, 'migrations')
        if os.path.exists(migration_dir):
            # Delete all .py files except __init__.py
            migration_files = glob.glob(os.path.join(migration_dir, '*.py'))
            for file in migration_files:
                if not file.endswith('__init__.py'):
                    try:
                        os.remove(file)
                        print(f"  ✓ Deleted {file}")
                    except Exception as e:
                        print(f"  ✗ Error deleting {file}: {e}")
            
            # Delete __pycache__
            pycache_dir = os.path.join(migration_dir, '__pycache__')
            if os.path.exists(pycache_dir):
                shutil.rmtree(pycache_dir)
    
    print("\n✓ Migration files cleaned")
    
    # Step 4: Create new migrations
    print("\n[4/6] Creating fresh migrations...")
    print("\nRun the following commands in order:\n")
    
    print("# 1. Create initial migrations")
    print("python manage.py makemigrations")
    
    print("\n# 2. Apply migrations")
    print("python manage.py migrate")
    
    print("\n# 3. Create superuser (optional)")
    print("python manage.py createsuperuser")
    
    print("\n# 4. Generate test data")
    print("python generate_mock_data.py")
    
    print("\n# 5. Run the server")
    print("python manage.py runserver")
    
    print("\n" + "=" * 80)
    print("MANUAL STEPS REQUIRED")
    print("=" * 80)
    print("\nPlease run the commands above in your terminal.")
    print("If you encounter any errors, see the troubleshooting section below.")
    
    print("\n" + "=" * 80)
    print("TROUBLESHOOTING")
    print("=" * 80)
    
    print("\n1. If you get 'No module named appointments':")
    print("   - Make sure the appointments app is in INSTALLED_APPS in settings.py")
    
    print("\n2. If you get foreign key constraint errors:")
    print("   - Run migrations in this order:")
    print("     python manage.py migrate contenttypes")
    print("     python manage.py migrate auth")
    print("     python manage.py migrate accounts")
    print("     python manage.py migrate moze")
    print("     python manage.py migrate doctordirectory")
    print("     python manage.py migrate")
    
    print("\n3. If you get 'table already exists' errors:")
    print("   - Delete db.sqlite3 again and start over")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()