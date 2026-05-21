import re
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


PHONE_REGEX = RegexValidator(
    regex=r'^\+91[6-9]\d{9}$',
    message=_('Enter a valid Indian phone number: +91XXXXXXXXXX')
)


class User(AbstractUser):
    ROLE_CUSTOMER = 'customer'
    ROLE_VENDOR = 'vendor'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, _('Customer')),
        (ROLE_VENDOR, _('Vendor')),
        (ROLE_ADMIN, _('Admin')),
    ]

    LANG_MR = 'mr'
    LANG_HI = 'hi'
    LANG_EN = 'en'
    LANG_CHOICES = [
        (LANG_MR, 'मराठी'),
        (LANG_HI, 'हिंदी'),
        (LANG_EN, 'English'),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        verbose_name=_('Role')
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[PHONE_REGEX],
        unique=True,
        verbose_name=_('Phone Number')
    )
    preferred_language = models.CharField(
        max_length=2,
        choices=LANG_CHOICES,
        default=LANG_EN,
        verbose_name=_('Preferred Language')
    )
    profile_photo = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name=_('Profile Photo')
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone_number']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    @property
    def is_vendor(self):
        return self.role == self.ROLE_VENDOR

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_staff


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_addresses',
        verbose_name=_('User')
    )
    label = models.CharField(max_length=50, verbose_name=_('Label'), default='Home')
    address_line = models.TextField(verbose_name=_('Address Line'))
    landmark = models.CharField(max_length=200, blank=True, verbose_name=_('Landmark'))
    area = models.ForeignKey(
        'locations.Area',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Area')
    )
    is_default = models.BooleanField(default=False, verbose_name=_('Default Address'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return f'{self.label} - {self.user.username}'

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('User')
    )
    default_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_for',
        verbose_name=_('Default Address')
    )

    class Meta:
        verbose_name = _('Customer Profile')
        verbose_name_plural = _('Customer Profiles')

    def __str__(self):
        return f'Customer: {self.user.get_full_name()}'


class VendorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        verbose_name=_('User')
    )
    aadhaar_number = models.CharField(
        max_length=12,
        unique=True,
        verbose_name=_('Aadhaar Number')
    )
    pan_number = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('PAN Number')
    )
    service_areas = models.ManyToManyField(
        'locations.Area',
        blank=True,
        related_name='vendors',
        verbose_name=_('Service Areas')
    )
    skills = models.ManyToManyField(
        'services.ServiceProblem',
        blank=True,
        related_name='qualified_vendors',
        verbose_name=_('Skills')
    )
    is_verified = models.BooleanField(default=False, verbose_name=_('Verified'))
    is_available = models.BooleanField(default=True, verbose_name=_('Available'))
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Rating')
    )
    total_jobs_completed = models.PositiveIntegerField(default=0, verbose_name=_('Total Jobs'))
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_('Wallet Balance')
    )
    id_proof_front = models.ImageField(
        upload_to='vendor_docs/',
        null=True,
        blank=True,
        verbose_name=_('ID Proof Front')
    )
    id_proof_back = models.ImageField(
        upload_to='vendor_docs/',
        null=True,
        blank=True,
        verbose_name=_('ID Proof Back')
    )
    years_of_experience = models.PositiveIntegerField(default=0, verbose_name=_('Years of Experience'))
    same_professional_eligible = models.BooleanField(
        default=True,
        verbose_name=_('Same Professional Eligible')
    )
    bio = models.TextField(blank=True, verbose_name=_('Bio'))
    verification_notes = models.TextField(blank=True, verbose_name=_('Verification Notes'))
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Verified At'))

    class Meta:
        verbose_name = _('Vendor Profile')
        verbose_name_plural = _('Vendor Profiles')

    def __str__(self):
        return f'Vendor: {self.user.get_full_name()} ({"Verified" if self.is_verified else "Pending"})'

    def update_rating(self):
        from bookings.models import Review
        reviews = Review.objects.filter(vendor=self.user)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.rating = round(avg, 2)
            self.save(update_fields=['rating'])
