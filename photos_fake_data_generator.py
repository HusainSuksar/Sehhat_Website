#!/usr/bin/env python3
"""
Comprehensive Fake Data Generator for Photos App
Creates realistic fake images, albums, metadata, and social interactions
"""

import os
import sys
import django
import random
import traceback
import time
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'umoor_sehhat.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile

# Import all models
from accounts.models import User, UserProfile
from moze.models import Moze
from photos.models import PhotoAlbum, Photo, PhotoTag, PhotoComment, PhotoLike

User = get_user_model()
fake = Faker(['en_US', 'ar_SA'])

# Data specifications
PHOTO_DATA_SPECS = {
    'albums_count': 50,
    'photos_per_album': (5, 25),  # Range of photos per album
    'tags_count': 30,
    'comments_per_photo': (0, 8),  # Range of comments per photo
    'likes_per_photo': (0, 15),    # Range of likes per photo
    'users_per_moze': (3, 8),      # Range of users per moze
}

# Photo categories and their characteristics
PHOTO_CATEGORIES = {
    'medical': {
        'titles': [
            'Medical Consultation', 'Patient Examination', 'Treatment Session',
            'Medical Equipment Setup', 'Clinical Procedure', 'Health Check',
            'Medical Team Meeting', 'Patient Care', 'Medical Documentation',
            'Emergency Response', 'Surgery Preparation', 'Medical Training'
        ],
        'descriptions': [
            'Professional medical consultation in progress',
            'Patient receiving medical examination',
            'Medical team providing treatment',
            'Advanced medical equipment in use',
            'Clinical procedure being performed',
            'Comprehensive health check session',
            'Medical team coordination meeting',
            'Patient care and monitoring',
            'Medical documentation and records',
            'Emergency medical response team',
            'Surgery preparation and setup',
            'Medical training and education'
        ],
        'locations': [
            'Medical Center', 'Consultation Room', 'Treatment Area',
            'Emergency Room', 'Surgery Suite', 'Medical Laboratory',
            'Patient Care Unit', 'Medical Office', 'Clinical Area'
        ]
    },
    'event': {
        'titles': [
            'Health Awareness Event', 'Medical Workshop', 'Community Health Day',
            'Medical Conference', 'Health Fair', 'Training Session',
            'Team Building Event', 'Medical Outreach', 'Health Education',
            'Community Meeting', 'Medical Seminar', 'Health Campaign'
        ],
        'descriptions': [
            'Health awareness event for the community',
            'Medical workshop and training session',
            'Community health day activities',
            'Medical conference and presentations',
            'Health fair with various activities',
            'Professional training session',
            'Team building and collaboration event',
            'Medical outreach to community',
            'Health education and awareness',
            'Community health meeting',
            'Medical seminar and discussion',
            'Health campaign activities'
        ],
        'locations': [
            'Community Center', 'Medical Center', 'Conference Hall',
            'Public Park', 'Training Facility', 'Community Hall',
            'Medical Office', 'Public Space', 'Educational Center'
        ]
    },
    'infrastructure': {
        'titles': [
            'Medical Facility', 'Equipment Installation', 'Facility Maintenance',
            'Medical Center Building', 'Equipment Setup', 'Facility Upgrade',
            'Medical Office Space', 'Equipment Maintenance', 'Facility Expansion',
            'Medical Laboratory', 'Equipment Testing', 'Facility Inspection'
        ],
        'descriptions': [
            'Modern medical facility and infrastructure',
            'Medical equipment installation process',
            'Facility maintenance and upkeep',
            'Medical center building and structure',
            'Equipment setup and configuration',
            'Facility upgrade and improvement',
            'Medical office space and layout',
            'Equipment maintenance and service',
            'Facility expansion and development',
            'Medical laboratory and equipment',
            'Equipment testing and validation',
            'Facility inspection and assessment'
        ],
        'locations': [
            'Medical Center', 'Laboratory', 'Equipment Room',
            'Facility Building', 'Maintenance Area', 'Office Space',
            'Medical Suite', 'Equipment Storage', 'Facility Area'
        ]
    },
    'team': {
        'titles': [
            'Medical Team', 'Staff Meeting', 'Team Collaboration',
            'Medical Staff', 'Team Training', 'Staff Development',
            'Medical Professionals', 'Team Building', 'Staff Workshop',
            'Medical Personnel', 'Team Coordination', 'Staff Meeting'
        ],
        'descriptions': [
            'Medical team working together',
            'Staff meeting and coordination',
            'Team collaboration and discussion',
            'Medical staff in action',
            'Team training and development',
            'Staff development session',
            'Medical professionals at work',
            'Team building activities',
            'Staff workshop and learning',
            'Medical personnel coordination',
            'Team coordination meeting',
            'Staff meeting and planning'
        ],
        'locations': [
            'Medical Office', 'Conference Room', 'Team Space',
            'Medical Center', 'Meeting Room', 'Collaboration Area',
            'Office Space', 'Training Room', 'Staff Area'
        ]
    },
    'patient': {
        'titles': [
            'Patient Care', 'Patient Consultation', 'Patient Treatment',
            'Patient Support', 'Patient Education', 'Patient Monitoring',
            'Patient Assessment', 'Patient Recovery', 'Patient Follow-up',
            'Patient Care Team', 'Patient Support Group', 'Patient Education'
        ],
        'descriptions': [
            'Comprehensive patient care services',
            'Patient consultation and assessment',
            'Patient treatment and care',
            'Patient support and assistance',
            'Patient education and guidance',
            'Patient monitoring and observation',
            'Patient assessment and evaluation',
            'Patient recovery and rehabilitation',
            'Patient follow-up and monitoring',
            'Patient care team in action',
            'Patient support group activities',
            'Patient education and awareness'
        ],
        'locations': [
            'Patient Care Area', 'Consultation Room', 'Treatment Room',
            'Patient Support Center', 'Education Room', 'Monitoring Area',
            'Assessment Room', 'Recovery Area', 'Follow-up Room'
        ]
    },
    'equipment': {
        'titles': [
            'Medical Equipment', 'Equipment Setup', 'Equipment Maintenance',
            'Medical Devices', 'Equipment Testing', 'Equipment Installation',
            'Medical Technology', 'Equipment Calibration', 'Equipment Training',
            'Medical Instruments', 'Equipment Validation', 'Equipment Service'
        ],
        'descriptions': [
            'Advanced medical equipment and devices',
            'Equipment setup and configuration',
            'Equipment maintenance and service',
            'Medical devices and technology',
            'Equipment testing and validation',
            'Equipment installation process',
            'Medical technology and innovation',
            'Equipment calibration and setup',
            'Equipment training and education',
            'Medical instruments and tools',
            'Equipment validation and testing',
            'Equipment service and maintenance'
        ],
        'locations': [
            'Equipment Room', 'Medical Laboratory', 'Technology Center',
            'Equipment Storage', 'Testing Area', 'Installation Site',
            'Medical Suite', 'Calibration Room', 'Training Facility'
        ]
    },
    'documentation': {
        'titles': [
            'Medical Documentation', 'Record Keeping', 'Documentation Process',
            'Medical Records', 'File Management', 'Documentation Review',
            'Medical Files', 'Record Maintenance', 'Documentation Update',
            'Medical Reports', 'File Organization', 'Documentation System'
        ],
        'descriptions': [
            'Comprehensive medical documentation',
            'Record keeping and management',
            'Documentation process and workflow',
            'Medical records and files',
            'File management and organization',
            'Documentation review and update',
            'Medical files and records',
            'Record maintenance and upkeep',
            'Documentation update and revision',
            'Medical reports and documentation',
            'File organization and structure',
            'Documentation system and process'
        ],
        'locations': [
            'Medical Office', 'Records Room', 'Documentation Center',
            'File Storage', 'Records Area', 'Documentation Room',
            'Medical Suite', 'File Management', 'Records Center'
        ]
    },
    'other': {
        'titles': [
            'General Activity', 'Daily Operations', 'Regular Activities',
            'General Operations', 'Daily Tasks', 'Regular Procedures',
            'General Work', 'Daily Routine', 'Regular Work',
            'General Activities', 'Daily Functions', 'Regular Operations'
        ],
        'descriptions': [
            'General activities and operations',
            'Daily operations and tasks',
            'Regular activities and procedures',
            'General operations and work',
            'Daily tasks and functions',
            'Regular procedures and activities',
            'General work and operations',
            'Daily routine and tasks',
            'Regular work and activities',
            'General activities and functions',
            'Daily functions and operations',
            'Regular operations and work'
        ],
        'locations': [
            'General Area', 'Office Space', 'Work Area',
            'Operations Center', 'Work Space', 'Activity Area',
            'General Office', 'Work Room', 'Operations Area'
        ]
    }
}

