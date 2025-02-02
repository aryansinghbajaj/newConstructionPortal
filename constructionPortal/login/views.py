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


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import UserRegistration
from .forms import UserLoginForm

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            userid = form.cleaned_data['userid']
            password = form.cleaned_data['password']
            
            try:
                user = UserRegistration.objects.get(userid=userid)
                if check_password(password, user.password):
                    request.session['userid'] = userid
                    messages.success(request, 'Login successful!')
                    
                    if user.group and user.group.name == 'Managers':
                        # Simply redirect to managers view
                        return redirect('managers')
                    else:
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

def managers_view(request):
    # Simply get all projects
    all_projects = Project.objects.all().order_by('-created_at')
    return render(request, 'managers.html', {'all_projects': all_projects})
def materials_resources_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        
        # Check if user is a manager
        if user.group.name == 'Managers':  # Adjust this condition based on how you store user groups
            project = Project.objects.get(project_id=project_id)  # Managers can access any project
        else:
            # For associates, check project ownership
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
def user_can_delete_files(user):
    return user.group.name != 'Associates'

def project_completion_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        # Check if user is a manager
        if user.group.name == 'Managers':
            project = Project.objects.get(project_id=project_id)
        else:
            project = Project.objects.get(project_id=project_id, user=user)
            
        project_completion, created = ProjectCompletion.objects.get_or_create(project=project)
        
        if request.method == 'POST' and 'delete_file' in request.POST:
            if user_can_delete_files(user):
                file_field = request.POST.get('delete_file')
                file_mapping = {
                    'before_after_completion': project_completion.before_after_completion,
                    'completion_proof': project_completion.completion_proof,
                }
                if file_field in file_mapping and file_mapping[file_field]:
                    if os.path.isfile(file_mapping[file_field].path):
                        os.remove(file_mapping[file_field].path)
                    setattr(project_completion, file_field, None)
                    project_completion.save()
                    messages.success(request, f'{file_field.replace("_", " ").title()} file has been deleted.')
                return redirect('project_completion', project_id=project_id)
            else:
                messages.error(request, 'You do not have permission to delete files.')
                return redirect('project_completion', project_id=project_id)
        
        form = ProjectCompletionForm(request.POST or None, request.FILES or None, instance=project_completion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project completion data has been saved successfully!')
            return redirect('project_completion', project_id=project_id)
        
        return render(request, 'project_completion.html', {
            'form': form,
            'project': project,
            'current_before_after': project_completion.before_after_completion,
            'current_completion_proof': project_completion.completion_proof,
        })
    except (UserRegistration.DoesNotExist, Project.DoesNotExist):
        messages.error(request, 'User or project not found.')
        return redirect('portal')

def work_execution_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        # Check if user is a manager
        if user.group.name == 'Managers':
            project = Project.objects.get(project_id=project_id)
        else:
            project = Project.objects.get(project_id=project_id, user=user)
            
        work_execution, created = WorkExecution.objects.get_or_create(project=project)
        
        if request.method == 'POST' and 'delete_file' in request.POST:
            if user_can_delete_files(user):
                file_field = request.POST.get('delete_file')
                file_mapping = {
                    'site_visit_documentation': work_execution.site_visit_documentation,
                    'quotation_submission': work_execution.quotation_submission,
                    'quotation_approval': work_execution.quotation_approval,
                }
                if file_field in file_mapping and file_mapping[file_field]:
                    if os.path.isfile(file_mapping[file_field].path):
                        os.remove(file_mapping[file_field].path)
                    setattr(work_execution, file_field, None)
                    work_execution.save()
                    messages.success(request, f'{file_field.replace("_", " ").title()} file has been deleted.')
                return redirect('work_execution', project_id=project_id)
            else:
                messages.error(request, 'You do not have permission to delete files.')
                return redirect('work_execution', project_id=project_id)
        
        form = WorkExecutionForm(request.POST or None, request.FILES or None, instance=work_execution)
        if form.is_valid():
            form.save()
            messages.success(request, 'Work execution data has been saved successfully!')
            return redirect('work_execution', project_id=project_id)
        
        return render(request, 'work_execution.html', {
            'form': form,
            'project': project,
            'current_site_visit_doc': work_execution.site_visit_documentation,
            'current_quotation_submission': work_execution.quotation_submission,
            'current_quotation_approval': work_execution.quotation_approval,
        })
    except (UserRegistration.DoesNotExist, Project.DoesNotExist):
        messages.error(request, 'User or project not found.')
        return redirect('portal')

def billing_view(request, project_id):
    if 'userid' not in request.session:
        messages.error(request, 'Please log in to access this page')
        return redirect('new_user_login')
    
    try:
        user = UserRegistration.objects.get(userid=request.session['userid'])
        if user.group.name == 'Managers':
            project = Project.objects.get(project_id=project_id)
        else:
            project = Project.objects.get(project_id=project_id, user=user)
            
        billing, created = Billing.objects.get_or_create(project=project)
        
        if request.method == 'POST':
            if 'delete_payment_proof' in request.POST:
                if user_can_delete_files(user):
                    try:
                        payment_entry = PaymentEntry.objects.get(
                            serial_no=request.POST.get('payment_entry_id'), 
                            billing=billing
                        )
                        if payment_entry.payment_proof and os.path.isfile(payment_entry.payment_proof.path):
                            os.remove(payment_entry.payment_proof.path)
                            payment_entry.payment_proof = None
                            payment_entry.save()
                            messages.success(request, 'Payment proof has been deleted successfully.')
                    except PaymentEntry.DoesNotExist:
                        messages.error(request, 'Payment entry not found.')
                else:
                    messages.error(request, 'You do not have permission to delete files.')
                return redirect('billing', project_id=project_id)
            
            # Handle billing form submission
            if 'billing_form' in request.POST:
                billing_form = BillingForm(request.POST, instance=billing)
                if billing_form.is_valid():
                    billing_form.save()
                    messages.success(request, 'Billing information has been updated successfully!')
                    return redirect('billing', project_id=project_id)
            
            # Handle payment form submission
            if 'payment_form' in request.POST:
                payment_form = PaymentEntryForm(request.POST, request.FILES)
                if payment_form.is_valid():
                    payment = payment_form.save(commit=False)
                    payment.billing = billing
                    payment.save()
                    messages.success(request, 'Payment entry has been added successfully!')
                    return redirect('billing', project_id=project_id)
        
        billing_form = BillingForm(instance=billing)
        payment_form = PaymentEntryForm()
        payment_entries = PaymentEntry.objects.filter(billing=billing).order_by('-payment_date')
        
        return render(request, 'billing.html', {
            'billing_form': billing_form,
            'payment_form': payment_form,
            'project': project,
            'payment_entries': payment_entries,
            'billing': billing,
        })
        
    except (UserRegistration.DoesNotExist, Project.DoesNotExist):
        messages.error(request, 'User or project not found.')
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