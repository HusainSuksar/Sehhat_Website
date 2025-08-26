#!/usr/bin/env python
"""
Quick fix for the photo album date error
"""

import os
import django
from faker import Faker

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

fake = Faker()

# Test the fix
print("Testing date generation...")
date_obj = fake.date_between(start_date='-2y', end_date='today')
print(f"Generated date: {date_obj}")
print(f"Date type: {type(date_obj)}")
print(f"Year: {date_obj.year}")

# Test original problematic code (commented out)
# date_str = fake.date()  # This returns a string
# print(f"fake.date() returns: {date_str} (type: {type(date_str)})")

print("✅ Fix verified - date_between() returns proper date object with .year attribute")