# Album themes and descriptions
ALBUM_THEMES = {
    'medical': [
        ('Medical Consultations 2024', 'Collection of medical consultation sessions and patient care activities'),
        ('Clinical Procedures', 'Documentation of various clinical procedures and medical treatments'),
        ('Medical Team Activities', 'Medical team collaboration and professional activities'),
        ('Patient Care Sessions', 'Comprehensive patient care and treatment sessions'),
        ('Medical Equipment Usage', 'Medical equipment setup, usage, and maintenance'),
        ('Emergency Response', 'Emergency medical response and critical care activities'),
        ('Medical Training', 'Medical training sessions and professional development'),
        ('Health Assessments', 'Patient health assessments and medical evaluations'),
        ('Medical Documentation', 'Medical documentation and record keeping activities'),
        ('Treatment Sessions', 'Various treatment sessions and medical interventions')
    ],
    'event': [
        ('Health Awareness Events', 'Community health awareness and education events'),
        ('Medical Workshops', 'Professional medical workshops and training sessions'),
        ('Community Health Day', 'Community health day activities and events'),
        ('Medical Conferences', 'Medical conferences and professional meetings'),
        ('Health Fairs', 'Health fairs and community health activities'),
        ('Training Sessions', 'Professional training and development sessions'),
        ('Team Building Events', 'Team building and collaboration activities'),
        ('Medical Outreach', 'Medical outreach and community service activities'),
        ('Health Education', 'Health education and awareness programs'),
        ('Community Meetings', 'Community health meetings and discussions')
    ],
    'infrastructure': [
        ('Facility Development', 'Medical facility development and infrastructure projects'),
        ('Equipment Installation', 'Medical equipment installation and setup processes'),
        ('Facility Maintenance', 'Facility maintenance and improvement activities'),
        ('Medical Center Setup', 'Medical center setup and configuration'),
        ('Equipment Setup', 'Medical equipment setup and configuration'),
        ('Facility Upgrades', 'Facility upgrade and improvement projects'),
        ('Medical Office Space', 'Medical office space and layout development'),
        ('Equipment Maintenance', 'Equipment maintenance and service activities'),
        ('Facility Expansion', 'Facility expansion and development projects'),
        ('Medical Laboratory', 'Medical laboratory setup and equipment')
    ],
    'team': [
        ('Medical Team Activities', 'Medical team collaboration and activities'),
        ('Staff Meetings', 'Staff meetings and coordination sessions'),
        ('Team Training', 'Team training and development activities'),
        ('Staff Development', 'Staff development and professional growth'),
        ('Medical Professionals', 'Medical professionals at work'),
        ('Team Building', 'Team building and collaboration activities'),
        ('Staff Workshops', 'Staff workshops and learning sessions'),
        ('Medical Personnel', 'Medical personnel coordination and activities'),
        ('Team Coordination', 'Team coordination and planning sessions'),
        ('Staff Activities', 'Staff activities and professional development')
    ],
    'patient': [
        ('Patient Care Activities', 'Comprehensive patient care and support activities'),
        ('Patient Consultations', 'Patient consultation and assessment sessions'),
        ('Patient Treatment', 'Patient treatment and care activities'),
        ('Patient Support', 'Patient support and assistance activities'),
        ('Patient Education', 'Patient education and guidance sessions'),
        ('Patient Monitoring', 'Patient monitoring and observation activities'),
        ('Patient Assessment', 'Patient assessment and evaluation sessions'),
        ('Patient Recovery', 'Patient recovery and rehabilitation activities'),
        ('Patient Follow-up', 'Patient follow-up and monitoring sessions'),
        ('Patient Care Team', 'Patient care team activities and coordination')
    ],
    'equipment': [
        ('Medical Equipment', 'Medical equipment and technology usage'),
        ('Equipment Setup', 'Medical equipment setup and configuration'),
        ('Equipment Maintenance', 'Equipment maintenance and service activities'),
        ('Medical Devices', 'Medical devices and technology usage'),
        ('Equipment Testing', 'Equipment testing and validation activities'),
        ('Equipment Installation', 'Equipment installation and setup processes'),
        ('Medical Technology', 'Medical technology and innovation'),
        ('Equipment Calibration', 'Equipment calibration and setup'),
        ('Equipment Training', 'Equipment training and education'),
        ('Medical Instruments', 'Medical instruments and tools usage')
    ],
    'documentation': [
        ('Medical Documentation', 'Medical documentation and record keeping'),
        ('Record Keeping', 'Record keeping and file management activities'),
        ('Documentation Process', 'Documentation process and workflow'),
        ('Medical Records', 'Medical records and file management'),
        ('File Management', 'File management and organization activities'),
        ('Documentation Review', 'Documentation review and update activities'),
        ('Medical Files', 'Medical files and records management'),
        ('Record Maintenance', 'Record maintenance and upkeep activities'),
        ('Documentation Update', 'Documentation update and revision activities'),
        ('Medical Reports', 'Medical reports and documentation activities')
    ],
    'other': [
        ('General Activities', 'General activities and daily operations'),
        ('Daily Operations', 'Daily operations and regular activities'),
        ('Regular Activities', 'Regular activities and procedures'),
        ('General Operations', 'General operations and work activities'),
        ('Daily Tasks', 'Daily tasks and functions'),
        ('Regular Procedures', 'Regular procedures and activities'),
        ('General Work', 'General work and operations'),
        ('Daily Routine', 'Daily routine and tasks'),
        ('Regular Work', 'Regular work and activities'),
        ('General Functions', 'General functions and operations')
    ]
}

