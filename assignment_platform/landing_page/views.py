from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, CustomAuthenticationForm # Use CustomAuthenticationForm
# from django.contrib.auth.forms import AuthenticationForm # No longer directly needed here
from django.contrib import messages

def landing_page_view(request):
    return render(request, 'landing_page/landing_page.html')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log in the new user
            messages.success(request, "Registration successful.")
            # Redirect based on user type after registration
            if hasattr(user, 'user_type'):
                if user.user_type == 'student':
                    return redirect('users:student_dashboard')
                elif user.user_type == 'writer':
                    return redirect('users:writer_dashboard')
                elif user.user_type == 'admin' or user.is_staff:
                    return redirect('users:admin_dashboard')
                else:
                    return redirect('landing_page:landing_page')
            elif user.is_staff: # Fallback for Django admin users without a specific user_type
                return redirect('users:admin_dashboard')
            else:
                # Default fallback if no specific role matches
                return redirect('landing_page:landing_page')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()
    return render(request, 'landing_page/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                # Redirect based on user type
                if hasattr(user, 'user_type'): # Check if user_type attribute exists
                    if user.user_type == 'student':
                        return redirect('users:student_dashboard')
                    elif user.user_type == 'writer':
                        return redirect('users:writer_dashboard')
                    elif user.user_type == 'admin' or user.is_staff: # Check is_staff for Django admins
                        return redirect('users:admin_dashboard')
                    else:
                        # Fallback for users with user_type not matching or undefined
                        return redirect('landing_page:landing_page')
                elif user.is_staff: # Fallback for Django admin users without a specific user_type
                    return redirect('users:admin_dashboard')
                else:
                    # Default fallback if no specific role matches
                    return redirect('landing_page:landing_page')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'landing_page/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('landing_page:landing_page') # Use namespaced URL

# Role-Specific Registration Views

def student_register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'student'
            user.save()
            login(request, user)
            messages.success(request, 'Student account created successfully! Welcome.')
            return redirect('users:student_dashboard')
        else:
            # Pass form with errors to the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'form_title': 'Student Registration',
        'role_description': 'Sign up to post assignments and find expert help.',
        'login_url_name': 'landing_page:student_login'
    }
    return render(request, 'landing_page/register_role.html', context)

def writer_register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'writer'
            user.is_active = False  # Set new writers to inactive by default
            user.save()
            # Do not log in the user automatically
            messages.success(request, 'Writer account created successfully! It is now awaiting admin approval and activation.')
            return redirect('landing_page:landing_page') # Redirect to home page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'form_title': 'Writer Registration',
        'role_description': 'Join our team of expert writers. Your account will be activated after admin review.', # Updated description
        'login_url_name': 'landing_page:writer_login'
    }
    return render(request, 'landing_page/register_role.html', context)


# Role-Specific Login Views

def student_login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() # User is active here due to AuthenticationForm
            login(request, user) # Log in the user first

            # Redirect logic
            if user.is_superuser or user.is_staff: # Prioritize admin/staff
                messages.success(request, f'Welcome Admin, {user.username}!')
                return redirect('users:admin_dashboard')
            elif hasattr(user, 'user_type') and user.user_type == 'student':
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next')
                return redirect(next_url or 'users:student_dashboard')
            else:
                # Log out user if they were logged in but don't match any role for this portal
                logout(request)
                messages.error(request, 'This login portal is for students. Your account type is not student.')
                # Form remains the same, context will re-render it.
        else: # Form is not valid (e.g. wrong password, or user is inactive)
            username = request.POST.get('username')
            from users.models import User # Import User model
            try:
                user_check = User.objects.get(username=username)
                if not user_check.is_active and hasattr(user_check, 'user_type') and user_check.user_type == 'student':
                    messages.error(request, 'Your student account is awaiting activation or has been deactivated.')
                # For other cases, the form's default error messages are usually sufficient,
                # or a generic one can be added.
                # else:
                #     messages.error(request, 'Invalid username or password, or your account may be inactive/disabled for this portal.')
            except User.DoesNotExist:
                pass # Form.is_valid() already handled this by "Invalid username or password"
            # If form is invalid, it will re-render with its own errors. Add a general one if desired.
            if not form.errors: # If Django's AuthenticationForm didn't add specific errors (e.g. inactive user)
                 messages.error(request, 'Invalid username or password. Please try again or check if your account is active.')
    else:
        form = CustomAuthenticationForm() # Use CustomAuthenticationForm

    context = {
        'form': form,
        'form_title': 'Student Login',
        'description': 'Access your dashboard to manage assignments.',
        'register_url_name': 'landing_page:student_register',
        'forgot_password_url_name': '#' # Placeholder
    }
    return render(request, 'landing_page/login_role.html', context)

def writer_login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user() # User is active here
            login(request, user) # Log in the user first

            if user.is_superuser or user.is_staff: # Prioritize admin/staff
                messages.success(request, f'Welcome Admin, {user.username}!')
                return redirect('users:admin_dashboard')
            elif hasattr(user, 'user_type') and user.user_type == 'writer':
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next')
                return redirect(next_url or 'users:writer_dashboard')
            else:
                logout(request) # Log out if wrong role for this portal
                messages.error(request, 'This login portal is for writers. Your account type is not writer.')
        else: # Form is not valid
            username = request.POST.get('username')
            from users.models import User # Import User model
            try:
                user_check = User.objects.get(username=username)
                if hasattr(user_check, 'user_type') and user_check.user_type == 'writer' and not user_check.is_active:
                    messages.error(request, 'Your writer account is awaiting admin approval and activation.')
                # else:
                #     messages.error(request, 'Invalid username or password, or your account may be inactive/disabled for this portal.')
            except User.DoesNotExist:
                pass # Form.is_valid() already handled this
            if not form.errors: # If Django's AuthenticationForm didn't add specific errors
                 messages.error(request, 'Invalid username or password. Please try again or check if your account is active.')
    else:
        form = CustomAuthenticationForm() # Use CustomAuthenticationForm

    context = {
        'form': form,
        'form_title': 'Writer Login',
        'description': 'Access your dashboard to find assignments and manage your bids.',
        'register_url_name': 'landing_page:writer_register',
        'forgot_password_url_name': '#' # Placeholder
    }
    return render(request, 'landing_page/login_role.html', context)
