from django.core.management.base import BaseCommand
from django.db import transaction
import csv
import json
from accounts.services import ITSService


class Command(BaseCommand):
    help = 'Upload student and moze coordinator ITS IDs from CSV or JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to CSV or JSON file containing ITS IDs'
        )
        parser.add_argument(
            '--role',
            type=str,
            choices=['student', 'coordinator'],
            required=True,
            help='Role to assign to these ITS IDs'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing ITS IDs before uploading'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        role = options['role']
        clear = options.get('clear', False)
        
        self.stdout.write(f"Uploading {role} ITS IDs from {file_path}...")
        
        try:
            # Clear existing IDs if requested
            if clear:
                if role == 'student':
                    ITSService.STUDENT_ITS_IDS.clear()
                    self.stdout.write("Cleared existing student ITS IDs")
                else:
                    ITSService.COORDINATOR_ITS_IDS.clear()
                    self.stdout.write("Cleared existing coordinator ITS IDs")
            
            # Read ITS IDs from file
            its_ids = []
            
            if file_path.endswith('.csv'):
                with open(file_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    # Skip header if present
                    first_row = next(csv_reader, None)
                    if first_row and first_row[0].lower() != 'its_id':
                        its_ids.append(first_row[0])
                    
                    for row in csv_reader:
                        if row and row[0]:
                            its_ids.append(row[0].strip())
            
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    if isinstance(data, list):
                        its_ids = [str(id).strip() for id in data]
                    elif isinstance(data, dict) and 'its_ids' in data:
                        its_ids = [str(id).strip() for id in data['its_ids']]
            
            else:
                # Try reading as plain text file
                with open(file_path, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line and line.isdigit() and len(line) == 8:
                            its_ids.append(line)
            
            # Validate ITS IDs
            valid_ids = []
            invalid_ids = []
            
            for its_id in its_ids:
                if ITSService.validate_its_id(its_id):
                    valid_ids.append(its_id)
                else:
                    invalid_ids.append(its_id)
            
            # Upload valid ITS IDs
            if valid_ids:
                if role == 'student':
                    ITSService.add_student_its_ids(valid_ids)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully added {len(valid_ids)} student ITS IDs"
                        )
                    )
                else:
                    ITSService.add_coordinator_its_ids(valid_ids)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully added {len(valid_ids)} coordinator ITS IDs"
                        )
                    )
            
            # Report invalid IDs
            if invalid_ids:
                self.stdout.write(
                    self.style.WARNING(
                        f"Found {len(invalid_ids)} invalid ITS IDs:"
                    )
                )
                for invalid_id in invalid_ids[:10]:  # Show first 10
                    self.stdout.write(f"  - {invalid_id}")
                if len(invalid_ids) > 10:
                    self.stdout.write(f"  ... and {len(invalid_ids) - 10} more")
            
            # Show current counts
            self.stdout.write("\nCurrent ITS ID counts:")
            self.stdout.write(f"  Students: {len(ITSService.STUDENT_ITS_IDS)}")
            self.stdout.write(f"  Coordinators: {len(ITSService.COORDINATOR_ITS_IDS)}")
            
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f"File not found: {file_path}")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error processing file: {str(e)}")
            )