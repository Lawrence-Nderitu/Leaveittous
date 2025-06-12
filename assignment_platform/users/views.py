from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin_user(user):
    return user.is_staff or (hasattr(user, 'user_type') and user.user_type == 'admin')

from assignments.models import Assignment # Import Assignment model

@login_required
def student_dashboard_view(request):
    assignments = Assignment.objects.filter(student=request.user).order_by('-created_at')
    context = {
        'assignments': assignments
    }
    return render(request, 'users/student_dashboard.html', context)

from assignments.models import Bid # Import Bid model

# Ensure Assignment is imported if not already (it was from student_dashboard_view)
# from assignments.models import Assignment

# Define is_writer_user if it's not already defined or imported
# For this example, assuming is_writer_user is defined as:
# def is_writer_user(user): return hasattr(user, 'user_type') and user.user_type == 'writer'
# If it's in assignments.views, you might need to import it or redefine it here.
# For simplicity, I'll use a lambda in user_passes_test directly if not already defined.

def is_writer_user(user): # Define is_writer_user locally
    return user.is_authenticated and hasattr(user, 'user_type') and user.user_type == 'writer'

@login_required
@user_passes_test(is_writer_user, login_url='/login/') # Use the defined function
def writer_dashboard_view(request):
    my_bids = Bid.objects.filter(writer=request.user).select_related('assignment').order_by('-created_at')

    assigned_work = Assignment.objects.filter(
        writer=request.user,
        status='assigned'
    ).order_by('deadline')

    context = {
        'my_bids': my_bids,
        'assigned_work': assigned_work,
    }
    return render(request, 'users/writer_dashboard.html', context)

@login_required
@user_passes_test(is_admin_user)
def admin_dashboard_view(request):
    return render(request, 'users/admin_dashboard.html')
