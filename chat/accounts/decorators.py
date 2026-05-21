from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_customer:
            messages.error(request, _('This page is for customers only.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def vendor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_vendor:
            messages.error(request, _('This page is for vendors only.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_admin_user:
            messages.error(request, _('Admin access required.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def verified_vendor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next={request.path}')
        if not request.user.is_vendor:
            messages.error(request, _('This page is for vendors only.'))
            return redirect('dashboard:home')
        try:
            if not request.user.vendor_profile.is_verified:
                messages.warning(request, _('Your account is pending verification. Please wait for admin approval.'))
                return redirect('dashboard:home')
        except Exception:
            messages.error(request, _('Vendor profile not found.'))
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper
