from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import AssignmentCreateForm, BidForm, AssignmentSubmissionForm # Import AssignmentSubmissionForm
from .models import Assignment, Bid
from django.utils import timezone # Import timezone

def is_student_user(user):
    # Check if user is authenticated and has user_type attribute
    if not user.is_authenticated:
        return False
    return hasattr(user, 'user_type') and user.user_type == 'student'

def is_writer_user(user):
    if not user.is_authenticated:
        return False
    return hasattr(user, 'user_type') and user.user_type == 'writer'

@login_required
@user_passes_test(is_student_user, login_url='/users/login/') # Redirect if test fails, login_url can be customized
def create_assignment_view(request):
    if request.method == 'POST':
        form = AssignmentCreateForm(request.POST, request.FILES) # Added request.FILES for potential file uploads
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.student = request.user
            assignment.status = 'open' # Default status
            assignment.save()
            messages.success(request, f"Assignment '{assignment.title}' created successfully.") # Updated success message
            return redirect('users:student_dashboard')
        else:
            # Keep existing detailed error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = AssignmentCreateForm()

    context = {
        'form': form,
        'page_title': 'Post New Assignment'
    }
    return render(request, 'assignments/create_assignment.html', context)

@login_required
@user_passes_test(is_student_user, login_url='/users/login/')
def assignment_detail_student_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, student=request.user)
    bids = Bid.objects.filter(assignment=assignment).order_by('created_at')
    context = {
        'assignment': assignment,
        'bids': bids,
    }
    return render(request, 'assignments/assignment_detail_student.html', context)

@login_required
@user_passes_test(is_writer_user, login_url='/users/login/') # Redirect if test fails
def browse_open_assignments_view(request):
    # Fetch assignments that are 'open' and that the current writer has not already bid on (optional)
    # For now, just fetching all open assignments.
    open_assignments = Assignment.objects.filter(status='open').order_by('deadline')

    # Consider excluding assignments the writer has already bid on, if that logic is desired.
    # Example:
    # my_bids = Bid.objects.filter(writer=request.user).values_list('assignment_id', flat=True)
    # open_assignments = Assignment.objects.filter(status='open').exclude(id__in=my_bids).order_by('deadline')

    context = {
        'assignments': open_assignments,
    }
    return render(request, 'assignments/browse_open_assignments.html', context)

@login_required
@user_passes_test(is_writer_user, login_url='/users/login/')
def assignment_detail_writer_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, status='open')
    existing_bid = Bid.objects.filter(assignment=assignment, writer=request.user).first()
    bid_form = None

    if not existing_bid: # Only process form if no existing bid
        if request.method == 'POST':
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.writer = request.user
                bid.assignment = assignment
                bid.save()
                messages.success(request, 'Your bid has been placed successfully!')
                return redirect('assignments:browse_open_assignments')
        else:
            bid_form = BidForm()
    elif existing_bid: # If bid exists, inform user
        messages.info(request, "You have already placed a bid on this assignment. You can update it from your dashboard (feature coming soon).")
        # Not passing bid_form to context if bid exists, so form won't render

    context = {
        'assignment': assignment,
        'bid_form': bid_form, # Will be None if bid exists or if not POST/GET
        'existing_bid': existing_bid,
    }
    return render(request, 'assignments/assignment_detail_writer.html', context)

