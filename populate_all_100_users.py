#!/usr/bin/env python
"""
Populate All 100 Users + App Data Script
Creates complete dataset for comprehensive testing
"""
import os
import django
import random
from datetime import datetime, timedelta, date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.services import MockITSService
from accounts.forms import CustomLoginForm
from django.test import RequestFactory

User = get_user_model()

def create_all_100_users():
    """Create all 100 users from ITS API"""
    print("🔐 Creating all 100 users from ITS API...")
    
    request_factory = RequestFactory()
    request = request_factory.post('/accounts/login/')
    request.session = {}
    
    created_count = 0
    existing_count = 0
    
    # Get all 100 ITS IDs
    all_its_ids = list(MockITSService.VALID_ITS_IDS.keys())
    print(f"📋 Total ITS IDs available: {len(all_its_ids)}")
    
    for its_id in all_its_ids:
        try:
            # Check if user already exists
            if User.objects.filter(its_id=its_id).exists():
                existing_count += 1
                print(f"⏭️  User {its_id} already exists")
                continue
                
            # Create new user via ITS API
            form_data = {'its_id': its_id, 'password': 'test123'}
            form = CustomLoginForm(request=request, data=form_data)
            
            if form.is_valid():
                user = form.get_user()
                created_count += 1
                print(f"✅ Created {user.get_full_name()} ({its_id}) - {user.get_role_display()}")
            else:
                print(f"❌ Failed {its_id}: {form.errors}")
                
        except Exception as e:
            print(f"❌ Error {its_id}: {e}")
    
    total_users = User.objects.count()
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Created: {created_count} new users")
    print(f"   ⏭️  Existing: {existing_count} users")
    print(f"   🎯 Total: {total_users} users in database")
    
    return total_users

def create_basic_app_data():
    """Create basic data for dashboard stats"""
    print("\n📊 Creating basic app data for dashboard stats...")
    
    try:
        # Import models dynamically to avoid import errors
        all_users = list(User.objects.all())
        
        # Create basic Moze data
        try:
            from moze.models import Moze
            if Moze.objects.count() == 0:
                print("🏢 Creating Moze data...")
                aamils = User.objects.filter(role='aamil')[:10]  # First 10 aamils
                for i, aamil in enumerate(aamils):
                    Moze.objects.create(
                        name=f"Moze {chr(65+i)}{i%2+1}",  # A1, B1, C1, etc.
                        location=f"Location {i+1}",
                        aamil=aamil,
                        contact_number=f"+91{random.randint(9000000000, 9999999999)}",
                        email=f"moze{i+1}@example.com",
                        description=f"Description for Moze {chr(65+i)}{i%2+1}",
                        established_date=date.today() - timedelta(days=random.randint(365, 3650))
                    )
                print(f"   ✅ Created {Moze.objects.count()} Moze entries")
        except ImportError:
            print("   ⏭️  Moze model not available")
        
        # Create basic Student data
        try:
            from students.models import Student
            students = User.objects.filter(role='student')
            student_count = 0
            for student_user in students:
                if not hasattr(student_user, 'student'):
                    Student.objects.create(
                        user=student_user,
                        student_id=f"STU{random.randint(1000, 9999)}",
                        academic_level='undergraduate',
                        field_of_study='Islamic Studies',
                        admission_date=date.today() - timedelta(days=random.randint(30, 1460)),
                        is_active=True
                    )
                    student_count += 1
            print(f"   ✅ Created {student_count} Student profiles")
        except ImportError:
            print("   ⏭️  Student model not available")
        
        # Create basic Doctor data
        try:
            from doctordirectory.models import Doctor
            doctors = User.objects.filter(role='doctor')
            doctor_count = 0
            specialties = ['General Medicine', 'Cardiology', 'Pediatrics', 'Dermatology']
            for doctor_user in doctors:
                try:
                    if not Doctor.objects.filter(user=doctor_user).exists():
                        Doctor.objects.create(
                            user=doctor_user,
                            license_number=f"MED{random.randint(10000, 99999)}",
                            specialty=random.choice(specialties),
                            years_of_experience=random.randint(1, 30),
                            bio=f"Experienced {random.choice(specialties)} specialist.",
                            consultation_fee=Decimal(str(random.randint(500, 2000))),
                            is_verified=True
                        )
                        doctor_count += 1
                except Exception as e:
                    print(f"   ⚠️  Could not create doctor for {doctor_user}: {e}")
            print(f"   ✅ Created {doctor_count} Doctor profiles")
        except ImportError:
            print("   ⏭️  Doctor model not available")
        
        # Create basic Survey data
        try:
            from surveys.models import Survey, Question
            if Survey.objects.count() == 0:
                admin_user = User.objects.filter(role='badri_mahal_admin').first()
                if admin_user:
                    survey = Survey.objects.create(
                        title='Community Feedback Survey',
                        description='General community feedback survey for testing',
                        created_by=admin_user,
                        is_active=True,
                        start_date=timezone.now() - timedelta(days=30),
                        end_date=timezone.now() + timedelta(days=30)
                    )
                    print(f"   ✅ Created 1 Survey")
        except ImportError:
            print("   ⏭️  Survey model not available")
        
        # Create basic Petition data
        try:
            from araz.models import Petition
            if Petition.objects.count() < 5:
                users_sample = random.sample(all_users, min(5, len(all_users)))
                petition_count = 0
                for user in users_sample:
                    if not Petition.objects.filter(petitioner_its_id=user.its_id).exists():
                        Petition.objects.create(
                            petitioner_its_id=user.its_id,
                            petitioner_name=user.get_full_name(),
                            petitioner_mobile=user.mobile_number or f"+91{random.randint(9000000000, 9999999999)}",
                            petitioner_email=user.email,
                            petitioner_moze=user.jamaat or 'General',
                            petition_type='Request',
                            subject=f'Sample petition from {user.get_full_name()}',
                            description=f'Sample petition description for testing purposes.',
                            status='pending',
                            created_at=timezone.now() - timedelta(days=random.randint(1, 30)),
                            updated_at=timezone.now()
                        )
                        petition_count += 1
                print(f"   ✅ Created {petition_count} Petitions")
        except ImportError:
            print("   ⏭️  Petition model not available")
            
    except Exception as e:
        print(f"   ⚠️  Error creating app data: {e}")

