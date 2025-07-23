#!/usr/bin/env python3
"""
Web Application Status Report for Umoor Sehhat Django Project
"""

import os
import sys
import django
import requests
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from django.conf import settings

def check_server_status():
    """Check if development server is running"""
    print("🌐 SERVER STATUS")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        print(f"✅ Development server: RUNNING (Status: {response.status_code})")
        return True
    except:
        print("❌ Development server: NOT RUNNING")
        return False

def check_app_endpoints():
    """Test all app endpoints"""
    print("\n📱 APP ENDPOINTS STATUS")
    print("=" * 50)
    
    apps = {
        'accounts': '/accounts/login/',
        'moze': '/moze/',
        'surveys': '/surveys/',
        'students': '/students/',
        'araz': '/araz/',
        'evaluation': '/evaluation/',
        'doctordirectory': '/doctordirectory/',
        'mahalshifa': '/mahalshifa/'
    }
    
    working_apps = 0
    for app_name, endpoint in apps.items():
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=3)
            status = "✅ WORKING" if response.status_code in [200, 302] else f"⚠️  STATUS {response.status_code}"
            print(f"{app_name.capitalize()}: {status}")
            if response.status_code in [200, 302]:
                working_apps += 1
        except Exception as e:
            print(f"{app_name.capitalize()}: ❌ ERROR - {str(e)[:50]}")
    
    print(f"\nWorking Apps: {working_apps}/{len(apps)}")
    return working_apps

def check_database_status():
    """Check database and table status"""
    print("\n🗄️  DATABASE STATUS")
    print("=" * 50)
    
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection: WORKING")
        
        # Check tables
        tables = connection.introspection.table_names()
        print(f"📊 Total tables: {len(tables)}")
        
        # Check app-specific tables
        app_tables = {}
        for table in tables:
            for app in ['accounts', 'araz', 'moze', 'surveys', 'students', 'evaluation', 'doctordirectory', 'mahalshifa']:
                if table.startswith(f"{app}_"):
                    if app not in app_tables:
                        app_tables[app] = []
                    app_tables[app].append(table)
        
        print("\n📋 Tables per app:")
        for app, tables_list in app_tables.items():
            print(f"  {app}: {len(tables_list)} tables")
            
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_user_data():
    """Check user and test data"""
    print("\n👥 USER DATA STATUS")
    print("=" * 50)
    
    try:
        User = get_user_model()
        
        total_users = User.objects.count()
        print(f"📊 Total users: {total_users}")
        
        # Check user roles
        roles = ['admin', 'doctor', 'student', 'aamil', 'moze_coordinator']
        for role in roles:
            count = User.objects.filter(role=role).count()
            print(f"  {role.capitalize()}: {count}")
        
        # Check superusers
        superuser_count = User.objects.filter(is_superuser=True).count()
        print(f"  Superusers: {superuser_count}")
        
        return total_users > 0
        
    except Exception as e:
        print(f"❌ User data error: {e}")
        return False

def check_app_specific_data():
    """Check data for each app"""
    print("\n📝 APP DATA STATUS")
    print("=" * 50)
    
    data_status = {}
    
    # Test each app's models
    try:
        from moze.models import Moze
        moze_count = Moze.objects.count()
        print(f"🏥 Moze Centers: {moze_count}")
        data_status['moze'] = moze_count > 0
    except Exception as e:
        print(f"❌ Moze data error: {str(e)[:50]}")
        data_status['moze'] = False
    
    try:
        from surveys.models import Survey
        survey_count = Survey.objects.count()
        print(f"📋 Surveys: {survey_count}")
        data_status['surveys'] = survey_count > 0
    except Exception as e:
        print(f"❌ Survey data error: {str(e)[:50]}")
        data_status['surveys'] = False
    
    try:
        from araz.models import DuaAraz
        araz_count = DuaAraz.objects.count()
        print(f"🤲 Araz Requests: {araz_count}")
        data_status['araz'] = araz_count > 0
    except Exception as e:
        print(f"❌ Araz data error: {str(e)[:50]}")
        data_status['araz'] = False
    
    # Additional apps (may have missing tables)
    missing_tables = []
    try:
        from students.models import Student
        student_count = Student.objects.count()
        print(f"🎓 Students: {student_count}")
        data_status['students'] = student_count > 0
    except Exception as e:
        print(f"⚠️  Students data: TABLE MISSING")
        missing_tables.append('students_student')
        data_status['students'] = False
    
    if missing_tables:
        print(f"\n⚠️  Missing tables detected: {', '.join(missing_tables)}")
    
    return data_status

def generate_summary():
    """Generate overall summary"""
    print("\n📈 OVERALL STATUS SUMMARY")
    print("=" * 50)
    
    server_ok = check_server_status()
    working_apps = check_app_endpoints()
    db_ok = check_database_status()
    users_ok = check_user_data()
    data_status = check_app_specific_data()
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"✅ Server Running: {'YES' if server_ok else 'NO'}")
    print(f"✅ Apps Working: {working_apps}/8")
    print(f"✅ Database: {'WORKING' if db_ok else 'ERROR'}")
    print(f"✅ User Data: {'POPULATED' if users_ok else 'MISSING'}")
    
    working_data_apps = sum(1 for status in data_status.values() if status)
    print(f"✅ App Data: {working_data_apps}/{len(data_status)} apps have data")
    
    # Overall health score
    total_checks = 5 + len(data_status)  # server, db, users, + each app data
    passed_checks = (1 if server_ok else 0) + (1 if db_ok else 0) + (1 if users_ok else 0) + working_data_apps + (1 if working_apps >= 6 else 0)
    health_score = (passed_checks / total_checks) * 100
    
    print(f"\n🏆 HEALTH SCORE: {health_score:.1f}%")
    
    if health_score >= 80:
        print("🟢 Status: EXCELLENT - App is fully functional")
    elif health_score >= 60:
        print("🟡 Status: GOOD - Minor issues need attention")
    elif health_score >= 40:
        print("🟠 Status: FAIR - Several issues need fixing")
    else:
        print("🔴 Status: POOR - Major issues require immediate attention")

if __name__ == "__main__":
    print(f"UMOOR SEHHAT WEB APPLICATION STATUS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    generate_summary()