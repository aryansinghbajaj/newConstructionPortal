from django import forms 
from .models import UserRegistration, PreRegisteredUser , Project , MaterialsAndResources , ProjectCompletion , WorkExecution , Billing,PaymentEntry
from django.contrib.auth.hashers import make_password

class UserRegistrationForm(forms.ModelForm):
    userid = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter User ID'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'})
    )
    password_sent = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Pre-registered Password'}),
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter New Password'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        required=True
    )

    class Meta:
        model = UserRegistration
        fields = ['name', 'userid', 'email', 'contact_no']

    def clean(self):
        cleaned_data = super().clean()
        userid = cleaned_data.get('userid')
        email = cleaned_data.get('email')
        password_sent = cleaned_data.get('password_sent')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        name = cleaned_data.get('name')
        contact_no = cleaned_data.get('contact_no')

        if not all([userid, email, password_sent, new_password, confirm_password, name, contact_no]):
            raise forms.ValidationError("All fields are required.")

        try:
            pre_registered_user = PreRegisteredUser.objects.get(
                userid=userid,
                email=email,
                password_sent=password_sent
            )
            # Store the group from pre-registered user for use in view
            cleaned_data['group'] = pre_registered_user.group
        except PreRegisteredUser.DoesNotExist:
            raise forms.ValidationError("Invalid userid, email, or pre-registered password.")

        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match")

        return cleaned_data
class UserLoginForm(forms.Form):
    userid = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput())

class CreateProjectForm(forms.Form):
    project_id = forms.CharField(
        max_length=50,
        required = True,
        widget=forms.TextInput(attrs={'placeholder':'Enter Project ID'})
    )
class OpenProjectForm(forms.Form):
    project_id = forms.CharField(
        max_length= 50,
        required=True,
        widget= forms.TextInput(attrs={'placeholder':'Enter Project ID'})
    )
class MaterialsAndResourcesForm(forms.ModelForm):
    class Meta:
        model = MaterialsAndResources
        fields = ['required_materials', 'labour', 'machinery', 'equipment', 'tools', 'consumables']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True
            
        # Add widgets with custom attributes
        self.fields['required_materials'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter required materials (Required)'
        })
        
        self.fields['labour'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter labour details (Required)'
        })
        
        self.fields['machinery'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter machinery details (Required)'
        })
        
        self.fields['equipment'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter equipment details (Required)'
        })
        
        self.fields['tools'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter tools details (Required)'
        })
        
        self.fields['consumables'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter consumables details (Required)'
        })

class ProjectCompletionForm(forms.ModelForm):
    CLIENT_RATING_CHOICES = [
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent'),
    ]

    client_rating = forms.ChoiceField(
        choices=CLIENT_RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = ProjectCompletion
        fields = ['before_after_completion', 'completion_proof', 'client_rating', 'client_feedback']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True

        # Add widgets with custom attributes
        self.fields['before_after_completion'].widget = forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.png,.jpg,.jpeg',
        })
        self.fields['completion_proof'].widget = forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.png,.jpg,.jpeg',
        })
        self.fields['client_feedback'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter client feedback on quality and quantity of work (Required)',
        })


class WorkExecutionForm(forms.ModelForm):
    class Meta:
        model = WorkExecution
        fields = ['through', 'client', 'client_name', 'time_of_visit', 'record', 'site_visit_remarks', 
                 'identification_of_problems', 'solutions', 'recommendations',
                 'site_visit_documentation', 'quotation_submission', 'quotation_approval']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True
            
        # Add widgets with custom attributes and choices
        self.fields['through'].widget = forms.Select(
            attrs={'class': 'form-control'},
            choices=WorkExecution.THROUGH_CHOICES
        )
        self.fields['client'].widget = forms.Select(
            attrs={'class': 'form-control'},
            choices=WorkExecution.CLIENT_CHOICES
        )
        self.fields['client_name'].widget = forms.Textarea(attrs={
            'rows': 1,
            'class': 'form-control',
            'placeholder': 'Enter client name (Required)'
        })
        self.fields['time_of_visit'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Enter time of visit in dd/mm/yyyy (Required)'
        })
        self.fields['record'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter record (Required)'
        })
        self.fields['site_visit_remarks'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter site visit remarks (Required)'
        })
        self.fields['identification_of_problems'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter identified problems (Required)'
        })
        self.fields['solutions'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter solutions (Required)'
        })
        self.fields['recommendations'].widget = forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control',
            'placeholder': 'Enter recommendations (Required)'
        })
        self.fields['site_visit_documentation'].widget = forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.png,.jpg,.jpeg'
        })
        self.fields['quotation_submission'].widget = forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.png,.jpg,.jpeg'
        })
        self.fields['quotation_approval'].widget = forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.png,.jpg,.jpeg'
        })
        
        # Make file fields not required since they can be null/blank in the model
        self.fields['site_visit_documentation'].required = False
        self.fields['quotation_submission'].required = False
        self.fields['quotation_approval'].required = False
class BillingForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['total_amount', 'estimated_amount', 'next_expected_amount', 'next_expected_date']
        widgets = {
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'estimated_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'next_expected_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'next_expected_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
class PaymentEntryForm(forms.ModelForm):
    class Meta:
        model = PaymentEntry
        fields = ['amount_paid', 'client_detail', 'mode_of_payment', 'payment_proof', 'payment_date']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'client_detail': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter client payment details'
            }),
            'mode_of_payment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Bank Transfer, Cash, Check'
            }),
            'payment_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'payment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

class DeleteProjectForm(forms.Form):
    project_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Project ID'})
    )