def print_final_stats():
    """Print final statistics"""
    print(f"\n🎉 FINAL STATISTICS:")
    print(f"=" * 50)
    
    # User counts
    total_users = User.objects.count()
    admin_count = User.objects.filter(role='badri_mahal_admin').count()
    aamil_count = User.objects.filter(role='aamil').count()
    coordinator_count = User.objects.filter(role='moze_coordinator').count()
    doctor_count = User.objects.filter(role='doctor').count()
    student_count = User.objects.filter(role='student').count()
    
    print(f"👥 USERS:")
    print(f"   Total: {total_users}")
    print(f"   👑 Admins: {admin_count}")
    print(f"   👥 Aamils: {aamil_count}")
    print(f"   📊 Coordinators: {coordinator_count}")
    print(f"   👩‍⚕️ Doctors: {doctor_count}")
    print(f"   🎓 Students: {student_count}")
    
    # App data counts
    try:
        from moze.models import Moze
        print(f"   🏢 Moze: {Moze.objects.count()}")
    except:
        pass
    
    try:
        from students.models import Student
        print(f"   📚 Student Profiles: {Student.objects.count()}")
    except:
        pass
    
    try:
        from doctordirectory.models import Doctor
        print(f"   👨‍⚕️ Doctor Profiles: {Doctor.objects.count()}")
    except:
        pass
    
    try:
        from surveys.models import Survey
        print(f"   📋 Surveys: {Survey.objects.count()}")
    except:
        pass
    
    try:
        from araz.models import Petition
        print(f"   📄 Petitions: {Petition.objects.count()}")
    except:
        pass

def main():
    """Main function"""
    print("🚀 POPULATING ALL 100 USERS + APP DATA")
    print("=" * 60)
    
    try:
        # Step 1: Create all 100 users
        total_users = create_all_100_users()
        
        # Step 2: Create basic app data
        create_basic_app_data()
        
        # Step 3: Print final stats
        print_final_stats()
        
        print(f"\n✅ SUCCESS! Database now ready for comprehensive testing!")
        print(f"🔐 Login with ITS ID 50000001 to see full dashboard stats")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()