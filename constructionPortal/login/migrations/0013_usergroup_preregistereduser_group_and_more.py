# Generated by Django 4.2.17 on 2025-02-01 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0012_billing_estimated_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'User Group',
                'verbose_name_plural': 'User Groups',
            },
        ),
        migrations.AddField(
            model_name='preregistereduser',
            name='group',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.usergroup'),
        ),
        migrations.AddField(
            model_name='userregistration',
            name='group',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='login.usergroup'),
        ),
    ]
