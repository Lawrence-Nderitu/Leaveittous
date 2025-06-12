from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from users.models import User # Updated import path

class UserRegistrationForm(UserCreationForm):
    # user_type field is removed from here, it will be set in the view.
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=150, required=False, help_text='Optional.')

    class Meta(UserCreationForm.Meta):
        model = User
        # UserCreationForm.Meta.fields already includes username.
        # Password fields are handled by UserCreationForm itself.
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name',)

class LoginForm(AuthenticationForm):
    pass
