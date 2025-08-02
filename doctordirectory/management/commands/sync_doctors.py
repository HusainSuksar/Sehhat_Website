from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from doctordirectory.models import Doctor as DoctordirectoryDoctor
from mahalshifa.models import Doctor as MahalShifaDoctor

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync mahalshifa doctors with doctordirectory doctors'

    def handle(self, *args, **options):
        self.stdout.write('Starting doctor sync...')
        
        # Get all mahalshifa doctors
        mahalshifa_doctors = MahalShifaDoctor.objects.all()
        
        created_count = 0
        updated_count = 0
        
        for mahal_doctor in mahalshifa_doctors:
            try:
                # Try to get existing doctordirectory doctor
                doctordirectory_doctor = DoctordirectoryDoctor.objects.get(user=mahal_doctor.user)
                
                # Update existing doctor
                doctordirectory_doctor.name = mahal_doctor.user.get_full_name()
                doctordirectory_doctor.specialty = mahal_doctor.specialization
                doctordirectory_doctor.qualification = mahal_doctor.qualification
                doctordirectory_doctor.experience_years = mahal_doctor.experience_years
                doctordirectory_doctor.is_verified = mahal_doctor.user.is_active
                doctordirectory_doctor.is_available = mahal_doctor.is_available
                doctordirectory_doctor.license_number = mahal_doctor.license_number
                doctordirectory_doctor.consultation_fee = mahal_doctor.consultation_fee
                doctordirectory_doctor.phone = mahal_doctor.user.phone_number
                doctordirectory_doctor.email = mahal_doctor.user.email
                doctordirectory_doctor.save()
                
                updated_count += 1
                self.stdout.write(f'Updated doctor: {doctordirectory_doctor.name}')
                
            except DoctordirectoryDoctor.DoesNotExist:
                # Create new doctordirectory doctor
                doctordirectory_doctor = DoctordirectoryDoctor.objects.create(
                    user=mahal_doctor.user,
                    name=mahal_doctor.user.get_full_name(),
                    its_id=mahal_doctor.user.its_id or '00000000',
                    specialty=mahal_doctor.specialization,
                    qualification=mahal_doctor.qualification,
                    experience_years=mahal_doctor.experience_years,
                    is_verified=mahal_doctor.user.is_active,
                    is_available=mahal_doctor.is_available,
                    license_number=mahal_doctor.license_number,
                    consultation_fee=mahal_doctor.consultation_fee,
                    phone=mahal_doctor.user.phone_number,
                    email=mahal_doctor.user.email,
                )
                
                created_count += 1
                self.stdout.write(f'Created doctor: {doctordirectory_doctor.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced doctors. Created: {created_count}, Updated: {updated_count}'
            )
        )