def create_fake_image(category, width=800, height=600):
    """Create a fake image for the given category"""
    # Create a base image with category-specific colors
    colors = {
        'medical': [(0, 123, 255), (220, 53, 69), (255, 193, 7)],  # Blue, Red, Yellow
        'event': [(40, 167, 69), (255, 193, 7), (220, 53, 69)],    # Green, Yellow, Red
        'infrastructure': [(108, 117, 125), (52, 58, 64), (73, 80, 87)],  # Grays
        'team': [(255, 193, 7), (40, 167, 69), (0, 123, 255)],     # Yellow, Green, Blue
        'patient': [(220, 53, 69), (255, 193, 7), (40, 167, 69)],  # Red, Yellow, Green
        'equipment': [(108, 117, 125), (0, 123, 255), (52, 58, 64)], # Gray, Blue, Dark Gray
        'documentation': [(73, 80, 87), (108, 117, 125), (52, 58, 64)], # Grays
        'other': [(108, 117, 125), (73, 80, 87), (52, 58, 64)]     # Grays
    }
    
    # Create image with gradient background
    img = Image.new('RGB', (width, height), colors[category][0])
    draw = ImageDraw.Draw(img)
    
    # Add some geometric shapes to make it look more interesting
    for i in range(5):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = random.choice(colors[category])
        draw.rectangle([x1, y1, x2, y2], fill=color, outline=None)
    
    # Add some circles
    for i in range(3):
        x = random.randint(50, width-50)
        y = random.randint(50, height-50)
        radius = random.randint(20, 80)
        color = random.choice(colors[category])
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
    
    # Add category text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
    
    text = category.upper()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text with background
    draw.rectangle([x-10, y-10, x+text_width+10, y+text_height+10], fill=(255, 255, 255))
    draw.text((x, y), text, fill=(0, 0, 0), font=font)
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=85)
    img_byte_arr.seek(0)
    
    return img_byte_arr

