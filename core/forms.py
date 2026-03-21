"""
Forms for User Authentication and Registration

Handles citizen signup, login, profile editing, and business signup.
Part of the "Citizens First" strategy - free citizen accounts, paid business accounts.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from core.models import UserProfile, City


class CitizenSignupForm(UserCreationForm):
    """
    Citizen Registration Form (FREE)
    
    Fields:
    - username: Unique username
    - email: Email (required for verification)
    - first_name, last_name: Full name
    - password1, password2: Password confirmation
    - default_city: Their Springfield (optional)
    - email_weekly_digest, email_new_businesses, email_new_events: Email preferences
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'john@example.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'John'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Doe'
        })
    )
    
    default_city = forms.ModelChoiceField(
        queryset=City.objects.all().order_by('state__name', 'name'),
        required=False,
        empty_label="-- Select your Springfield --",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Email preferences (default True for weekly digest and new businesses)
    email_weekly_digest = forms.BooleanField(
        required=False,
        initial=True,
        label="Weekly Digest",
        help_text="Get a weekly summary of local news and events"
    )
    
    email_new_businesses = forms.BooleanField(
        required=False,
        initial=True,
        label="New Businesses",
        help_text="Notify me when businesses join my Springfield"
    )
    
    email_new_events = forms.BooleanField(
        required=False,
        initial=False,
        label="Events",
        help_text="Get notified about upcoming local events"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind CSS classes to all fields
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
    
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email or log in.")
        return email
    
    def save(self, commit=True):
        """Save user and create UserProfile"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # UserProfile is auto-created by signal, just update it
            profile = user.userprofile
            profile.user_type = 'CITIZEN'  # FREE account
            profile.default_city = self.cleaned_data.get('default_city')
            profile.email_weekly_digest = self.cleaned_data.get('email_weekly_digest', True)
            profile.email_new_businesses = self.cleaned_data.get('email_new_businesses', True)
            profile.email_new_events = self.cleaned_data.get('email_new_events', False)
            profile.save()
        
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Custom Login Form
    
    Allows login with username or email
    """
    
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'johndoe or john@example.com',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label="Remember me"
    )
    
    def clean_username(self):
        """Allow email as username"""
        username_or_email = self.cleaned_data.get('username')
        
        # Check if it's an email
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                return user.username
            except User.DoesNotExist:
                # Will fail in parent clean() method
                pass
        
        return username_or_email


class ProfileEditForm(forms.ModelForm):
    """
    Edit User Profile
    
    Allows users to update their info and preferences
    """
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'default_city',
            'phone',
            'bio',
            'profile_photo',
            'email_weekly_digest',
            'email_new_businesses',
            'email_new_events'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'default_city': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def save(self, commit=True):
        """Save both User and UserProfile"""
        profile = super().save(commit=False)
        
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            
            if commit:
                self.user.save()
                profile.save()
        
        return profile


class BusinessSignupForm(UserCreationForm):
    """
    Business Owner Registration Form (PAID - 30-day FREE trial)
    
    Creates a user account AND prompts for first business
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'owner@business.com'
        })
    )
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    # Business info (for first business)
    business_name = forms.CharField(
        max_length=200,
        required=True,
        label="Business Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    business_city = forms.ModelChoiceField(
        queryset=City.objects.all().order_by('state__name', 'name'),
        required=True,
        label="Springfield Location",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email
    
    def save(self, commit=True):
        """Save user and create UserProfile with BUSINESS type"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Update UserProfile to BUSINESS type
            profile = user.userprofile
            profile.user_type = 'BUSINESS'  # PAID account (30-day trial)
            profile.default_city = self.cleaned_data.get('business_city')
            profile.save()
        
        return user


class BusinessClaimForm(forms.Form):
    """
    Claim an existing business
    
    User provides business ID and verification method (email link)
    """
    
    business_email = forms.EmailField(
        required=True,
        label="Business Email Address",
        help_text="We'll send a verification link to this email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    verification_method = forms.ChoiceField(
        choices=[('EMAIL', 'Email Link')],
        initial='EMAIL',
        widget=forms.HiddenInput()
    )
