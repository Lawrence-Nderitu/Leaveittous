from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User # Updated import path

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm', 'placeholder': 'you@example.com'})
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm', 'placeholder': 'Your first name'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm', 'placeholder': 'Your last name'})
    )
    # new_password1 and new_password2 will be styled in __init__ by updating their widgets.
    # Explicit re-definitions are removed.

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")
        # UserCreationForm adds new_password1 and new_password2 to its fields by default.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Corrected super call

        common_input_attrs = {
            'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm',
        }

        # Style username field
        self.fields['username'].widget.attrs.update({
            **common_input_attrs, # Spread common attributes
            'placeholder': 'Choose a username'
        })

        # Style password fields inherited from UserCreationForm
        # UserCreationForm names them 'new_password1' and 'new_password2'
        password_widget_attrs = {
            **common_input_attrs,
            'autocomplete': 'new-password',
        }

        if 'new_password1' in self.fields:
            self.fields['new_password1'].widget = forms.PasswordInput(attrs=password_widget_attrs)
            self.fields['new_password1'].widget.attrs['placeholder'] = 'Enter password'
            # Default help_text for new_password1 is usually sufficient.
            # To customize or remove default help_text:
            # self.fields['new_password1'].help_text = 'Your custom help text or None'

        if 'new_password2' in self.fields:
            self.fields['new_password2'].widget = forms.PasswordInput(attrs=password_widget_attrs)
            self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm password'
            # self.fields['new_password2'].help_text = None # Usually no help_text for confirmation by default

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm',
        'placeholder': 'Password'
    }))
