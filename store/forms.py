from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm,
)
from django.contrib.auth.models import User
from .models import Product, UserProfile, Order, Review, ContactMessage


import re

CA_POSTAL = re.compile(r'^[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d$', re.I)


def _clean_postal(value, required):
    """Validate and tidy a Canadian postal code into 'N9A 1A1' form."""
    value = (value or '').strip().upper()
    if not value:
        if required:
            raise forms.ValidationError('Postal code is required.')
        return value
    if not CA_POSTAL.match(value):
        raise forms.ValidationError('Enter a valid postal code, for example N9A 1A1.')
    value = value.replace(' ', '').replace('-', '')
    return f'{value[:3]} {value[3:]}'


def _bootstrap(fields):
    """Attach the Bootstrap 'form-control' class to a set of fields."""
    for f in fields.values():
        existing = f.widget.attrs.get('class', '')
        if isinstance(f.widget, (forms.CheckboxInput, forms.RadioSelect)):
            continue
        f.widget.attrs['class'] = (existing + ' form-control').strip()
class RegisterForm(UserCreationForm):
    # User.email isn't unique at the DB level, so Django's default signup
    # form happily lets two accounts share an address - enforce it here instead.
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)

    def clean_email(self):
        # case-insensitive so Demo@x.com and demo@x.com count as a clash
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'This email address is already taken. Try logging in instead.')
        return email.lower()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)


class PasswordResetRequestForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)


class PasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)


class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'street_address', 'city', 'province',
                  'postal_code', 'country', 'avatar']
        labels = {
            'street_address': 'Street address',
            'postal_code': 'Postal code',
        }
        widgets = {
            'street_address': forms.TextInput(attrs={'placeholder': '123 Ouellette Ave'}),
            'city': forms.TextInput(attrs={'placeholder': 'Windsor'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'N9A 1A1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)

    def clean_postal_code(self):
        return _clean_postal(self.cleaned_data.get('postal_code', ''), required=False)


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'brand', 'description', 'price', 'stock', 'image', 'sizes']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'sizes': forms.TextInput(attrs={'placeholder': 'S,M,L,XL or Regular'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _bootstrap(self.fields)
