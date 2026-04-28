"""
AptiTrack Forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    """Custom signup form with email."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Choose a username',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Styled login form."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Username',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })


class ProfileForm(forms.Form):
    """Profile edit form."""
    first_name = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'})
    )
    bio = forms.CharField(
        max_length=500, required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Tell us about yourself...', 'rows': 3})
    )


class QuizConfigForm(forms.Form):
    """Quiz configuration form."""
    QUESTION_COUNTS = [(10, '10 Questions'), (15, '15 Questions'), (20, '20 Questions'), (30, '30 Questions')]
    TIME_LIMITS = [(10, '10 Minutes'), (15, '15 Minutes'), (20, '20 Minutes'), (30, '30 Minutes'), (45, '45 Minutes'), (60, '60 Minutes')]

    category = forms.CharField(required=False, widget=forms.HiddenInput())
    company = forms.CharField(required=False, widget=forms.HiddenInput())
    difficulty = forms.ChoiceField(
        choices=[('', 'All Levels'), ('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    num_questions = forms.ChoiceField(
        choices=QUESTION_COUNTS,
        initial=20,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    time_limit = forms.ChoiceField(
        choices=TIME_LIMITS,
        initial=30,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
