from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    """
    User registration form with avatar support
    """

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "avatar",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Enter a username'
        self.fields['email'].widget.attrs['placeholder'] = 'your@email.com'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password (8+ chars)'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    User profile update form
    """

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "avatar",
        ]
