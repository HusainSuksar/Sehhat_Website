from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.core.files.base import ContentFile
import random
from faker import Faker

from moze.models import Moze
from photos.models import PhotoAlbum, Photo, PhotoTag, PhotoComment, PhotoLike

User = get_user_model()
fake = Faker(['en_US', 'ar_SA'])

# Data specifications
PHOTO_DATA_SPECS = {
    'albums_count': 20,
    'photos_per_album': (3, 10),  # Range of photos per album
    'tags_count': 15,
    'comments_per_photo': (0, 5),  # Range of comments per photo
    'likes_per_photo': (0, 8),     # Range of likes per photo
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
    ],
    'event': [
        ('Health Awareness Events', 'Community health awareness and education events'),
        ('Medical Workshops', 'Professional medical workshops and training sessions'),
        ('Community Health Day', 'Community health day activities and events'),
        ('Medical Conferences', 'Medical conferences and professional meetings'),
        ('Health Fairs', 'Health fairs and community health activities'),
    ],
    'team': [
        ('Medical Team Activities', 'Medical team collaboration and activities'),
        ('Staff Meetings', 'Staff meetings and coordination sessions'),
        ('Team Training', 'Team training and development activities'),
        ('Staff Development', 'Staff development and professional growth'),
        ('Medical Professionals', 'Medical professionals at work'),
    ],
    'patient': [
        ('Patient Care Activities', 'Comprehensive patient care and support activities'),
        ('Patient Consultations', 'Patient consultation and assessment sessions'),
        ('Patient Treatment', 'Patient treatment and care activities'),
        ('Patient Support', 'Patient support and assistance activities'),
        ('Patient Education', 'Patient education and guidance sessions'),
    ],
    'other': [
        ('General Activities', 'General activities and daily operations'),
        ('Daily Operations', 'Daily operations and regular activities'),
        ('Regular Activities', 'Regular activities and procedures'),
        ('General Operations', 'General operations and work activities'),
        ('Daily Tasks', 'Daily tasks and functions'),
    ]
}

def create_fake_image_data():
    """Create a simple fake image data (1x1 pixel JPEG)"""
    # Minimal JPEG data for a 1x1 pixel image
    jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
    return ContentFile(jpeg_data)

