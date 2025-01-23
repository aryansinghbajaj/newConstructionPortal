from django import forms
from .models import (
    UserRegistration,
    PreRegisteredUser,
    Project,
    MaterialsAndResources,
    ProjectCompletion,
    WorkExecution,
    Billing,
    PaymentEntry,
)
from django.contrib.auth.hashers import make_password


class BaseFormWithAsterisk(forms.ModelForm):
    """Base form to dynamically add an asterisk to required fields."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:  # Add asterisk only for required fields
                if field.label:
                    field.label = f"{field.label} *"
                else:
                    field.label = "*"


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

        # Validate all required fields are present
        if not all([userid, email, password_sent, new_password, confirm_password]):
            raise forms.ValidationError("All fields are required.")

        # Validate pre-registered user
        try:
            PreRegisteredUser.objects.get(
                userid=userid,
                email=email,
                password_sent=password_sent
            )
        except PreRegisteredUser.DoesNotExist:
            raise forms.ValidationError("Invalid userid, email, or pre-registered password.")

        # Validate password match
        if new_password != confirm_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data


class UserLoginForm(forms.Form):
    userid = forms.CharField(max_length=50, label="User ID *")
    password = forms.CharField(widget=forms.PasswordInput(), label="Password *")


class CreateProjectForm(forms.Form):
    project_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Project ID'}),
        label="Project ID *"
    )


class OpenProjectForm(forms.Form):
    project_id = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Project ID'}),
        label="Project ID *"
    )


class MaterialsAndResourcesForm(BaseFormWithAsterisk):
    class Meta:
        model = MaterialsAndResources
        fields = ['required_materials', 'labour', 'machinery', 'equipment', 'tools', 'consumables']
        widgets = {
            'required_materials': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter required materials'
            }),
            'labour': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter labour details'
            }),
            'machinery': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter machinery details'
            }),
            'equipment': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter equipment details'
            }),
            'tools': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter tools details'
            }),
            'consumables': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter consumables details'
            }),
        }


class ProjectCompletionForm(BaseFormWithAsterisk):
    class Meta:
        model = ProjectCompletion
        fields = ['before_after_completion', 'completion_proof', 'client_rating', 'client_feedback']
        widgets = {
            'before_after_completion': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'completion_proof': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'client_rating': forms.Select(attrs={
                'class': 'form-control',
            }),
            'client_feedback': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter client feedback on quality and quantity of work'
            }),
        }


class WorkExecutionForm(BaseFormWithAsterisk):
    class Meta:
        model = WorkExecution
        fields = [
            'through', 'client', 'time_of_visit', 'record', 'site_visit_remarks',
            'identification_of_problems', 'solutions', 'recommendations',
            'site_visit_documentation', 'quotation_submission', 'quotation_approval', 'client_name'
        ]
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name'
            }),
            'through': forms.Select(attrs={
                'class': 'form-control',
            }),
            'client': forms.Select(attrs={
                'class': 'form-control',
            }),
            'time_of_visit': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'record': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter record'
            }),
            'site_visit_remarks': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter site visit remarks'
            }),
            'identification_of_problems': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter identified problems'
            }),
            'solutions': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter solutions'
            }),
            'recommendations': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Enter recommendations'
            }),
            'site_visit_documentation': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'quotation_submission': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
            'quotation_approval': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.png,.jpg,.jpeg'
            }),
        }


class BillingForm(BaseFormWithAsterisk):
    class Meta:
        model = Billing
        fields = ['total_amount', 'estimated_amount', 'amount_left', 'next_expected_amount', 'next_expected_date']
        widgets = {
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'estimated_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'amount_left': forms.NumberInput(attrs={
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


class PaymentEntryForm(BaseFormWithAsterisk):
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
        widget=forms.TextInput(attrs={'placeholder': 'Enter Project ID'}),
        label="Project ID *"
    )