@login_required
@user_passes_test(is_student_user, login_url='/users/login/')
def award_assignment_view(request, bid_id):
    bid_to_accept = get_object_or_404(Bid, id=bid_id)
    assignment_to_award = bid_to_accept.assignment

    # Security checks:
    if assignment_to_award.student != request.user:
        messages.error(request, "You are not authorized to award this assignment.")
        # Redirect to a safe page, like the main landing page or student dashboard
        return redirect('landing_page:landing_page')

    if assignment_to_award.status != 'open':
        messages.error(request, "This assignment is no longer open for awarding.")
        return redirect('assignments:assignment_detail_student', assignment_id=assignment_to_award.id)

    if request.method == 'POST':
        # Update assignment
        assignment_to_award.status = 'assigned'
        assignment_to_award.writer = bid_to_accept.writer
        assignment_to_award.save()

        # Update the accepted bid
        bid_to_accept.status = 'accepted'
        bid_to_accept.save()

        # Reject other bids for the same assignment
        other_bids = Bid.objects.filter(assignment=assignment_to_award).exclude(id=bid_to_accept.id)
        for other_bid in other_bids:
            other_bid.status = 'rejected'
            other_bid.save()

        messages.success(request, f"Assignment '{assignment_to_award.title}' has been awarded to {bid_to_accept.writer.username}.")
        return redirect('assignments:assignment_detail_student', assignment_id=assignment_to_award.id)
    else:
        # GET request not typical for this action
        messages.info(request, "Please use the award button on the assignment detail page to select a bid.")
        return redirect('assignments:assignment_detail_student', assignment_id=assignment_to_award.id)

@login_required
@user_passes_test(is_writer_user, login_url='/users/login/') # Ensure is_writer_user is defined or imported
def submit_assignment_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, writer=request.user)

    if assignment.status != 'assigned':
        messages.error(request, "This assignment is not currently awaiting submission or has already been submitted.")
        return redirect('users:writer_dashboard')

    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()
            submission.save()
            messages.success(request, f"Your work for '{assignment.title}' has been submitted successfully.")
            return redirect('users:writer_dashboard')
        else:
            # Form is invalid, add error messages
            for field, errors_list in form.errors.items():
                for error in errors_list:
                    messages.error(request, f"Error in {form.fields[field].label if field != '__all__' else 'form'}: {error}")

    else:
        form = AssignmentSubmissionForm(instance=assignment)

    context = {
        'form': form,
        'assignment': assignment,
    }
    return render(request, 'assignments/submit_assignment.html', context)

@login_required
@user_passes_test(is_student_user, login_url='/users/login/')
def mark_assignment_complete_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, student=request.user)

    if assignment.status != 'submitted':
        messages.error(request, "This assignment cannot be marked as complete. It has not been submitted or is already completed/cancelled.")
        return redirect('assignments:assignment_detail_student', assignment_id=assignment.id)

    if request.method == 'POST':
        assignment.status = 'completed'
        # Optionally, you might want to set a completion date field here if you add one to the model
        # assignment.completion_date = timezone.now()
        assignment.save()
        messages.success(request, f"Assignment '{assignment.title}' has been marked as completed.")
        # Consider also notifying the writer, or other post-completion logic
        return redirect('assignments:assignment_detail_student', assignment_id=assignment.id)
    else:
        # If accessed via GET, just redirect back, as this action should be via POST from a button.
        messages.info(request, "Please use the button on the assignment detail page to mark it as complete.")
        return redirect('assignments:assignment_detail_student', assignment_id=assignment.id)

# Admin views for assignments
@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'user_type') and u.user_type == 'admin'))
def admin_list_assignments_view(request):
    assignments = Assignment.objects.select_related('student', 'writer').all().order_by('-created_at')
    context = {
        'assignments': assignments,
        'page_title': 'Manage Assignments'
    }
    return render(request, 'assignments/admin_list_assignments.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or (hasattr(u, 'user_type') and u.user_type == 'admin'))
def admin_assignment_detail_view(request, assignment_id):
    assignment = get_object_or_404(Assignment.objects.select_related('student', 'writer'), id=assignment_id)
    bids = Bid.objects.filter(assignment=assignment).select_related('writer').order_by('-created_at')

    context = {
        'assignment': assignment,
        'bids': bids,
        'page_title': f"Details for Assignment: {assignment.title[:30]}..." if len(assignment.title) > 33 else f"Details for Assignment: {assignment.title}"
    }
    return render(request, 'assignments/admin_assignment_detail.html', context)