def create_photo_tags():
    """Create photo tags for categorization"""
    tags_data = [
        # Medical tags
        ('medical-consultation', 'Medical consultations and patient care', '#007bff'),
        ('clinical-procedure', 'Clinical procedures and treatments', '#dc3545'),
        ('patient-care', 'Patient care and support activities', '#28a745'),
        ('medical-equipment', 'Medical equipment and devices', '#6c757d'),
        ('emergency-response', 'Emergency medical response', '#dc3545'),
        
        # Event tags
        ('health-awareness', 'Health awareness and education events', '#28a745'),
        ('medical-workshop', 'Medical workshops and training', '#ffc107'),
        ('community-health', 'Community health activities', '#28a745'),
        ('medical-conference', 'Medical conferences and meetings', '#007bff'),
        ('health-fair', 'Health fairs and community events', '#fd7e14'),
        
        # Team tags
        ('medical-team', 'Medical team activities', '#007bff'),
        ('staff-meeting', 'Staff meetings and coordination', '#28a745'),
        ('team-training', 'Team training and development', '#ffc107'),
        ('staff-development', 'Staff development and growth', '#17a2b8'),
        ('medical-professionals', 'Medical professionals at work', '#6f42c1'),
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
        moze_users = [user for user in users if user.role in ['admin', 'aamil', 'moze_coordinator']]
        if not moze_users:
            moze_users = users
        
        creator = random.choice(moze_users) if moze_users else random.choice(users)
        
        # Create albums for each category
        for category in ['medical', 'event', 'team', 'patient', 'other']:
            theme_count = random.randint(1, 2)  # 1-2 albums per category
            for i in range(theme_count):
                theme_name, theme_description = random.choice(ALBUM_THEMES[category])
                
                # Add moze name, timestamp, and random suffix to make it unique
                album_name = f"{theme_name} - {moze.name} - {fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m')} - {random.randint(1000, 9999)}"
                
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
            
            # Create fake image data
            img_data = create_fake_image_data()
            
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
                file_size=len(img_data.read()),
                image_width=1,
                image_height=1
            )
            
            # Reset file pointer
            img_data.seek(0)
            
            # Save the photo
            photo.save()
            
            # Add image file
            photo.image.save(
                f"{category}_{album.moze.id}_{i+1}.jpg",
                img_data,
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

class Command(BaseCommand):
    help = 'Generate fake photos data for testing and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--albums',
            type=int,
            default=20,
            help='Number of albums to create (default: 20)'
        )
        parser.add_argument(
            '--photos-per-album',
            type=int,
            nargs=2,
            default=[3, 10],
            help='Range of photos per album (default: 3 10)'
        )
        parser.add_argument(
            '--tags',
            type=int,
            default=15,
            help='Number of tags to create (default: 15)'
        )
        parser.add_argument(
            '--comments-per-photo',
            type=int,
            nargs=2,
            default=[0, 5],
            help='Range of comments per photo (default: 0 5)'
        )
        parser.add_argument(
            '--likes-per-photo',
            type=int,
            nargs=2,
            default=[0, 8],
            help='Range of likes per photo (default: 0 8)'
        )

    def handle(self, *args, **options):
        # Update data specs with command line arguments
        PHOTO_DATA_SPECS.update({
            'albums_count': options['albums'],
            'photos_per_album': tuple(options['photos_per_album']),
            'tags_count': options['tags'],
            'comments_per_photo': tuple(options['comments_per_photo']),
            'likes_per_photo': tuple(options['likes_per_photo']),
        })
        
        self.stdout.write("📸 Starting photos fake data generation...")
        self.stdout.write(f"📊 Data volumes: {PHOTO_DATA_SPECS}")
        
        try:
            with transaction.atomic():
                # Step 1: Get existing data
                self.stdout.write("\n👥 Getting existing users and moze...")
                users = list(User.objects.filter(is_active=True))
                moze_list = list(Moze.objects.filter(is_active=True))
                
                if not users:
                    self.stdout.write(self.style.ERROR("❌ No users found. Please create users first."))
                    return
                
                if not moze_list:
                    self.stdout.write(self.style.ERROR("❌ No moze found. Please create moze first."))
                    return
                
                # Step 2: Create photo tags
                self.stdout.write(f"\n🏷️ Creating {PHOTO_DATA_SPECS['tags_count']} photo tags...")
                tags = create_photo_tags()
                
                # Step 3: Create photo albums
                self.stdout.write(f"\n📁 Creating photo albums...")
                albums = create_photo_albums(moze_list, users)
                
                # Step 4: Create photos
                self.stdout.write(f"\n📸 Creating photos for albums...")
                photos = create_photos(albums, users, tags)
                
                # Step 5: Create comments
                self.stdout.write(f"\n💬 Creating photo comments...")
                comments = create_photo_comments(photos, users)
                
                # Step 6: Create likes
                self.stdout.write(f"\n❤️ Creating photo likes...")
                likes = create_photo_likes(photos, users)
                
                # Print summary
                self.stdout.write("\n" + "="*50)
                self.stdout.write("📊 PHOTOS FAKE DATA GENERATION SUMMARY")
                self.stdout.write("="*50)
                self.stdout.write(f"📁 Albums created: {len(albums)}")
                self.stdout.write(f"📸 Photos created: {len(photos)}")
                self.stdout.write(f"🏷️ Tags created: {len(tags)}")
                self.stdout.write(f"💬 Comments created: {len(comments)}")
                self.stdout.write(f"❤️ Likes created: {len(likes)}")
                self.stdout.write(f"👥 Users involved: {len(set([p.uploaded_by for p in photos]))}")
                self.stdout.write(f"🏢 Moze involved: {len(set([p.moze for p in photos]))}")
                
                # Category breakdown
                category_counts = {}
                for photo in photos:
                    category_counts[photo.category] = category_counts.get(photo.category, 0) + 1
                
                self.stdout.write(f"\n📊 Photos by category:")
                for category, count in category_counts.items():
                    self.stdout.write(f"  {category}: {count}")
                
                self.stdout.write(self.style.SUCCESS("\n✅ Photos fake data generation completed successfully!"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error during photos fake data generation: {str(e)}"))
            import traceback
            traceback.print_exc()