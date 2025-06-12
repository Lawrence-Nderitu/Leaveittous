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

from .models import User # Import User model for admin dashboard stats
from django.db.models import Count, Q # For aggregations if needed, though simple counts are used here

@login_required
@user_passes_test(is_admin_user)
def admin_dashboard_view(request):
    total_users = User.objects.count()
    student_count = User.objects.filter(user_type='student').count()
    writer_count = User.objects.filter(user_type='writer').count()
    # For admin_user_count, consider if 'admin' user_type is used or just is_staff
    admin_user_count = User.objects.filter(Q(user_type='admin') | Q(is_staff=True)).distinct().count()

    total_assignments = Assignment.objects.count()
    open_assignments = Assignment.objects.filter(status='open').count()
    assigned_assignments = Assignment.objects.filter(status='assigned').count()
    submitted_assignments = Assignment.objects.filter(status='submitted').count()
    completed_assignments = Assignment.objects.filter(status='completed').count()
    cancelled_assignments = Assignment.objects.filter(status='cancelled').count()

    context = {
        'total_users': total_users,
        'student_count': student_count,
        'writer_count': writer_count,
        'admin_user_count': admin_user_count,
        'total_assignments': total_assignments,
        'open_assignments': open_assignments,
        'assigned_assignments': assigned_assignments,
        'submitted_assignments': submitted_assignments,
        'completed_assignments': completed_assignments,
        'cancelled_assignments': cancelled_assignments,
        'page_title': 'Admin Dashboard Overview'
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin_user) # Re-using is_admin_user for authorization
def admin_list_users_view(request):
    users = User.objects.all().order_by('username')
    context = {
        'users': users,
        'page_title': 'Manage Users'
    }
    return render(request, 'users/admin_list_users.html', context)
