#!/usr/bin/env python3
"""
Quick script to check what services exist in the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from doctordirectory.models import Doctor, MedicalService

def main():
    print("=== DOCTORS AND THEIR SERVICES ===")
    
    doctors = Doctor.objects.all()
    print(f"Total doctors: {doctors.count()}")
    
    total_services = MedicalService.objects.count()
    print(f"Total services: {total_services}")
    
    if total_services == 0:
        print("❌ No services found in database!")
        return
    
    print("\n=== SERVICES BY DOCTOR ===")
    for doctor in doctors[:10]:  # Show first 10 doctors
        services = MedicalService.objects.filter(doctor=doctor, is_available=True)
        print(f"\nDoctor: {doctor.name} (ID: {doctor.id})")
        print(f"  Services count: {services.count()}")
        
        for service in services[:3]:  # Show first 3 services
            print(f"    - {service.name} (₹{service.price})")
        
        if services.count() > 3:
            print(f"    ... and {services.count() - 3} more")
    
    print(f"\n=== API TEST FOR DOCTOR 131 ===")
    try:
        doctor_131 = Doctor.objects.get(id=131)
        services_131 = MedicalService.objects.filter(doctor=doctor_131, is_available=True)
        print(f"Doctor 131: {doctor_131.name}")
        print(f"Services for doctor 131: {services_131.count()}")
        
        for service in services_131:
            print(f"  - {service.name}: ₹{service.price} ({service.duration_minutes} min)")
            
    except Doctor.DoesNotExist:
        print("❌ Doctor with ID 131 not found")

if __name__ == '__main__':
    main()