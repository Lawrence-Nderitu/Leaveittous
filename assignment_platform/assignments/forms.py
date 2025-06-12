from django import forms
from .models import Assignment, Bid # Import Assignment and Bid models

class AssignmentCreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'subject', 'deadline', 'budget']
        widgets = {
            'deadline': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm'
                }
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm'
                }
            ),
            'subject': forms.TextInput(
                attrs={
                    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm'
                }
            ),
            'budget': forms.NumberInput(
                attrs={
                    'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm'
                }
            ),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'proposal']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm', 'placeholder': 'Your bid amount'}),
            'proposal': forms.Textarea(attrs={'rows': 5, 'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm', 'placeholder': 'Explain why you are a good fit for this assignment...'}),
        }

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Assignment # Should be Assignment model
        fields = ['submitted_work', 'submission_notes']
        widgets = {
            'submitted_work': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'}),
            'submission_notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm', 'placeholder': 'Optional: Add any notes for the student regarding your submission.'}),
        }
        labels = {
            'submitted_work': 'Upload Your Completed Work',
            'submission_notes': 'Submission Notes (Optional)',
        }
