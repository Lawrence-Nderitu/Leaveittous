from django.db import models
from django.conf import settings
from django.urls import reverse # Add this import

# It's good practice to directly reference settings.AUTH_USER_MODEL
# for ForeignKey relationships to the User model, especially if the User model
# is in a different app.

class Assignment(models.Model):
    # title, description, subject, deadline, budget, student, writer, created_at, updated_at (existing fields)
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(max_length=100, blank=True)
    deadline = models.DateTimeField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assignments_as_student',
        # The limit_choices_to using 'user_type' assumes this field is on the User model.
        # This will work correctly once AUTH_USER_MODEL points to 'users.User'.
        limit_choices_to={'user_type': 'student'},
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments_as_writer',
        limit_choices_to={'user_type': 'writer'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('submitted', 'Submitted for Review'), # New
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(
        max_length=25, # Increased length for 'Submitted for Review'
        choices=STATUS_CHOICES,
        default='open',
    )

    # New fields for submission
    submitted_work = models.FileField(
        upload_to='submissions/%Y/%m/%d/',
        null=True,
        blank=True
    )
    submission_notes = models.TextField(
        null=True,
        blank=True
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # This typically points to a detail view for the object.
        # We have two detail views: one for students, one for writers.
        # Defaulting to the student's detail view as they are the owner.
        return reverse('assignments:assignment_detail_student', kwargs={'assignment_id': self.pk})

class Bid(models.Model):
    # Ensure Assignment model is defined before Bid, or use string reference if necessary.
    # Here, it's defined above, so direct reference is fine.
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='bids')
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bids',
        limit_choices_to={'user_type': 'writer'},
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proposal = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )

    def __str__(self):
        return f"Bid for {self.assignment.title} by {self.writer.username}"
