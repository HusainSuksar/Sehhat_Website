# Photos App Fake Data Generator

This directory contains comprehensive fake data generators for your photos app. The generators create realistic fake images, albums, metadata, and social interactions for testing and development.

## 📁 Files Overview

### 1. `photos_fake_data_generator.py` (Comprehensive Version)
- **Features**: Full image generation with PIL, realistic fake images for each category
- **Dependencies**: Requires Pillow for image generation
- **Use Case**: When you need realistic-looking images for testing

### 2. `photos_fake_data_simple.py` (Simple Version)
- **Features**: Minimal image data, faster execution, no external dependencies
- **Dependencies**: Only requires Faker (already in your project)
- **Use Case**: Quick testing without image generation overhead

### 3. `photos_requirements.txt`
- **Purpose**: Lists additional dependencies needed for the comprehensive version
- **Installation**: `pip install -r photos_requirements.txt`

## 🚀 Quick Start

### Option 1: Simple Version (Recommended for testing)
```bash
# Run the simple version (no additional dependencies needed)
python photos_fake_data_simple.py
```

### Option 2: Comprehensive Version (With realistic images)
```bash
# Install additional dependencies
pip install -r photos_requirements.txt

# Run the comprehensive version
python photos_fake_data_generator.py
```

## 📊 What Gets Generated

### 1. Photo Tags (15-30 tags)
- **Medical tags**: medical-consultation, clinical-procedure, patient-care, etc.
- **Event tags**: health-awareness, medical-workshop, community-health, etc.
- **Team tags**: medical-team, staff-meeting, team-training, etc.
- **Equipment tags**: medical-equipment, equipment-setup, equipment-maintenance, etc.
- **Documentation tags**: medical-documentation, record-keeping, etc.

### 2. Photo Albums (20-50 albums)
- **Themed albums**: Medical Consultations, Health Awareness Events, Team Activities, etc.
- **Per Moze**: Multiple albums per medical center
- **Categories**: medical, event, team, patient, infrastructure, equipment, documentation, other

### 3. Photos (100-500+ photos)
- **Realistic metadata**: Titles, descriptions, locations, dates, photographers
- **Categories**: 8 different categories with specific content
- **File information**: Size, dimensions, upload dates
- **Privacy settings**: Public/private, featured, permission requirements

### 4. Social Interactions
- **Comments**: 0-8 comments per photo with realistic content
- **Likes**: 0-15 likes per photo from different users
- **User relationships**: Proper user permissions and ownership

### 5. Fake Images (Comprehensive version only)
- **Category-specific**: Different colors and designs for each category
- **Realistic dimensions**: 800x600 pixels
- **JPEG format**: Optimized for web display
- **Visual elements**: Geometric shapes, text labels, color schemes

## 🎨 Photo Categories

### Medical
- **Colors**: Blue, Red, Yellow theme
- **Content**: Consultations, procedures, treatments, equipment
- **Locations**: Medical centers, consultation rooms, treatment areas

### Event
- **Colors**: Green, Yellow, Red theme
- **Content**: Workshops, conferences, health fairs, community events
- **Locations**: Community centers, conference halls, public spaces

### Team
- **Colors**: Yellow, Green, Blue theme
- **Content**: Staff meetings, team training, collaboration
- **Locations**: Conference rooms, team spaces, meeting areas

### Patient
- **Colors**: Red, Yellow, Green theme
- **Content**: Patient care, consultations, support, education
- **Locations**: Patient care areas, consultation rooms, support centers

### Infrastructure
- **Colors**: Gray theme
- **Content**: Facility development, equipment installation, maintenance
- **Locations**: Medical centers, laboratories, equipment rooms

### Equipment
- **Colors**: Gray, Blue theme
- **Content**: Medical devices, setup, maintenance, testing
- **Locations**: Equipment rooms, laboratories, technology centers

### Documentation
- **Colors**: Gray theme
- **Content**: Record keeping, file management, documentation
- **Locations**: Medical offices, records rooms, documentation centers

### Other
- **Colors**: Gray theme
- **Content**: General activities, daily operations, regular tasks
- **Locations**: General areas, office spaces, work areas

## 🔧 Configuration

### Data Volumes (Simple Version)
```python
PHOTO_DATA_SPECS = {
    'albums_count': 20,
    'photos_per_album': (3, 10),  # Range of photos per album
    'tags_count': 15,
    'comments_per_photo': (0, 5),  # Range of comments per photo
    'likes_per_photo': (0, 8),     # Range of likes per photo
}
```

### Data Volumes (Comprehensive Version)
```python
PHOTO_DATA_SPECS = {
    'albums_count': 50,
    'photos_per_album': (5, 25),  # Range of photos per album
    'tags_count': 30,
    'comments_per_photo': (0, 8),  # Range of comments per photo
    'likes_per_photo': (0, 15),    # Range of likes per photo
    'users_per_moze': (3, 8),      # Range of users per moze
}
```

## 🎯 Usage Examples

