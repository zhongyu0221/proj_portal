from django import forms

from .models import User, UserProfile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name', 'email', 'is_active')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        
        # Add help text and placeholders
        self.fields['username'].help_text = 'Choose a unique username for login'
        self.fields['email'].help_text = 'This email will be used for password reset'
        self.fields['first_name'].help_text = 'Enter the member\'s first name'
        self.fields['last_name'].help_text = 'Enter the member\'s last name'
        
        # Add placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'e.g., john.doe'})
        self.fields['email'].widget.attrs.update({'placeholder': 'e.g., john.doe@company.com'})
        self.fields['first_name'].widget.attrs.update({'placeholder': 'e.g., John'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'e.g., Doe'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                if self.instance and self.instance.pk:
                    # For updates, allow if it's the same user
                    if self.instance.email != email:
                        raise forms.ValidationError("This email address is already in use.")
                else:
                    # For new users, always check
                    raise forms.ValidationError("This email address is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                if self.instance and self.instance.pk:
                    # For updates, allow if it's the same user
                    if self.instance.username != username:
                        raise forms.ValidationError("This username is already taken.")
                else:
                    # For new users, always check
                    raise forms.ValidationError("This username is already taken.")
        return username

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        # Add help text and placeholders
        self.fields['phone'].help_text = 'Enter contact phone number (optional)'
        self.fields['city'].help_text = 'Enter city/location (optional)'
        self.fields['user_level'].help_text = 'Select the appropriate role for this member'
        
        # Add placeholders
        self.fields['phone'].widget.attrs.update({'placeholder': 'e.g., +1-555-123-4567'})
        self.fields['city'].widget.attrs.update({'placeholder': 'e.g., New York'})
        
        # Make phone and city optional
        self.fields['phone'].required = False
        self.fields['city'].required = False



class CustomPasswordResetForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'id': 'username'
        }),
        help_text='Enter the username associated with your account'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'id': 'email'
        }),
        help_text='Enter the email address associated with your account'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        if username and email:
            try:
                user = User.objects.get(username=username, email=email)
                if not user.is_active:
                    raise forms.ValidationError("This account is inactive. Please contact an administrator.")
            except User.DoesNotExist:
                raise forms.ValidationError("No user found with this username and email combination.")
        
        return cleaned_data


# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = UserProfile
#         fields = ('bsd_id', 'lab', 'user_level')
