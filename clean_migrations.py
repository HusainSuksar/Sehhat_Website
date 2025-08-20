#!/usr/bin/env python
"""
Clean all migrations and start fresh
"""

import os
import shutil
import glob

def clean_migrations():
    """Remove all migration files except __init__.py"""
    print("Cleaning migration files...")
    
    apps = [
        'accounts', 'moze', 'mahalshifa', 'doctordirectory', 
        'appointments', 'surveys', 'photos', 'evaluation', 
        'araz', 'students', 'services', 'bulk_upload'
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
                print(f"  ✓ Deleted {pycache_dir}")

def main():
    print("=" * 60)
    print("MIGRATION CLEANUP SCRIPT")
    print("=" * 60)
    
    # Remove database
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("✓ Removed database")
    
    # Clean migrations
    clean_migrations()
    
    print("\n✓ Cleanup complete!")
    print("\nNow run these commands in order:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python generate_mock_data.py")

if __name__ == '__main__':
    main()