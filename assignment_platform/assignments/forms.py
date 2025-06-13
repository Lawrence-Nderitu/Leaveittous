from django import forms
from .models import Assignment, Bid # Import Assignment and Bid models

class AssignmentCreateForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = [
            'title', 'description', 'subject', 'deadline', 'budget',
            'requirement_file_1', 'requirement_file_2', 'requirement_file_3' # Add new fields
        ]
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
            # Add widgets for the new file fields
            'requirement_file_1': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'}),
            'requirement_file_2': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'}),
            'requirement_file_3': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100'}),
        }
        # Optional: Add labels if you want to customize them from the model's verbose_name
        # labels = {
        #     'requirement_file_1': 'Primary Requirement File (Optional)',
        #     'requirement_file_2': 'Secondary Requirement File (Optional)',
        # }

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

    def clean_submitted_work(self):
        submitted_file = self.cleaned_data.get('submitted_work', None)
        if submitted_file:
            # Max file size: 100MB
            max_size = 100 * 1024 * 1024
            if submitted_file.size > max_size:
                # Convert max_size to MB for the error message
                max_size_mb = max_size / (1024 * 1024)
                raise forms.ValidationError(f"The uploaded file is too large. Please upload a file smaller than {max_size_mb:.0f}MB.")
        # If the field is required (blank=False on model), Django's default validation
        # for required fields will handle the case where submitted_file is None.
        # If blank=True was on the model and you wanted to make it conditionally required here,
        # you might add:
        # else:
        #     raise forms.ValidationError("This field is required.")
        return submitted_file