def create_photo_tags():
    """Create photo tags for categorization"""
    tags_data = [
        # Medical tags
        ('medical-consultation', 'Medical consultations and patient care', '#007bff'),
        ('clinical-procedure', 'Clinical procedures and treatments', '#dc3545'),
        ('patient-care', 'Patient care and support activities', '#28a745'),
        ('medical-equipment', 'Medical equipment and devices', '#6c757d'),
        ('emergency-response', 'Emergency medical response', '#dc3545'),
        ('medical-training', 'Medical training and education', '#17a2b8'),
        
        # Event tags
        ('health-awareness', 'Health awareness and education events', '#28a745'),
        ('medical-workshop', 'Medical workshops and training', '#ffc107'),
        ('community-health', 'Community health activities', '#28a745'),
        ('medical-conference', 'Medical conferences and meetings', '#007bff'),
        ('health-fair', 'Health fairs and community events', '#fd7e14'),
        ('team-building', 'Team building activities', '#6f42c1'),
        
        # Infrastructure tags
        ('facility-development', 'Facility development and infrastructure', '#6c757d'),
        ('equipment-setup', 'Equipment setup and installation', '#495057'),
        ('facility-maintenance', 'Facility maintenance and upkeep', '#6c757d'),
        ('medical-center', 'Medical center and office space', '#343a40'),
        ('equipment-maintenance', 'Equipment maintenance and service', '#495057'),
        ('facility-expansion', 'Facility expansion and development', '#6c757d'),
        
        # Team tags
        ('medical-team', 'Medical team activities', '#007bff'),
        ('staff-meeting', 'Staff meetings and coordination', '#28a745'),
        ('team-training', 'Team training and development', '#ffc107'),
        ('staff-development', 'Staff development and growth', '#17a2b8'),
        ('medical-professionals', 'Medical professionals at work', '#6f42c1'),
        ('team-coordination', 'Team coordination and planning', '#fd7e14'),
        
        # Patient tags
        ('patient-care', 'Patient care and support', '#28a745'),
        ('patient-consultation', 'Patient consultation and assessment', '#007bff'),
        ('patient-treatment', 'Patient treatment and care', '#dc3545'),
        ('patient-education', 'Patient education and guidance', '#17a2b8'),
        ('patient-monitoring', 'Patient monitoring and observation', '#6c757d'),
        ('patient-recovery', 'Patient recovery and rehabilitation', '#28a745'),
        
        # Equipment tags
        ('medical-equipment', 'Medical equipment and devices', '#6c757d'),
        ('equipment-setup', 'Equipment setup and configuration', '#495057'),
        ('equipment-maintenance', 'Equipment maintenance and service', '#6c757d'),
        ('medical-devices', 'Medical devices and technology', '#343a40'),
        ('equipment-testing', 'Equipment testing and validation', '#495057'),
        ('equipment-calibration', 'Equipment calibration and setup', '#6c757d'),
        
        # Documentation tags
        ('medical-documentation', 'Medical documentation and records', '#6c757d'),
        ('record-keeping', 'Record keeping and file management', '#495057'),
        ('documentation-process', 'Documentation process and workflow', '#6c757d'),
        ('medical-records', 'Medical records and files', '#343a40'),
        ('file-management', 'File management and organization', '#495057'),
        ('documentation-review', 'Documentation review and update', '#6c757d'),
        
        # General tags
        ('general-activity', 'General activities and operations', '#6c757d'),
        ('daily-operations', 'Daily operations and tasks', '#495057'),
        ('regular-activities', 'Regular activities and procedures', '#6c757d'),
        ('general-work', 'General work and operations', '#343a40'),
        ('daily-tasks', 'Daily tasks and functions', '#495057'),
        ('regular-procedures', 'Regular procedures and activities', '#6c757d')
    ]
    
    tags = []
    for name, description, color in tags_data:
        tag, created = PhotoTag.objects.get_or_create(
            name=name,
            defaults={
                'description': description,
                'color': color
            }
        )
        tags.append(tag)
    
    return tags

