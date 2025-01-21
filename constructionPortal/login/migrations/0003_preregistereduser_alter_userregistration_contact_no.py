# Generated by Django 5.1.4 on 2024-12-18 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_userregistration_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreRegisteredUser',
            fields=[
                ('userid', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password_sent', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name='userregistration',
            name='contact_no',
            field=models.CharField(max_length=255),
        ),
    ]
