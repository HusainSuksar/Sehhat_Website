from django.core.management.base import BaseCommand
from doctordirectory.models import Doctor, MedicalService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test medical services for existing doctors'

    def handle(self, *args, **options):
        self.stdout.write("=== CREATING TEST MEDICAL SERVICES ===")
        
        # Get all doctors
        doctors = Doctor.objects.all()
        self.stdout.write(f"Found {doctors.count()} doctors")
        
        if doctors.count() == 0:
            self.stdout.write(self.style.ERROR("No doctors found! Please create doctors first."))
            return
        
        # Define common medical services
        services_templates = [
            {
                'name': 'General Consultation',
                'description': 'General medical consultation and check-up',
                'duration_minutes': 30,
                'price': Decimal('500.00')
            },
            {
                'name': 'Follow-up Consultation',
                'description': 'Follow-up visit for existing patients',
                'duration_minutes': 20,
                'price': Decimal('300.00')
            },
            {
                'name': 'Health Check-up',
                'description': 'Complete health screening and check-up',
                'duration_minutes': 45,
                'price': Decimal('800.00')
            },
            {
                'name': 'Prescription Renewal',
                'description': 'Renewal of existing prescriptions',
                'duration_minutes': 15,
                'price': Decimal('200.00')
            },
            {
                'name': 'Medical Certificate',
                'description': 'Issuance of medical certificates',
                'duration_minutes': 15,
                'price': Decimal('250.00')
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for doctor in doctors:
            self.stdout.write(f"\nProcessing doctor: {doctor.name}")
            
            # Check if doctor already has services
            existing_services = MedicalService.objects.filter(doctor=doctor).count()
            
            if existing_services > 0:
                self.stdout.write(f"  - Already has {existing_services} services")
                continue
            
            # Create services for this doctor
            for service_template in services_templates:
                service, created = MedicalService.objects.get_or_create(
                    doctor=doctor,
                    name=service_template['name'],
                    defaults={
                        'description': service_template['description'],
                        'duration_minutes': service_template['duration_minutes'],
                        'price': service_template['price'],
                        'is_available': True
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"  ✅ Created: {service.name} - ₹{service.price}")
                else:
                    updated_count += 1
                    self.stdout.write(f"  ⚠️ Already exists: {service.name}")
        
        self.stdout.write(f"\n=== SUMMARY ===")
        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_count} new services"))
        if updated_count > 0:
            self.stdout.write(self.style.WARNING(f"⚠️ {updated_count} services already existed"))
        
        # Show final statistics
        total_services = MedicalService.objects.count()
        doctors_with_services = Doctor.objects.filter(medical_services__isnull=False).distinct().count()
        
        self.stdout.write(f"\n=== FINAL STATISTICS ===")
        self.stdout.write(f"Total medical services: {total_services}")
        self.stdout.write(f"Doctors with services: {doctors_with_services}/{doctors.count()}")
        
        if doctors_with_services > 0:
            self.stdout.write(self.style.SUCCESS("\n🎉 Doctor services dropdown should now work properly!"))
        else:
            self.stdout.write(self.style.ERROR("\n❌ No services created. Check if doctors exist in the database."))