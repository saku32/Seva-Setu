from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate
from .forms import CustomerRegistrationForm, VendorRegistrationForm, LoginForm, ProfileUpdateForm, AddressForm
from .models import User, Address
import logging

logger = logging.getLogger('sevasetu')


def register_customer(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            activate(user.preferred_language)
            request.session['django_language'] = user.preferred_language
            login(request, user)
            logger.info(f'New customer registered: {user.username}')
            messages.success(request, _('Welcome to SevaSetu! Your account has been created.'))
            return redirect('dashboard:home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register_customer.html', {'form': form})


def register_vendor(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            activate(user.preferred_language)
            request.session['django_language'] = user.preferred_language
            login(request, user)
            logger.info(f'New vendor registered: {user.username}')
            messages.success(request, _('Registration submitted! Please wait for admin verification.'))
            return redirect('dashboard:home')
    else:
        form = VendorRegistrationForm()
    return render(request, 'accounts/register_vendor.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            activate(user.preferred_language)
            request.session['django_language'] = user.preferred_language
            next_url = request.GET.get('next', 'dashboard:home')
            messages.success(request, _('Welcome back, %(name)s!') % {'name': user.first_name or user.username})
            return redirect(next_url)
        else:
            messages.error(request, _('Invalid username or password.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, _('You have been logged out.'))
    return redirect('/')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            activate(user.preferred_language)
            request.session['django_language'] = user.preferred_language
            messages.success(request, _('Profile updated successfully.'))
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile_update.html', {'form': form})


@login_required
def address_list(request):
    addresses = request.user.saved_addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, _('Address added successfully.'))
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': _('Add Address')})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, _('Address updated.'))
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': _('Edit Address')})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, _('Address deleted.'))
    return redirect('accounts:address_list')
