from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.forms import ModelForm


User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    """Authentication form which uses bootstrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'login or email'}))
    password = forms.CharField(label='Your password',
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder': 'password'}))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True,
                             help_text='* Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)
