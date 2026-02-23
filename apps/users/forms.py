from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email', 
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email'
        })
    )

    first_name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
        })
    )

    last_name = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name (optional)',
        })
    )

    # Role is FIXED to student — only admin can create faculty/vendor accounts
    # The hidden field is kept so the model still receives it
    role = forms.CharField(widget=forms.HiddenInput(), initial='student')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })

    def clean_role(self):
        # Always force student regardless of what was posted
        return 'student'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.username   = self.cleaned_data['email']
        user.role       = 'student'
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user
