from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email', max_length=100, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': '', 'type': 'email', 'placeholder': 'Email'})
        self.fields['password'].widget.attrs.update({'class': '', 'placeholder': 'Password'})


class RegisterForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('voter', 'Voter'),
        ('candidate', 'Candidate'),
    )

    first_name = forms.CharField(
        label='First Name', max_length=30, required=True)
    last_name = forms.CharField(
        label='Last Name', max_length=30, required=True)
    email = forms.EmailField(label='Email', max_length=75, required=True)
    roll_no = forms.CharField(label='Roll No', max_length=10, required=True)
    user_type = forms.ChoiceField(label="User type", choices=USER_TYPE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'password1', 'password2', 'user_type')
    
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'class': '', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'class': '', 'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'class': '', 'placeholder': 'Email'})
        self.fields['roll_no'].widget.attrs.update({'class': '', 'placeholder': 'Roll No.'})
        self.fields['user_type'].widget.attrs.update({'class': ''})
        self.fields['password1'].widget.attrs.update({'class': '', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': '', 'placeholder': 'Confirm password'})

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email

    def clean_user_type(self):
        user_type = self.cleaned_data['user_type']
        if user_type not in [choice[0] for choice in self.USER_TYPE_CHOICES]:
            raise ValidationError("Invalid user type selected")
        return user_type

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = user.email
        user.user_type = self.cleaned_data['user_type']

        if user.user_type == 'admin':
            raise ValidationError("Invalid user type selected")

        if commit:
            user.save()
        return user
