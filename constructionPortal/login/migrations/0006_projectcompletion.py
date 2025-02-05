# Generated by Django 5.1.4 on 2024-12-22 15:48

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_materialsandresources'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectCompletion',
            fields=[
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='login.project')),
                ('before_after_completion', models.FileField(blank=True, null=True, upload_to='completion_files/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])])),
                ('completion_proof', models.FileField(blank=True, null=True, upload_to='completion_proofs/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])])),
                ('client_rating', models.IntegerField(blank=True, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], null=True)),
                ('client_feedback', models.TextField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
