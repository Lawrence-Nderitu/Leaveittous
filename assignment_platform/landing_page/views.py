from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, LoginForm
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
