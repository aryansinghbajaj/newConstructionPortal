from django.shortcuts import render, redirect ,reverse , get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm , CreateProjectForm ,OpenProjectForm ,MaterialsAndResourcesForm , ProjectCompletionForm , WorkExecutionForm , BillingForm , PaymentEntryForm , DeleteProjectForm
from .models import UserRegistration, PreRegisteredUser , Project ,MaterialsAndResources , ProjectCompletion , WorkExecution , Billing,PaymentEntry
import os 
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def home(request):
    return render(request, 'welcome.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        
        print("Form Data:", request.POST)
        
        if form.is_valid():
            try:
                user = UserRegistration(
                    name=form.cleaned_data['name'],
                    userid=form.cleaned_data['userid'],
                    email=form.cleaned_data['email'],
                    contact_no=form.cleaned_data['contact_no'],
                    password=make_password(form.cleaned_data['new_password']),
                    group=form.cleaned_data['group']  # Set the group from pre-registered user
                )
                user.save()
                
                messages.success(request, 'Registration successful!')
                return redirect('home')
            
            except Exception as e:
                print(f"Registration Error: {str(e)}")
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            print("Form Errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            userid = form.cleaned_data['userid']
            password = form.cleaned_data['password']
            
            try:
                user = UserRegistration.objects.get(userid=userid)
                if check_password(password, user.password):
                    request.session['userid'] = userid  # Store userid in session
                    messages.success(request, 'Login successful!')
                    return render(request, 'portal.html', {'user': user})
                else:
                    messages.error(request, 'Invalid password')
            except UserRegistration.DoesNotExist:
                messages.error(request, 'User ID not found')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def create_project(request):
    if request.method == 'POST':
        form = CreateProjectForm(request.POST)
        if form.is_valid():
            project_id = form.cleaned_data['project_id']
            
            # Check if project ID already exists
            if Project.objects.filter(project_id=project_id).exists():
                messages.error(request, 'Project ID already exists')
                return render(request, 'create_project.html', {'form': form})
            
            # Create new project
            project = Project(
                project_id=project_id,
                user=UserRegistration.objects.get(userid=request.session.get('userid'))
            )
            project.save()
            
            # Redirect to dashboard with project ID
            return redirect('dashboard', project_id=project_id)
    else:
        form = CreateProjectForm()
    return render(request, 'create_project.html', {'form': form})


def open_project(request):
    try:
        user_registration = UserRegistration.objects.get(userid=request.session.get('userid'))
        # Get all projects for the current user
        user_projects = Project.objects.filter(user=user_registration).order_by('-created_at')
    except UserRegistration.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        return redirect('login')
    
    if request.method == 'POST':
        form = OpenProjectForm(request.POST)
        if form.is_valid():
            project_id = form.cleaned_data['project_id']
            
            try:
                project = Project.objects.get(project_id=project_id)
                return redirect('dashboard', project_id=project_id)
            except Project.DoesNotExist:
                messages.error(request, 'Project ID does not exist')
                return render(request, 'open_project.html', {
                    'form': form,
                    'user_projects': user_projects
                })
    else:
        form = OpenProjectForm()
    
    return render(request, 'open_project.html', {
        'form': form,
        'user_projects': user_projects
    })
def dashboard(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id)
        return render(request, 'dashboard.html', {'project': project})
    except Project.DoesNotExist:
        messages.error(request, 'Project not found')
        return redirect('portal')
def portal_view(request):
    return render(request,'portal.html')

def materials_resources_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        project = Project.objects.get(
            project_id=project_id,
            user=user
        )
        
        materials_resources, created = MaterialsAndResources.objects.get_or_create(
            project=project
        )
        
        if request.method == 'POST':
            form = MaterialsAndResourcesForm(request.POST, instance=materials_resources)
            if form.is_valid():
                form.save()
                messages.success(request, 'Data has been saved successfully!')
                return redirect('materials_resources', project_id=project_id)
        else:
            form = MaterialsAndResourcesForm(instance=materials_resources)
        
        return render(request, 'material_resources.html', {
            'form': form,
            'project': project
        })
    
    except UserRegistration.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('new_user_login')
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or access denied')
        return redirect('portal')
def project_completion_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        project = Project.objects.get(
            project_id=project_id,
            user=user
        )
        
        project_completion, created = ProjectCompletion.objects.get_or_create(
            project=project
        )
        
        # Handle file deletion requests
        if request.method == 'POST' and 'delete_file' in request.POST:
            file_field = request.POST.get('delete_file')
            if file_field == 'before_after_completion' and project_completion.before_after_completion:
                if os.path.isfile(project_completion.before_after_completion.path):
                    os.remove(project_completion.before_after_completion.path)
                project_completion.before_after_completion = None
                project_completion.save()
                messages.success(request, 'Before/After Completion file has been deleted.')
                return redirect('project_completion', project_id=project_id)
            
            elif file_field == 'completion_proof' and project_completion.completion_proof:
                if os.path.isfile(project_completion.completion_proof.path):
                    os.remove(project_completion.completion_proof.path)
                project_completion.completion_proof = None
                project_completion.save()
                messages.success(request, 'Completion Proof file has been deleted.')
                return redirect('project_completion', project_id=project_id)
        
        if request.method == 'POST' and 'delete_file' not in request.POST:
            form = ProjectCompletionForm(
                request.POST,
                request.FILES,
                instance=project_completion
            )
            
            if form.is_valid():
                # Delete old files if new ones are uploaded
                if 'before_after_completion' in request.FILES:
                    if project_completion.before_after_completion:
                        old_file = project_completion.before_after_completion.path
                        if os.path.isfile(old_file):
                            os.remove(old_file)
                
                if 'completion_proof' in request.FILES:
                    if project_completion.completion_proof:
                        old_file = project_completion.completion_proof.path
                        if os.path.isfile(old_file):
                            os.remove(old_file)
                
                form.save()
                messages.success(request, 'Project completion data has been saved successfully!')
                return redirect('project_completion', project_id=project_id)
        else:
            form = ProjectCompletionForm(instance=project_completion)
        
        return render(request, 'project_completion.html', {
            'form': form,
            'project': project,
            'current_before_after': project_completion.before_after_completion,
            'current_completion_proof': project_completion.completion_proof,
        })
    
    except UserRegistration.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('new_user_login')
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or access denied')
        return redirect('portal')

def work_execution_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        project = Project.objects.get(
            project_id=project_id,
            user=user
        )
        
        work_execution, created = WorkExecution.objects.get_or_create(
            project=project
        )
        
        # Handle file deletion requests
        if request.method == 'POST' and 'delete_file' in request.POST:
            file_field = request.POST.get('delete_file')
            if file_field == 'site_visit_documentation' and work_execution.site_visit_documentation:
                if os.path.isfile(work_execution.site_visit_documentation.path):
                    os.remove(work_execution.site_visit_documentation.path)
                work_execution.site_visit_documentation = None
                work_execution.save()
                messages.success(request, 'Site Visit Documentation file has been deleted.')
                return redirect('work_execution', project_id=project_id)
            
            elif file_field == 'quotation_submission' and work_execution.quotation_submission:
                if os.path.isfile(work_execution.quotation_submission.path):
                    os.remove(work_execution.quotation_submission.path)
                work_execution.quotation_submission = None
                work_execution.save()
                messages.success(request, 'Quotation Submission file has been deleted.')
                return redirect('work_execution', project_id=project_id)
            
            elif file_field == 'quotation_approval' and work_execution.quotation_approval:
                if os.path.isfile(work_execution.quotation_approval.path):
                    os.remove(work_execution.quotation_approval.path)
                work_execution.quotation_approval = None
                work_execution.save()
                messages.success(request, 'Quotation Approval file has been deleted.')
                return redirect('work_execution', project_id=project_id)
        
        if request.method == 'POST' and 'delete_file' not in request.POST:
            form = WorkExecutionForm(
                request.POST,
                request.FILES,
                instance=work_execution
            )
            
            if form.is_valid():
                # Delete old files if new ones are uploaded
                if 'site_visit_documentation' in request.FILES:
                    if work_execution.site_visit_documentation:
                        old_file = work_execution.site_visit_documentation.path
                        if os.path.isfile(old_file):
                            os.remove(old_file)
                
                if 'quotation_submission' in request.FILES:
                    if work_execution.quotation_submission:
                        old_file = work_execution.quotation_submission.path
                        if os.path.isfile(old_file):
                            os.remove(old_file)
                
                if 'quotation_approval' in request.FILES:
                    if work_execution.quotation_approval:
                        old_file = work_execution.quotation_approval.path
                        if os.path.isfile(old_file):
                            os.remove(old_file)
                
                form.save()
                messages.success(request, 'Work execution data has been saved successfully!')
                return redirect('work_execution', project_id=project_id)
        else:
            form = WorkExecutionForm(instance=work_execution)
        
        return render(request, 'work_execution.html', {
            'form': form,
            'project': project,
            'current_site_visit_doc': work_execution.site_visit_documentation,
            'current_quotation_submission': work_execution.quotation_submission,
            'current_quotation_approval': work_execution.quotation_approval,
        })
    
    except UserRegistration.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('new_user_login')
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or access denied')
        return redirect('portal')

def billing_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        project = Project.objects.get(
            project_id=project_id,
            user=user
        )
        
        billing, created = Billing.objects.get_or_create(
            project=project
        )
        
        # Handle file deletion requests
        if request.method == 'POST' and 'delete_payment_proof' in request.POST:
            try:
                payment_entry = PaymentEntry.objects.get(
                    serial_no=request.POST.get('payment_entry_id'),
                    billing=billing
                )
                if payment_entry.payment_proof:
                    if os.path.isfile(payment_entry.payment_proof.path):
                        os.remove(payment_entry.payment_proof.path)
                    payment_entry.payment_proof = None
                    payment_entry.save()
                    messages.success(request, 'Payment proof has been deleted successfully.')
                return redirect('billing', project_id=project_id)
            except PaymentEntry.DoesNotExist:
                messages.error(request, 'Payment entry not found.')
                return redirect('billing', project_id=project_id)
        
        if request.method == 'POST':
            if 'billing_form' in request.POST:
                billing_form = BillingForm(request.POST, instance=billing)
                payment_form = PaymentEntryForm()
                
                if billing_form.is_valid():
                    billing_form.save()
                    messages.success(request, 'Billing information has been updated successfully!')
                    return redirect('billing', project_id=project_id)
            
            elif 'payment_form' in request.POST:
                payment_form = PaymentEntryForm(request.POST, request.FILES)
                billing_form = BillingForm(instance=billing)
                
                if payment_form.is_valid():
                    payment = payment_form.save(commit=False)
                    payment.billing = billing
                    payment.save()
                    messages.success(request, 'Payment entry has been added successfully!')
                    return redirect('billing', project_id=project_id)
        else:
            billing_form = BillingForm(instance=billing)
            payment_form = PaymentEntryForm()
        
        payment_entries = PaymentEntry.objects.filter(billing=billing).order_by('-payment_date')
        
        return render(request, 'billing.html', {
            'billing_form': billing_form,
            'payment_form': payment_form,
            'project': project,
            'payment_entries': payment_entries,
        })
    
    except UserRegistration.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('new_user_login')
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or access denied')
        return redirect('portal')
def delete_project(request):
    if request.method == 'POST':
        form = DeleteProjectForm(request.POST)
        if form.is_valid():
            project_id = form.cleaned_data['project_id']
            
            try:
                # Verify the project exists and belongs to the current user
                project = Project.objects.get(
                    project_id=project_id,
                    user__userid=request.session.get('userid')
                )
                
                # Due to CASCADE, this will delete all related records
                project.delete()
                
                messages.success(request, 'Project successfully deleted')
                return redirect('portal')  # Redirect to portal page after successful deletion
                
            except Project.DoesNotExist:
                messages.error(request, 'Invalid Project ID')
                return render(request, 'delete_project.html', {'form': form})
    else:
        form = DeleteProjectForm()
    return render(request, 'delete_project.html', {'form': form})

def confirm_delete(request):
    return render(request, 'confirm_delete.html')