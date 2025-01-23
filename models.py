import os
from django.db import models
from django.contrib.auth.hashers import make_password #securely store the hashed password in the database
from django.core.validators import FileExtensionValidator
class PreRegisteredUser(models.Model):
  userid = models.CharField(max_length=50 ,primary_key=True)
  email = models.EmailField(unique=True)
  password_sent = models.CharField(max_length=100)

  def __str__(self):
    return self.userid # the stored data will be represented by the userid

class UserRegistration(models.Model):
  name = models.CharField(max_length=100)
  userid = models.CharField(max_length=50,primary_key=True)
  email = models.EmailField(max_length=255, unique=True,null=True,blank=True)  
  contact_no = models.CharField(max_length=255)
  password = models.CharField(max_length=255)  # Hashed final password
 
  def save(self, *args, **kwargs):
        # Hash the password before saving
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
    required_materials = models.TextField(blank=False, null=False)
    labour = models.TextField(blank=False, null=False)
    machinery = models.TextField(blank=False, null=False)
    equipment = models.TextField(blank=False, null=False)
    tools = models.TextField(blank=False, null=False)
    consumables = models.TextField(blank=False, null=False)  # New field

    def __str__(self):
        return f"Materials and Resources for Project {self.project.project_id}"


class ProjectCompletion(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    before_after_completion = models.FileField(
        upload_to='completion_files/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
        blank=False,
        null=False
    )
    completion_proof = models.FileField(
        upload_to='completion_proofs/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
        blank=False,
        null=False
    )
    client_rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        blank=True,
        null=True
    )
    client_feedback = models.TextField(blank=True, null=True)
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
    client_name = models.CharField(max_length=100, blank=True, null=False) 
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True)
    through = models.CharField(max_length=20, choices=THROUGH_CHOICES, blank=False, null=False)
    client = models.CharField(max_length=20, choices=CLIENT_CHOICES, blank=False, null=False)
    time_of_visit = models.TextField(blank=False, null=False)
    record = models.TextField(blank=False, null=False)
    site_visit_remarks = models.TextField(blank=False, null=False)
    identification_of_problems = models.TextField(blank=False, null=False)
    solutions = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    site_visit_documentation = models.FileField(
        upload_to='site_visit_docs/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
        blank=True,
        null=True
    )
    quotation_submission = models.FileField(
        upload_to='quotation_submission/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
        blank=True,
        null=True
    )
    quotation_approval = models.FileField(
        upload_to='quotation_approval/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(['pdf', 'png', 'jpg', 'jpeg'])
        ],
        blank=True,
        null=True
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