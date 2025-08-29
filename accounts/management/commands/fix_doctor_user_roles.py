from django.core.management.base import BaseCommand
from accounts.models import User
from doctordirectory.models import Doctor
from django.db.models import Count


class Command(BaseCommand):
    help = 'Check and fix user roles for existing doctor profiles'

    def handle(self, *args, **options):
        self.stdout.write("=== INVESTIGATING DOCTOR-USER ROLE MISMATCH ===\n")
        
        # Check Doctor profiles
        doctors = Doctor.objects.all()
        self.stdout.write(f"Total Doctor profiles: {doctors.count()}")
        
        # Check User roles
        self.stdout.write("\n=== USER ROLE COUNTS ===")
        role_counts = User.objects.values('role').annotate(count=Count('role'))
        for item in role_counts:
            self.stdout.write(f"{item['role']}: {item['count']}")
        
        # Check what roles the users associated with doctor profiles have
        self.stdout.write("\n=== DOCTOR PROFILE USER ROLES ===")
        doctor_user_roles = {}
        for doctor in doctors[:10]:  # Check first 10 for sample
            if doctor.user:
                role = doctor.user.role
                if role not in doctor_user_roles:
                    doctor_user_roles[role] = 0
                doctor_user_roles[role] += 1
                
                if len(doctor_user_roles) <= 5:  # Show first few examples
                    self.stdout.write(f"Doctor: {doctor.name} | User: {doctor.user.username} | Role: {doctor.user.role}")
        
        self.stdout.write(f"\nRoles of users with doctor profiles (sample of {min(doctors.count(), 10)}):")
        for role, count in doctor_user_roles.items():
            self.stdout.write(f"  {role}: {count}")
        
        # Count how many doctor profiles have users with role != 'doctor'
        doctors_with_wrong_role = Doctor.objects.exclude(user__role='doctor').count()
        self.stdout.write(f"\nDoctor profiles with user role != 'doctor': {doctors_with_wrong_role}")
        
        if doctors_with_wrong_role > 0:
            self.stdout.write(self.style.WARNING(f"\n⚠️ FOUND THE ISSUE: {doctors_with_wrong_role} doctor profiles have users with wrong roles!"))
            
            # Ask for confirmation to fix
            self.stdout.write("\nThis explains why /accounts/users/?role=doctor shows 'No users found'")
            self.stdout.write("The doctor profiles exist, but their associated users don't have role='doctor'")
            
            if input("\nDo you want to fix this by setting role='doctor' for all users with doctor profiles? (y/N): ").lower() == 'y':
                self.stdout.write("\n=== FIXING USER ROLES ===")
                
                updated_count = 0
                for doctor in Doctor.objects.exclude(user__role='doctor'):
                    if doctor.user:
                        old_role = doctor.user.role
                        doctor.user.role = 'doctor'
                        doctor.user.save()
                        updated_count += 1
                        
                        if updated_count <= 5:  # Show first few updates
                            self.stdout.write(f"Updated {doctor.user.username}: {old_role} → doctor")
                
                self.stdout.write(self.style.SUCCESS(f"\n✅ Updated {updated_count} users to have role='doctor'"))
                
                # Show updated counts
                self.stdout.write("\n=== UPDATED USER ROLE COUNTS ===")
                role_counts = User.objects.values('role').annotate(count=Count('role'))
                for item in role_counts:
                    self.stdout.write(f"{item['role']}: {item['count']}")
                    
                self.stdout.write(self.style.SUCCESS(f"\n🎉 Now /accounts/users/?role=doctor should show {User.objects.filter(role='doctor').count()} doctors!"))
            else:
                self.stdout.write("No changes made.")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ All doctor profiles have users with role='doctor' - something else is wrong"))