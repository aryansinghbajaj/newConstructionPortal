import os
from django.db import models
from django.contrib.auth.hashers import make_password #securely store the hashed password in the database
from django.core.validators import FileExtensionValidator
from django.contrib.auth.hashers import make_password
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal

class UserGroup(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User Group'
        verbose_name_plural = 'User Groups'

class PreRegisteredUser(models.Model):
    userid = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField(unique=True)
    password_sent = models.CharField(max_length=100)
    group = models.ForeignKey(
        UserGroup,
        on_delete=models.CASCADE,
        null=True,  # Allow null temporarily for migration
        default=None  # No default value
    )


    def __str__(self):
        return self.userid

class UserRegistration(models.Model):
    name = models.CharField(max_length=100)
    userid = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    contact_no = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Hashed final password
    group = models.ForeignKey(
        UserGroup,
        on_delete=models.CASCADE,
        null=True,  # Allow null temporarily for migration
        default=None  # No default value
    )

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.userid
  
class Project(models.Model):
    project_id = models.CharField(max_length=50, primary_key=True)
    user = models.ForeignKey(UserRegistration, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_id} - {self.user.userid}"
class MaterialsAndResources(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    required_materials = models.TextField(default="Not Specified")
    labour = models.TextField(default="Not Specified")
    machinery = models.TextField(default="Not Specified")
    equipment = models.TextField(default="Not Specified")
    tools = models.TextField(default="Not Specified")
    consumables = models.TextField(default="Not Specified")

    def __str__(self):
        return f"Materials and Resources for Project {self.project.project_id}"


class ProjectCompletion(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    before_after_completion = models.FileField(
        upload_to='completion_files/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ]  ,
        null  = True,
        blank = True
    )
    completion_proof = models.FileField(
        upload_to='completion_proofs/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
          null = True,
            blank = True  # Removed blank=True and null=True
    )
    client_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
         default= 1 # Removed blank=True and null=True
    )
    client_feedback = models.TextField(default='No feedback provided')  # Removed blank=True and null=True
    uploaded_at = models.DateTimeField(auto_now_add=True)

class WorkExecution(models.Model):
    THROUGH_CHOICES = [
        ('Phone call', 'Phone call'),
        ('Whatsapp', 'Whatsapp'),
        ('Email', 'Email'),
    ]
    
    CLIENT_CHOICES = [
        ('Company', 'Company'),
        ('Institutions', 'Institutions'),
        ('Consultants', 'Consultants'),
        ('Engineers', 'Engineers'),
        ('Architects', 'Architects'),
        ('Individuals', 'Individuals'),
    ]
    
    client_name = models.CharField(max_length=100, default="Not Specified")
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    through = models.CharField(max_length=20, choices=THROUGH_CHOICES, default='Phone call')
    client = models.CharField(max_length=20, choices=CLIENT_CHOICES, default='Individuals')
    time_of_visit = models.TextField(default="Not Specified")
    record = models.TextField(default="Not Specified")
    site_visit_remarks = models.TextField(default="Not Specified")
    identification_of_problems = models.TextField(default="Not Specified")
    solutions = models.TextField(default="Not Specified")
    recommendations = models.TextField(default="Not Specified")
    site_visit_documentation = models.FileField(
        upload_to='site_visit_docs/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])],
        null=True,  # Keep this nullable initially
        blank=True  # Keep this blank initially
    )
    quotation_submission = models.FileField(
        upload_to='quotation_submission/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])],
        null=True,  # Keep this nullable initially
        blank=True  # Keep this blank initially
    )
    quotation_approval = models.FileField(
        upload_to='quotation_approval/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])],
        null=True,  # Keep this nullable initially
        blank=True  # Keep this blank initially
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Billing(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_left = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_expected_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_expected_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate amount_left before saving
        if self.total_amount is not None:
            total_paid = PaymentEntry.objects.filter(billing=self).aggregate(
                total=models.Sum('amount_paid'))['total'] or Decimal('0')
            self.amount_left = self.total_amount - total_paid
        super().save(*args, **kwargs)

class PaymentEntry(models.Model):
    billing = models.ForeignKey(Billing, on_delete=models.CASCADE, related_name='payments')
    serial_no = models.AutoField(primary_key=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    client_detail = models.TextField(null=True, blank=True)
    mode_of_payment = models.CharField(max_length=50, null=True, blank=True)
    payment_proof = models.FileField(
        upload_to='payment_proofs/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
        blank=True,
        null=True
    )
    payment_date = models.DateField(null=True, blank=True)

@receiver([post_save, post_delete], sender=PaymentEntry)
def update_billing_amount_left(sender, instance, **kwargs):
    """Update billing amount_left whenever a payment is saved or deleted"""
    if instance.billing:
        instance.billing.save()  # This will trigger the recalculation in Billing.save()