def create_photo_albums(moze_list, users):
    """Create photo albums for each moze"""
    albums = []
    
    for moze in moze_list:
        # Get users associated with this moze
        moze_users = [user for user in users if hasattr(user, 'managed_mozes') and moze in user.managed_mozes.all()]
        if not moze_users:
            moze_users = [user for user in users if user.role in ['admin', 'aamil', 'moze_coordinator']]
        
        creator = random.choice(moze_users) if moze_users else random.choice(users)
        
        # Create albums for each category
        for category in PHOTO_CATEGORIES.keys():
            theme_count = random.randint(1, 3)  # 1-3 albums per category
            for i in range(theme_count):
                theme_name, theme_description = random.choice(ALBUM_THEMES[category])
                
                # Add moze name to make it unique
                album_name = f"{theme_name} - {moze.name}"
                
                album = PhotoAlbum.objects.create(
                    name=album_name,
                    description=f"{theme_description} at {moze.name}",
                    moze=moze,
                    created_by=creator,
                    is_public=random.choice([True, False]),
                    allow_uploads=random.choice([True, False]),
                    event_date=fake.date_between(start_date='-1y', end_date='today')
                )
                albums.append(album)
    
    return albums

def create_photos(albums, users, tags):
    """Create photos for each album"""
    photos = []
    
    for album in albums:
        # Determine number of photos for this album
        photo_count = random.randint(*PHOTO_DATA_SPECS['photos_per_album'])
        
        # Get users who can upload to this album
        uploaders = [user for user in users if user.role in ['admin', 'aamil', 'moze_coordinator'] or user == album.created_by]
        
        for i in range(photo_count):
            # Determine category based on album name
            category = 'other'
            for cat in PHOTO_CATEGORIES.keys():
                if cat in album.name.lower():
                    category = cat
                    break
            
            # Get category-specific data
            cat_data = PHOTO_CATEGORIES[category]
            title = random.choice(cat_data['titles'])
            description = random.choice(cat_data['descriptions'])
            location = random.choice(cat_data['locations'])
            
            # Create fake image
            img_data = create_fake_image(category)
            
            # Create photo object
            photo = Photo(
                title=title,
                description=description,
                subject_tag=f"{category}-{i+1}",
                moze=album.moze,
                uploaded_by=random.choice(uploaders),
                location=f"{location} at {album.moze.name}",
                event_date=fake.date_between(start_date='-6m', end_date='today'),
                photographer=random.choice(uploaders).get_full_name(),
                category=category,
                is_public=random.choice([True, False]),
                is_featured=random.choice([True, False]) if random.random() < 0.1 else False,
                requires_permission=random.choice([True, False]),
                file_size=len(img_data.getvalue()),
                image_width=800,
                image_height=600
            )
            
            # Save the photo
            photo.save()
            
            # Add image file
            photo.image.save(
                f"{category}_{album.moze.id}_{i+1}.jpg",
                ContentFile(img_data.getvalue()),
                save=True
            )
            
            # Add to album
            album.photos.add(photo)
            
            # Add random tags
            photo_tags = random.sample(tags, random.randint(1, 3))
            photo.tags.set(photo_tags)
            
            photos.append(photo)
    
    return photos

