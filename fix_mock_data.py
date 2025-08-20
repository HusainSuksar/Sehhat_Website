#!/usr/bin/env python
"""Fix generate_mock_data.py to remove MozeCoordinator references"""

import re

# Read the file
with open('generate_mock_data.py', 'r') as f:
    content = f.read()

# Fix the import
content = content.replace('from moze.models import Moze, MozeCoordinator', 'from moze.models import Moze')

# Fix the MozeCoordinator.objects.create block
old_block = """                # Create MozeCoordinator entry
                MozeCoordinator.objects.create(
                    user=user,
                    moze=self.moze_list[i],
                    appointment_date=date.today() - timedelta(days=random.randint(30, 365)),
                    is_active=True
                )"""

new_block = """                # Assign coordinator to moze
                moze = self.moze_list[i]
                moze.moze_coordinator = user
                moze.save()
                self.coordinator_list.append(user)"""

content = content.replace(old_block, new_block)

# Write the fixed file
with open('generate_mock_data.py', 'w') as f:
    f.write(content)

print("✓ Fixed generate_mock_data.py")
print("  - Removed MozeCoordinator import")
print("  - Changed to use moze.moze_coordinator field instead")