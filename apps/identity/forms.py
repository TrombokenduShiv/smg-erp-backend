# apps/identity/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    # We must explicitly declare password_2 so the form knows to expect it
    password_2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Enter the same password as before, for verification.",
    )

    class Meta:
        model = User
        # Fields to show on the "Add" page
        fields = ('email', 'role', 'department') 

    def clean(self):
        # This is where Django validates the two passwords match.
        # It relies on 'password' and 'password_2' fields being present.
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password and password_2 and password != password_2:
            self.add_error('password_2', "Passwords don't match")
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'