def create_photo_comments(photos, users):
    """Create comments for photos"""
    comments = []
    
    for photo in photos:
        comment_count = random.randint(*PHOTO_DATA_SPECS['comments_per_photo'])
        
        for i in range(comment_count):
            comment = PhotoComment.objects.create(
                photo=photo,
                author=random.choice(users),
                content=fake.text(max_nb_chars=200),
                is_active=random.choice([True, False])
            )
            comments.append(comment)
    
    return comments

def create_photo_likes(photos, users):
    """Create likes for photos"""
    likes = []
    
    for photo in photos:
        like_count = random.randint(*PHOTO_DATA_SPECS['likes_per_photo'])
        likers = random.sample(users, min(like_count, len(users)))
        
        for liker in likers:
            like, created = PhotoLike.objects.get_or_create(
                photo=photo,
                user=liker
            )
            if created:
                likes.append(like)
    
    return likes

def create_photos_fake_data():
    """Create comprehensive fake data for photos app"""
    print("📸 Starting photos fake data generation...")
    print(f"📊 Data volumes: {PHOTO_DATA_SPECS}")
    
    try:
        with transaction.atomic():
            # Step 1: Get existing data
            print("\n👥 Getting existing users and moze...")
            users = list(User.objects.filter(is_active=True))
            moze_list = list(Moze.objects.filter(is_active=True))
            
            if not users:
                print("❌ No users found. Please create users first.")
                return
            
            if not moze_list:
                print("❌ No moze found. Please create moze first.")
                return
            
            # Step 2: Create photo tags
            print(f"\n🏷️ Creating {PHOTO_DATA_SPECS['tags_count']} photo tags...")
            tags = create_photo_tags()
            
            # Step 3: Create photo albums
            print(f"\n📁 Creating photo albums...")
            albums = create_photo_albums(moze_list, users)
            
            # Step 4: Create photos
            print(f"\n📸 Creating photos for albums...")
            photos = create_photos(albums, users, tags)
            
            # Step 5: Create comments
            print(f"\n💬 Creating photo comments...")
            comments = create_photo_comments(photos, users)
            
            # Step 6: Create likes
            print(f"\n❤️ Creating photo likes...")
            likes = create_photo_likes(photos, users)
            
            # Print summary
            print("\n" + "="*50)
            print("📊 PHOTOS FAKE DATA GENERATION SUMMARY")
            print("="*50)
            print(f"📁 Albums created: {len(albums)}")
            print(f"📸 Photos created: {len(photos)}")
            print(f"🏷️ Tags created: {len(tags)}")
            print(f"💬 Comments created: {len(comments)}")
            print(f"❤️ Likes created: {len(likes)}")
            print(f"👥 Users involved: {len(set([p.uploaded_by for p in photos]))}")
            print(f"🏢 Moze involved: {len(set([p.moze for p in photos]))}")
            
            # Category breakdown
            category_counts = {}
            for photo in photos:
                category_counts[photo.category] = category_counts.get(photo.category, 0) + 1
            
            print(f"\n📊 Photos by category:")
            for category, count in category_counts.items():
                print(f"  {category}: {count}")
            
            print("\n✅ Photos fake data generation completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during photos fake data generation: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    create_photos_fake_data()