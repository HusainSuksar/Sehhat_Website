# Generated manually to fix migration conflict

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('moze', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationCriteria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('weight', models.FloatField(default=1.0, help_text='Weight/importance of this criteria (0.1 to 10.0)', validators=[django.core.validators.MinValueValidator(0.1), django.core.validators.MaxValueValidator(10.0)])),
                ('max_score', models.PositiveIntegerField(default=10, help_text='Maximum score for this criteria')),
                ('category', models.CharField(choices=[('infrastructure', 'Infrastructure & Facilities'), ('medical_quality', 'Medical Care Quality'), ('staff_performance', 'Staff Performance'), ('patient_satisfaction', 'Patient Satisfaction'), ('administration', 'Administration & Management'), ('safety', 'Safety & Hygiene'), ('equipment', 'Medical Equipment'), ('accessibility', 'Accessibility & Availability')], default='medical_quality', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Evaluation Criteria',
                'verbose_name_plural': 'Evaluation Criteria',
                'ordering': ['category', 'order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='EvaluationForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('evaluation_type', models.CharField(max_length=20, choices=[('performance', 'Performance Evaluation'), ('satisfaction', 'Satisfaction Survey'), ('quality', 'Quality Assessment'), ('training', 'Training Evaluation'), ('service', 'Service Evaluation'), ('facility', 'Facility Evaluation')])),
                ('target_role', models.CharField(max_length=20, choices=[('all', 'All Users'), ('doctor', 'Doctors'), ('student', 'Students'), ('aamil', 'Aamils'), ('moze_coordinator', 'Moze Coordinators'), ('admin', 'Administrators')], default='all')),
                ('is_active', models.BooleanField(default=True)),
                ('is_anonymous', models.BooleanField(default=False)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluation_period', models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('biannual', 'Bi-annual'), ('annual', 'Annual'), ('special', 'Special Assessment')], default='quarterly')),
                ('overall_grade', models.CharField(blank=True, max_length=2, null=True, choices=[('A+', 'A+ (Excellent - 95-100%)'), ('A', 'A (Very Good - 85-94%)'), ('B', 'B (Good - 75-84%)'), ('C', 'C (Satisfactory - 65-74%)'), ('D', 'D (Needs Improvement - 55-64%)'), ('E', 'E (Unsatisfactory - Below 55%)')])),
                ('overall_score', models.FloatField(default=0.0, help_text='Overall score as percentage (0-100)', validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('infrastructure_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('medical_quality_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('staff_performance_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('patient_satisfaction_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('administration_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('safety_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('equipment_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('accessibility_score', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(100.0)])),
                ('strengths', models.TextField(blank=True, null=True, help_text='Key strengths observed')),
                ('weaknesses', models.TextField(blank=True, null=True, help_text='Areas needing improvement')),
                ('recommendations', models.TextField(blank=True, null=True, help_text='Specific recommendations')),
                ('action_items', models.TextField(blank=True, null=True, help_text='Action items for improvement')),
                ('follow_up_required', models.BooleanField(default=False)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('compliance_issues', models.TextField(blank=True, null=True)),
                ('certification_status', models.CharField(max_length=20, choices=[('certified', 'Certified'), ('provisional', 'Provisional'), ('warning', 'Warning Status'), ('suspended', 'Suspended'), ('revoked', 'Revoked')], default='certified')),
                ('evaluation_date', models.DateField()),
                ('evaluation_duration_hours', models.PositiveIntegerField(default=1, help_text='Duration in hours')),
                ('is_draft', models.BooleanField(default=True)),
                ('is_published', models.BooleanField(default=False)),
                ('is_confidential', models.BooleanField(default=False)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reviewer_notes', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conducted_evaluations', to=settings.AUTH_USER_MODEL)),
                ('moze', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='moze.moze')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_evaluations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-evaluation_date', '-created_at'],
                'unique_together': {('moze', 'evaluation_period', 'evaluation_date')},
            },
        ),
    ]