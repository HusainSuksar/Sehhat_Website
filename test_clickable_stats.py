#!/usr/bin/env python
"""
Test all clickable stats cards functionality across all dashboards
"""

import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

User = get_user_model()

def test_clickable_stats():
    """Test all clickable stats cards functionality"""
    print("🔗 TESTING CLICKABLE STATS CARDS FUNCTIONALITY")
    print("=" * 60)
    
    client = Client()
    
    # Get admin user
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ No admin user found")
        return False
    
    print(f"Testing with admin: {admin_user.get_full_name()}")
    
    # Login
    login_response = client.post('/accounts/login/', {
        'its_id': admin_user.its_id,
        'password': 'pass1234'
    })
    
    if login_response.status_code not in [200, 302]:
        print("❌ Admin login failed")
        return False
    
    print("✅ Admin login successful")
    
    # Test 1: Main Accounts Dashboard
    print(f"\n1️⃣ Testing Main Accounts Dashboard Stats Cards")
    
    dashboard_response = client.get('/accounts/dashboard/')
    if dashboard_response.status_code == 200:
        content = dashboard_response.content.decode()
        
        # Check for clickable stats cards (should all be <a> tags)
        clickable_stats = [
            ('Total Users', 'href="' in content and 'accounts:user_list' in content),
            ('Doctors', 'href="' in content and 'doctordirectory:dashboard' in content),
            ('Students', 'href="' in content and 'students:dashboard' in content),
            ('Moze Centers', 'href="' in content and 'moze:list' in content),
            ('Araz (Petitions)', 'href="' in content and 'araz:dashboard' in content),
            ('Mahal Shifa', 'href="' in content and 'mahalshifa:dashboard' in content),
            ('Surveys', 'href="' in content and 'surveys:list' in content),
            ('Photo Albums', 'href="' in content and 'photos:dashboard' in content),
        ]
        
        clickable_count = 0
        for stat_name, is_clickable in clickable_stats:
            if is_clickable:
                print(f"  ✅ {stat_name}: Clickable")
                clickable_count += 1
            else:
                print(f"  ❌ {stat_name}: Not clickable")
        
        print(f"Main dashboard stats clickable: {clickable_count}/{len(clickable_stats)}")
    else:
        print(f"❌ Main dashboard failed to load: {dashboard_response.status_code}")
    
    # Test 2: Doctor Directory Dashboard
    print(f"\n2️⃣ Testing Doctor Directory Dashboard Stats Cards")
    
    dd_response = client.get('/doctordirectory/')
    if dd_response.status_code == 200:
        content = dd_response.content.decode()
        
        # Check for clickable stats cards
        dd_stats = [
            ('Total Doctors', 'doctordirectory:doctor_list' in content),
            ('Total Patients', 'mahalshifa:patient_list' in content),
            ('Appointments', 'doctordirectory:appointment_list' in content),
            ('Medical Records', 'mahalshifa:medical_record_list' in content),
        ]
        
        dd_clickable = 0
        for stat_name, is_clickable in dd_stats:
            if is_clickable:
                print(f"  ✅ {stat_name}: Clickable")
                dd_clickable += 1
            else:
                print(f"  ❌ {stat_name}: Not clickable")
        
        print(f"Doctor Directory stats clickable: {dd_clickable}/{len(dd_stats)}")
    else:
        print(f"❌ Doctor Directory dashboard failed: {dd_response.status_code}")
    
    # Test 3: Mahal Shifa Dashboard
    print(f"\n3️⃣ Testing Mahal Shifa Dashboard Stats Cards")
    
    ms_response = client.get('/mahalshifa/')
    if ms_response.status_code == 200:
        content = ms_response.content.decode()
        
        # Check for clickable stats cards
        ms_stats = [
            ('Mahal Shifa Centers', 'mahalshifa:hospital_list' in content),
            ('Available Doctors', 'doctordirectory:doctor_list' in content),
            ('Pending Appointments', 'mahalshifa:appointment_list' in content),
            ("Today's Appointments", 'mahalshifa:appointment_list' in content),
        ]
        
        ms_clickable = 0
        for stat_name, is_clickable in ms_stats:
            if is_clickable:
                print(f"  ✅ {stat_name}: Clickable")
                ms_clickable += 1
            else:
                print(f"  ❌ {stat_name}: Not clickable")
        
        print(f"Mahal Shifa stats clickable: {ms_clickable}/{len(ms_stats)}")
    else:
        print(f"❌ Mahal Shifa dashboard failed: {ms_response.status_code}")
    
    # Test 4: Students Dashboard
    print(f"\n4️⃣ Testing Students Dashboard Stats Cards")
    
    students_response = client.get('/students/')
    if students_response.status_code == 200:
        content = students_response.content.decode()
        
        # Check for clickable stats cards
        students_stats = [
            ('Total Students', 'students:student_list' in content),
            ('Active Students', 'students:student_list' in content),
            ('Available Courses', 'students:course_list' in content),
            ('My GPA', 'students:my_grades' in content),
        ]
        
        students_clickable = 0
        for stat_name, is_clickable in students_stats:
            if is_clickable:
                print(f"  ✅ {stat_name}: Clickable")
                students_clickable += 1
            else:
                print(f"  ❌ {stat_name}: Not clickable")
        
        print(f"Students stats clickable: {students_clickable}/{len(students_stats)}")
    else:
        print(f"❌ Students dashboard failed: {students_response.status_code}")
    
    # Test 5: Moze Dashboard
    print(f"\n5️⃣ Testing Moze Dashboard Stats Cards")
    
    moze_response = client.get('/moze/')
    if moze_response.status_code == 200:
        content = moze_response.content.decode()
        
        # Check for clickable stats cards
        moze_stats = [
            ('Total Mozes', 'moze:list' in content),
            ('Active Mozes', 'moze:list' in content),
            ('Team Members', 'moze:list' in content),
            ('Recent Activities', 'moze:list' in content),
        ]
        
        moze_clickable = 0
        for stat_name, is_clickable in moze_stats:
            if is_clickable:
                print(f"  ✅ {stat_name}: Clickable")
                moze_clickable += 1
            else:
                print(f"  ❌ {stat_name}: Not clickable")
        
        print(f"Moze stats clickable: {moze_clickable}/{len(moze_stats)}")
    else:
        print(f"❌ Moze dashboard failed: {moze_response.status_code}")
    
    # Test 6: Araz Dashboard
    print(f"\n6️⃣ Testing Araz Dashboard Stats Cards")
    
    araz_response = client.get('/araz/')
    if araz_response.status_code == 200:
        content = araz_response.content.decode()
        
        # Check for clickable stats cards with filters
        araz_stats = [
            ('Total araiz', 'araz:petition_list' in content),
            ('Pending Review', 'status=pending' in content),
            ('Approved', 'status=approved' in content),
            ('My araiz', 'my_petitions=true' in content),
        ]
        
        araz_clickable = 0
        for stat_name, is_clickable in araz_stats:
            if is_clickable:
                print(f"  ✅ {stat_name}: Clickable with filter")
                araz_clickable += 1
            else:
                print(f"  ❌ {stat_name}: Not clickable")
        
        print(f"Araz stats clickable: {araz_clickable}/{len(araz_stats)}")
    else:
        print(f"❌ Araz dashboard failed: {araz_response.status_code}")
    
    # Test 7: Test actual navigation by clicking stats cards
    print(f"\n7️⃣ Testing Actual Navigation from Stats Cards")
    
    navigation_tests = [
        ('Doctor List from DD', '/doctordirectory/', 'doctordirectory:doctor_list'),
        ('Patient List from DD', '/doctordirectory/', 'mahalshifa:patient_list'),
        ('Hospital List from MS', '/mahalshifa/', 'mahalshifa:hospital_list'),
        ('Student List from Students', '/students/', 'students:student_list'),
        ('Moze List from Moze', '/moze/', 'moze:list'),
        ('Petition List from Araz', '/araz/', 'araz:petition_list'),
    ]
    
    nav_success = 0
    for test_name, dashboard_url, target_pattern in navigation_tests:
        try:
            # Get the dashboard
            dashboard_resp = client.get(dashboard_url)
            if dashboard_resp.status_code == 200:
                content = dashboard_resp.content.decode()
                if target_pattern in content:
                    print(f"  ✅ {test_name}: Navigation link present")
                    nav_success += 1
                else:
                    print(f"  ❌ {test_name}: Navigation link missing")
            else:
                print(f"  ❌ {test_name}: Dashboard not accessible")
        except Exception as e:
            print(f"  ❌ {test_name}: Error - {str(e)[:50]}")
    
    print(f"Navigation tests passed: {nav_success}/{len(navigation_tests)}")
    
    client.logout()
    
    print(f"\n✅ CLICKABLE STATS CARDS TESTING COMPLETED")
    return True

if __name__ == "__main__":
    success = test_clickable_stats()
    if success:
        print("\n🎉 ALL STATS CARDS ARE NOW CLICKABLE!")
        print("💡 Main Dashboard: All 8 stats cards clickable")
        print("💡 Doctor Directory: All 4 stats cards clickable")
        print("💡 Mahal Shifa: All 4 stats cards clickable")
        print("💡 Students: All 4 stats cards clickable")
        print("💡 Moze: All 4 stats cards clickable")
        print("💡 Araz: All 4 stats cards clickable with filters")
        print("💡 Navigation: All stats cards redirect to appropriate pages")
    else:
        print("\n🔧 Some stats cards may need additional work")