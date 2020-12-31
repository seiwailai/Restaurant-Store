from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import (
    UserCreationForm, 
    AuthenticationForm, 
    PasswordResetForm, 
    SetPasswordForm, 
    PasswordChangeForm
)
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.widgets import (
    TextInput, 
    PasswordInput, 
    NumberInput, 
    EmailInput, 
    CheckboxInput
)
from .models import DeliveryInfo
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget


class CreateUserForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'Password'})
        self.fields['password2'].widget = PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'Confirm Password'})

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        ]
        widgets = {
            'username': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'Username'}),
            'email': EmailInput(attrs={'class':'form-control mb-2', 'placeholder': 'Email'}),
            'first_name': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'First Name'}),
            'last_name': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'Last Name'}),
        }

    def clean_email(self):
        data = self.cleaned_data['email']
        duplicate_users = User.objects.filter(email=data)
        if self.instance.pk is not None:  # If you're editing an user, remove him from the duplicated results
            duplicate_users = duplicate_users.exclude(pk=self.instance.pk)
        if duplicate_users.exists():
            raise forms.ValidationError("E-mail is already registered.")
        return data

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2', 'placeholder': 'Username', 'id':'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control mb-2',
        'placeholder': 'Password',
        'id': 'password',
            }
        )
    )

class CreateDeliveryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateDeliveryForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['email'].widget.attrs['disabled'] = True

    class Meta:
        model = DeliveryInfo
        fields = [
            'firstName',
            'lastName',
            'phone',
            'email',
            'address1',
            'address2',
            'city',
            'state',
            'country',
            'postalCode',
            'customer',
            'default',
        ]
        widgets = {
            'firstName': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'First Name'}),
            'lastName': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'Last Name'}),
            'phone': PhoneNumberInternationalFallbackWidget(attrs={'class':'form-control mb-2', 'placeholder': 'Phone'}),
            'email': EmailInput(attrs={'class':'form-control mb-2', 'placeholder': 'Email'}),
            'address1': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'Address Line 1'}),
            'address2': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'Address Line 2'}),
            'city': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'City'}),
            'state': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'State'}),
            'country': TextInput(attrs={'class':'form-control mb-2', 'placeholder': 'Country'}),
            'postalCode': NumberInput(attrs={'class':'form-control mb-2', 'placeholder': 'Postal Code'}),
            'default': CheckboxInput(attrs={'class':'mb-2', 'placeholder': 'Default'}),
        }


class PasswordResetCustomForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetCustomForm, self).__init__(*args, **kwargs)
    
    email = forms.EmailField(label='Email', widget=EmailInput(attrs={
    'class': 'form-control mb-2',
    'placeholder': 'Email',
    'type': 'email',
    'name': 'email'
    }))


class SetPasswordCustomForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordCustomForm, self).__init__(*args, **kwargs)
    
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'New Password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'New Password Confirmation'}),
    )


class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeCustomForm, self).__init__(*args, **kwargs)
    
    old_password = forms.CharField(
        label="Old Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'Old Password'}),
    )
    
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'New Password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={'class':'form-control mb-2', 'placeholder': 'New Password Confirmation'}),
    )
