from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, CustomerProfile, VendorProfile, Address


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = _('Customer Profile')


class VendorProfileInline(admin.StackedInline):
    model = VendorProfile
    can_delete = False
    verbose_name_plural = _('Vendor Profile')
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'preferred_language')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('SevaSetu Info'), {'fields': ('role', 'phone_number', 'preferred_language', 'profile_photo')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('SevaSetu Info'), {'fields': ('role', 'phone_number', 'preferred_language')}),
    )

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == User.ROLE_CUSTOMER:
                return [CustomerProfileInline]
            elif obj.role == User.ROLE_VENDOR:
                return [VendorProfileInline]
        return []


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified', 'is_available', 'rating', 'total_jobs_completed', 'wallet_balance')
    list_filter = ('is_verified', 'is_available')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'aadhaar_number')
    actions = ['verify_vendors', 'reject_vendors']

    def verify_vendors(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
        self.message_user(request, _('Selected vendors have been verified.'))
    verify_vendors.short_description = _('Verify selected vendors')

    def reject_vendors(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, _('Selected vendors have been rejected.'))
    reject_vendors.short_description = _('Reject selected vendors')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'label', 'area', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('user__username', 'address_line', 'landmark')
