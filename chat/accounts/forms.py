from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User, VendorProfile, CustomerProfile, Address


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label=_('First Name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Last Name'))
    email = forms.EmailField(required=True, label=_('Email'))
    phone_number = forms.CharField(max_length=15, required=True, label=_('Phone Number'),
                                   help_text=_('Format: +91XXXXXXXXXX'))
    preferred_language = forms.ChoiceField(choices=User.LANG_CHOICES, label=_('Preferred Language'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number',
                  'preferred_language', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_CUSTOMER
        if commit:
            user.save()
            # Signal auto-creates CustomerProfile; use get_or_create to avoid duplicate
            CustomerProfile.objects.get_or_create(user=user)
        return user


class VendorRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label=_('First Name'))
    last_name = forms.CharField(max_length=30, required=True, label=_('Last Name'))
    email = forms.EmailField(required=True, label=_('Email'))
    phone_number = forms.CharField(max_length=15, required=True, label=_('Phone Number'),
                                   help_text=_('Format: +91XXXXXXXXXX'))
    preferred_language = forms.ChoiceField(choices=User.LANG_CHOICES, label=_('Preferred Language'))
    aadhaar_number = forms.CharField(max_length=12, required=True, label=_('Aadhaar Number'),
                                     help_text=_('12-digit Aadhaar number'))
    pan_number = forms.CharField(max_length=10, required=False, label=_('PAN Number'))
    years_of_experience = forms.IntegerField(min_value=0, max_value=50, label=_('Years of Experience'))
    id_proof_front = forms.ImageField(required=True, label=_('ID Proof (Front)'))
    id_proof_back = forms.ImageField(required=False, label=_('ID Proof (Back)'))
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label=_('About Yourself'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number',
                  'preferred_language', 'password1', 'password2')

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number')
        if aadhaar and not aadhaar.isdigit():
            raise forms.ValidationError(_('Aadhaar number must contain only digits.'))
        if aadhaar and len(aadhaar) != 12:
            raise forms.ValidationError(_('Aadhaar number must be exactly 12 digits.'))
        return aadhaar

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.ROLE_VENDOR
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                aadhaar_number=self.cleaned_data['aadhaar_number'],
                pan_number=self.cleaned_data.get('pan_number', ''),
                years_of_experience=self.cleaned_data.get('years_of_experience', 0),
                id_proof_front=self.cleaned_data.get('id_proof_front'),
                id_proof_back=self.cleaned_data.get('id_proof_back'),
                bio=self.cleaned_data.get('bio', ''),
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username / Phone'), widget=forms.TextInput(
        attrs={'placeholder': _('Username or Phone')}))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput(
        attrs={'placeholder': _('Password')}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'preferred_language', 'profile_photo')


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('label', 'address_line', 'landmark', 'area', 'is_default')
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 2}),
        }
