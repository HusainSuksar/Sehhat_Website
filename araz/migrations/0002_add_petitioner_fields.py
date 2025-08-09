# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('araz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='petitioner_name',
            field=models.CharField(help_text='Full name of the petitioner', max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='petition',
            name='petitioner_mobile',
            field=models.CharField(blank=True, help_text='Mobile number of the petitioner', max_length=20),
        ),
        migrations.AddField(
            model_name='petition',
            name='petitioner_email',
            field=models.EmailField(blank=True, help_text='Email address of the petitioner', max_length=254),
        ),
        migrations.AddField(
            model_name='petition',
            name='its_id',
            field=models.CharField(blank=True, help_text='ITS ID if available', max_length=8),
        ),
    ]