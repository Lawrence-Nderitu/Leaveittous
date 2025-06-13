from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from datetime import timedelta

from .models import Assignment, Bid

# Use a custom user model if defined, otherwise default User
User = get_user_model()

class AssignmentWorkflowTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.student_password = 'studentpassword'
        cls.student_user = User.objects.create_user(
            username='teststudent',
            password=cls.student_password,
            email='student@example.com',
            user_type='student'
        )

        cls.other_student_user = User.objects.create_user(
            username='otherstudent',
            password='otherstudentpassword',
            email='otherstudent@example.com',
            user_type='student'
        )

        cls.writer_password = 'writerpassword'
        cls.writer_user = User.objects.create_user(
            username='testwriter',
            password=cls.writer_password,
            email='writer@example.com',
            user_type='writer'
        )

        # Basic assignment data
        cls.assignment_data = {
            'title': 'Test Assignment Title',
            'description': 'Detailed description of the test assignment.',
            'subject': 'Test Subject',
            'deadline': timezone.now() + timedelta(days=7),
            'budget': 100.00,
        }

    def setUp(self):
        """Set up client and log in student user for each test."""
        self.client = Client()
        self.client.login(username=self.student_user.username, password=self.student_password)

        # Create dummy files for upload tests
        self.file1 = SimpleUploadedFile("file1.txt", b"file_content_1", content_type="text/plain")
        self.file2 = SimpleUploadedFile("file2.txt", b"file_content_2", content_type="text/plain")
        self.file3 = SimpleUploadedFile("file3.txt", b"file_content_3", content_type="text/plain")


    def test_create_assignment_with_three_files(self):
        """Test creating an assignment with three requirement files."""
        form_data = self.assignment_data.copy()
        form_data.update({
            'requirement_file_1': self.file1,
            'requirement_file_2': self.file2,
            'requirement_file_3': self.file3,
        })

        response = self.client.post(reverse('assignments:create_assignment'), data=form_data)

        self.assertEqual(response.status_code, 302, "Should redirect after successful creation.")
        self.assertRedirects(response, reverse('users:student_dashboard'), msg_prefix="Redirects to student dashboard.")

        self.assertTrue(Assignment.objects.exists(), "Assignment object should be created.")
        created_assignment = Assignment.objects.first()

        self.assertEqual(created_assignment.student, self.student_user)
        self.assertEqual(created_assignment.title, form_data['title'])
        self.assertTrue(created_assignment.requirement_file_1.name, "File 1 should be saved.")
        self.assertTrue(created_assignment.requirement_file_2.name, "File 2 should be saved.")
        self.assertTrue(created_assignment.requirement_file_3.name, "File 3 should be saved.")

    def _create_test_assignment(self, status='open', student=None, writer=None):
        """Helper method to create an assignment for tests."""
        if student is None:
            student = self.student_user

        assignment = Assignment.objects.create(
            student=student,
            title="Sample Assignment for Cancellation",
            description="A test assignment.",
            subject="Testing",
            deadline=timezone.now() + timedelta(days=5),
            budget=50.00,
            status=status
        )
        if writer and status == 'assigned':
            assignment.writer = writer
            assignment.save()
        return assignment

    def test_cancel_open_assignment_by_student_success(self):
        """Test successful cancellation of an 'open' assignment by its student owner."""
        assignment = self._create_test_assignment(status='open')

        response = self.client.post(reverse('assignments:cancel_assignment', args=[assignment.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:student_dashboard'))

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'cancelled_by_student')

        # Check for messages (basic check, actual message content might need more specific tools/setup)
        # For Django 4.2+ you can use self.assertMesages
        # For now, we'll check if the redirect implies success, which the view logic does.
        # To properly test messages, you might need to inspect response.context or use a helper.
        # For this example, we'll rely on the redirect and status change as primary success indicators.
        # A more robust way would be to check messages if your test setup supports it easily.
        # e.g. messages = list(get_messages(response.wsgi_request))
        # self.assertTrue(any("has been cancelled" in str(m) for m in messages))

    def test_cancel_assigned_assignment_by_student_success(self):
        """Test successful cancellation of an 'assigned' assignment by its student owner."""
        assignment = self._create_test_assignment(status='assigned', writer=self.writer_user)

        response = self.client.post(reverse('assignments:cancel_assignment', args=[assignment.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:student_dashboard'))

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, 'cancelled_by_student')

    def test_cancel_assignment_forbidden_not_owner(self):
        """Test cancellation is forbidden if the logged-in student is not the owner."""
        assignment = self._create_test_assignment(status='open', student=self.other_student_user)
        original_status = assignment.status

        response = self.client.post(reverse('assignments:cancel_assignment', args=[assignment.id]))

        self.assertEqual(response.status_code, 302) # Should redirect (to dashboard typically)
        self.assertRedirects(response, reverse('users:student_dashboard')) # View redirects to dashboard on error

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, original_status, "Assignment status should not change.")
        # Add message assertion here if possible, e.g. "You are not authorized"

    def test_cancel_assignment_forbidden_wrong_status(self):
        """Test cancellation is forbidden for assignments with non-cancellable statuses."""
        for status in ['completed', 'submitted', 'cancelled']: # 'cancelled_by_student' is also final
            assignment = self._create_test_assignment(status=status)
            original_status = assignment.status

            response = self.client.post(reverse('assignments:cancel_assignment', args=[assignment.id]))

            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse('users:student_dashboard'))

            assignment.refresh_from_db()
            self.assertEqual(assignment.status, original_status, f"Assignment status '{status}' should not change.")
            # Add message assertion here, e.g. "cannot be cancelled at its current stage"

    def test_cancel_assignment_get_request_redirects_with_info(self):
        """Test that a GET request to cancel_assignment redirects and shows an info message."""
        assignment = self._create_test_assignment(status='open')
        original_status = assignment.status

        response = self.client.get(reverse('assignments:cancel_assignment', args=[assignment.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:student_dashboard'))

        assignment.refresh_from_db()
        self.assertEqual(assignment.status, original_status, "Assignment status should not change on GET request.")
        # Add message assertion for info message if possible.
        # e.g. "To cancel this assignment, please confirm..."

    def tearDown(self):
        # Clean up SimpleUploadedFile resources if necessary, though Django's test runner usually handles temporary files.
        # If files were saved to media_root and not cleaned up by test runner, add cleanup here.
        pass

# Example of how to check messages if you have a utility or want to implement one
# from django.contrib.messages import get_messages
# messages = list(get_messages(response.wsgi_request))
# self.assertEqual(len(messages), 1)
# self.assertEqual(str(messages[0]), "Expected message here")
# Or: self.assertIn("Expected part of message", str(messages[0]))
# For Django 4.2+, client.captureMessage() or response.context['messages'] can be used more easily.
# For now, focusing on status codes, redirects, and DB state.
# Consider adding a helper in a BaseTestCase if message testing is crucial across many tests.
# For instance:
# from django.contrib.messages import get_messages
# class BaseTestCase(TestCase):
#     def assertMessageContains(self, response, expected_message, level=None):
#         messages = list(get_messages(response.wsgi_request))
#         self.assertTrue(any(expected_message in str(m) for m in messages),
#                         msg=f"Message '{expected_message}' not found in {messages}")
#         if level:
#             self.assertTrue(any(m.level == level for m in messages if expected_message in str(m)),
#                             msg=f"Message '{expected_message}' with level {level} not found.")