### 1. Generate Test Data for Development
```bash
# Quick test data
python photos_fake_data_simple.py
```

### 2. Generate Comprehensive Data for Testing
```bash
# Full test data with realistic images
python photos_fake_data_generator.py
```

### 3. Customize Data Volumes
Edit the `PHOTO_DATA_SPECS` in either file to adjust:
- Number of albums
- Photos per album
- Comments and likes per photo
- Number of tags

### 4. Add Custom Categories
Modify `PHOTO_CATEGORIES` to add new categories with:
- Custom titles and descriptions
- Specific locations
- Category-specific colors (comprehensive version)

## 📈 Expected Output

### Simple Version
```
📸 Starting photos fake data generation...
📊 Data volumes: {'albums_count': 20, 'photos_per_album': (3, 10), ...}

👥 Getting existing users and moze...
🏷️ Creating 15 photo tags...
📁 Creating photo albums...
📸 Creating photos for albums...
💬 Creating photo comments...
❤️ Creating photo likes...

==================================================
📊 PHOTOS FAKE DATA GENERATION SUMMARY
==================================================
📁 Albums created: 45
📸 Photos created: 234
🏷️ Tags created: 15
💬 Comments created: 456
❤️ Likes created: 1234
👥 Users involved: 8
🏢 Moze involved: 5

📊 Photos by category:
  medical: 45
  event: 38
  team: 42
  patient: 35
  other: 74

✅ Photos fake data generation completed successfully!
```

### Comprehensive Version
```
📸 Starting photos fake data generation...
📊 Data volumes: {'albums_count': 50, 'photos_per_album': (5, 25), ...}

👥 Getting existing users and moze...
🏷️ Creating 30 photo tags...
📁 Creating photo albums...
📸 Creating photos for albums...
💬 Creating photo comments...
❤️ Creating photo likes...

==================================================
📊 PHOTOS FAKE DATA GENERATION SUMMARY
==================================================
📁 Albums created: 125
📸 Photos created: 1876
🏷️ Tags created: 30
💬 Comments created: 8234
❤️ Likes created: 15678
👥 Users involved: 12
🏢 Moze involved: 8

📊 Photos by category:
  medical: 234
  event: 198
  team: 245
  patient: 187
  infrastructure: 156
  equipment: 134
  documentation: 123
  other: 599

✅ Photos fake data generation completed successfully!
```

## 🔍 Verification

After running the generator, you can verify the data:

### 1. Check Django Admin
- Go to `/admin/photos/`
- Verify albums, photos, tags, comments, and likes

### 2. Check Photos App
- Navigate to your photos app
- Browse albums and photos
- Test search and filtering

### 3. Database Queries
```python
# Check photo counts
from photos.models import Photo, PhotoAlbum, PhotoTag
print(f"Photos: {Photo.objects.count()}")
print(f"Albums: {PhotoAlbum.objects.count()}")
print(f"Tags: {PhotoTag.objects.count()}")

# Check by category
from django.db.models import Count
photos_by_category = Photo.objects.values('category').annotate(count=Count('id'))
for item in photos_by_category:
    print(f"{item['category']}: {item['count']}")
```

## 🛠️ Troubleshooting

### Common Issues

1. **No users found**
   - Ensure you have active users in your database
   - Run your existing test data generator first

2. **No moze found**
   - Ensure you have active moze in your database
   - Run your existing test data generator first

3. **PIL/Pillow import error**
   - Install Pillow: `pip install Pillow`
   - Or use the simple version instead

4. **Permission errors**
   - Ensure the media directory is writable
   - Check Django media settings

### Performance Tips

1. **For large datasets**: Use the simple version for faster generation
2. **For realistic images**: Use the comprehensive version
3. **Memory usage**: Adjust photo counts in `PHOTO_DATA_SPECS`
4. **Database size**: Monitor database growth with large datasets

## 🎨 Customization

### Adding New Categories
1. Add category to `PHOTO_CATEGORIES`
2. Add album themes to `ALBUM_THEMES`
3. Add color scheme to image generation (comprehensive version)

### Modifying Content
1. Edit titles, descriptions, and locations in `PHOTO_CATEGORIES`
2. Adjust album themes in `ALBUM_THEMES`
3. Modify tag data in `create_photo_tags()`

### Changing Data Volumes
1. Modify `PHOTO_DATA_SPECS`
2. Adjust ranges for photos, comments, likes
3. Change album counts per category

## 📝 Notes

- **Safe to run multiple times**: Uses `get_or_create` to avoid duplicates
- **Transaction safety**: All operations wrapped in database transaction
- **User relationships**: Properly links to existing users and moze
- **File storage**: Images stored in Django media directory
- **Performance**: Simple version is much faster for testing

## 🤝 Contributing

To extend the fake data generator:

1. Add new categories to `PHOTO_CATEGORIES`
2. Create new album themes in `ALBUM_THEMES`
3. Add new tags in `create_photo_tags()`
4. Customize image generation in `create_fake_image()` (comprehensive version)

The generators are designed to be easily extensible and maintainable for your specific needs.