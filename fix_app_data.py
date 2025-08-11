#!/usr/bin/env python
"""
Fix App Data Script - Create app data with correct field names
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

User = get_user_model()

def fix_app_data():
    """Create app data with correct field names"""
    print("🔧 Creating app data with correct field names...")
    
    all_users = list(User.objects.all())
    
    # 1. Create Moze data with correct fields
    try:
        from moze.models import Moze
        if Moze.objects.count() == 0:
            print("🏢 Creating Moze data...")
            aamils = User.objects.filter(role='aamil')[:10]  # First 10 aamils
            for i, aamil in enumerate(aamils):
                try:
                    Moze.objects.create(
                        name=f"Moze {chr(65+i)}{i%2+1}",  # A1, B1, C1, etc.
                        location=f"Location {i+1}",
                        aamil=aamil
                    )
                except Exception as e:
                    print(f"   ⚠️  Error creating Moze {i+1}: {e}")
            print(f"   ✅ Created {Moze.objects.count()} Moze entries")
    except ImportError:
        print("   ⏭️  Moze model not available")
    except Exception as e:
        print(f"   ⚠️  Moze creation error: {e}")
    
    # 2. Create Student profiles
    try:
        from students.models import Student
        students = User.objects.filter(role='student')
        student_count = 0
        for student_user in students:
            try:
                # Check if student profile already exists
                if not Student.objects.filter(user=student_user).exists():
                    Student.objects.create(
                        user=student_user,
                        student_id=f"STU{random.randint(1000, 9999)}",
                        academic_level='undergraduate',
                        field_of_study='Islamic Studies',
                        admission_date=date.today() - timedelta(days=random.randint(30, 1460)),
                        is_active=True
                    )
                    student_count += 1
            except Exception as e:
                print(f"   ⚠️  Error creating student profile for {student_user}: {e}")
        print(f"   ✅ Created {student_count} Student profiles")
    except ImportError:
        print("   ⏭️  Student model not available")
    except Exception as e:
        print(f"   ⚠️  Student creation error: {e}")
    
    # 3. Create Doctor profiles  
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
                print(f"   ⚠️  Error creating doctor profile for {doctor_user}: {e}")
        print(f"   ✅ Created {doctor_count} Doctor profiles")
    except ImportError:
        print("   ⏭️  Doctor model not available")
    except Exception as e:
        print(f"   ⚠️  Doctor creation error: {e}")
    
    # 4. Create basic Survey
    try:
        from surveys.models import Survey
        if Survey.objects.count() == 0:
            admin_user = User.objects.filter(role='badri_mahal_admin').first()
            if admin_user:
                try:
                    Survey.objects.create(
                        title='Community Feedback Survey',
                        description='General community feedback survey for testing',
                        created_by=admin_user,
                        is_active=True,
                        start_date=timezone.now() - timedelta(days=30),
                        end_date=timezone.now() + timedelta(days=30)
                    )
                    print(f"   ✅ Created 1 Survey")
                except Exception as e:
                    print(f"   ⚠️  Error creating survey: {e}")
    except ImportError:
        print("   ⏭️  Survey model not available")
    except Exception as e:
        print(f"   ⚠️  Survey creation error: {e}")
    
    # 5. Create basic Petitions
    try:
        from araz.models import Petition
        if Petition.objects.count() < 5:
            users_sample = random.sample(all_users, min(5, len(all_users)))
            petition_count = 0
            for user in users_sample:
                try:
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
                except Exception as e:
                    print(f"   ⚠️  Error creating petition for {user}: {e}")
            print(f"   ✅ Created {petition_count} Petitions")
    except ImportError:
        print("   ⏭️  Petition model not available")
    except Exception as e:
        print(f"   ⚠️  Petition creation error: {e}")

def print_final_stats():
    """Print final statistics"""
    print(f"\n🎉 FINAL STATISTICS AFTER FIX:")
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
        print(f"   🏢 Moze: 0 (model error)")
    
    try:
        from students.models import Student
        print(f"   📚 Student Profiles: {Student.objects.count()}")
    except:
        print(f"   📚 Student Profiles: 0 (model error)")
    
    try:
        from doctordirectory.models import Doctor
        print(f"   👨‍⚕️ Doctor Profiles: {Doctor.objects.count()}")
    except:
        print(f"   👨‍⚕️ Doctor Profiles: 0 (model error)")
    
    try:
        from surveys.models import Survey
        print(f"   📋 Surveys: {Survey.objects.count()}")
    except:
        print(f"   📋 Surveys: 0 (model error)")
    
    try:
        from araz.models import Petition
        print(f"   📄 Petitions: {Petition.objects.count()}")
    except:
        print(f"   📄 Petitions: 0 (model error)")

def main():
    """Main function"""
    print("🔧 FIXING APP DATA WITH CORRECT FIELD NAMES")
    print("=" * 60)
    
    try:
        fix_app_data()
        print_final_stats()
        
        print(f"\n✅ APP DATA FIX COMPLETED!")
        print(f"🔐 Login with ITS ID 50000001 to see updated dashboard stats")
        print(f"📊 Dashboard should now show meaningful numbers instead of zeros")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()