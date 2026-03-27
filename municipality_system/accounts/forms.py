from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterForm(UserCreationForm):
    """Registration form with profile fields."""
    first_name = forms.CharField(max_length=50, required=True,
                                  widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone_number = forms.CharField(max_length=15, required=False,
                                    widget=forms.TextInput(attrs={'placeholder': '0XX XXX XXXX'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2,
                                                                            'placeholder': 'Street Address, Suburb, City'}))
    ward_number = forms.CharField(max_length=10, required=False,
                                   widget=forms.TextInput(attrs={'placeholder': 'e.g. Ward 5'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data.get('phone_number', ''),
                address=self.cleaned_data.get('address', ''),
                ward_number=self.cleaned_data.get('ward_number', ''),
            )
        return user


class LoginForm(AuthenticationForm):
    """Custom styled login form."""
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class UserUpdateForm(forms.ModelForm):
    """Update basic user info."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """Update profile info."""
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'ward_number', 'profile_picture']
