# Generated manually for adding ITS API fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_profile_photo'),
    ]

    operations = [
        # Remove old arabic_name field and add new ITS fields
        migrations.RemoveField(
            model_name='user',
            name='arabic_name',
        ),
        
        # Add all 21 ITS API fields
        migrations.AddField(
            model_name='user',
            name='arabic_full_name',
            field=models.CharField(blank=True, help_text='Arabic Full Name', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='prefix',
            field=models.CharField(blank=True, help_text='Title prefix (Mr, Mrs, Dr, etc.)', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='marital_status',
            field=models.CharField(blank=True, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='misaq',
            field=models.CharField(blank=True, help_text='Misaq information', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='occupation',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='qualification',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='idara',
            field=models.CharField(blank=True, help_text='Administrative division', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='whatsapp_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='jamaat',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='jamiaat',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='nationality',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='vatan',
            field=models.CharField(blank=True, help_text='Original homeland', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='hifz_sanad',
            field=models.CharField(blank=True, help_text='Quran memorization certificate', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='photograph',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
        migrations.AddField(
            model_name='user',
            name='its_last_sync',
            field=models.DateTimeField(blank=True, help_text='Last time data was synced from ITS API', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='its_sync_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('synced', 'Synced'), ('failed', 'Failed')], default='pending', max_length=20),
        ),
    ]