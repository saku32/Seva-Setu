from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from accounts.decorators import customer_required, vendor_required
from services.models import ServiceProblem
from locations.models import Area
from .models import Booking, BookingStatusLog, BookingPhoto, Review, Complaint, VendorETA
import razorpay
import hmac
import hashlib
import json
import logging

logger = logging.getLogger('sevasetu')


@customer_required
def booking_new(request):
    problem_slug = request.GET.get('problem')
    problem = None
    if problem_slug:
        problem = ServiceProblem.objects.filter(slug=problem_slug, is_active=True).first()

    if request.method == 'POST':
        problem_id = request.POST.get('problem_id')
        area_id = request.POST.get('area_id')
        address_line = request.POST.get('address_line', '')
        landmark = request.POST.get('landmark', '')
        preferred_date = request.POST.get('preferred_date')
        preferred_time_slot = request.POST.get('preferred_time_slot', 'morning')
        description = request.POST.get('description', '')
        payment_method = request.POST.get('payment_method', 'cod')
        same_prof = request.POST.get('same_professional') == '1'

        try:
            problem_obj = ServiceProblem.objects.get(id=problem_id)
            area_obj = Area.objects.get(id=area_id)
        except (ServiceProblem.DoesNotExist, Area.DoesNotExist):
            messages.error(request, _('Invalid service or area. Please try again.'))
            return redirect('services:category_list')

        # Check for previous vendor (same professional feature)
        prev_vendor = None
        if same_prof:
            prev_booking = Booking.objects.filter(
                customer=request.user,
                problem__category=problem_obj.category,
                vendor__isnull=False,
                status=Booking.STATUS_CLOSED
            ).order_by('-created_at').first()
            if prev_booking:
                prev_vendor = prev_booking.vendor

        booking = Booking.objects.create(
            customer=request.user,
            problem=problem_obj,
            area=area_obj,
            address_line=address_line,
            landmark=landmark,
            preferred_date=preferred_date,
            preferred_time_slot=preferred_time_slot,
            description=description,
            voice_transcript=request.POST.get('voice_transcript', ''),
            base_price=problem_obj.base_price,
            total_price=problem_obj.base_price,
            payment_method=payment_method,
            same_professional_requested=same_prof,
            assigned_previous_vendor=prev_vendor,
        )

        BookingStatusLog.objects.create(
            booking=booking,
            from_status='',
            to_status=Booking.STATUS_REQUESTED,
            changed_by=request.user,
            notes='Booking created by customer'
        )

        logger.info(f'Booking created: {booking.display_id} by {request.user.username}')
        messages.success(request, _('Booking %(id)s created! We will assign a vendor shortly.') % {'id': booking.display_id})
        return redirect('bookings:detail', booking_id=booking.display_id)

    from locations.models import District
    districts = District.objects.filter(is_active=True)
    addresses = request.user.saved_addresses.all()
    return render(request, 'bookings/booking_new.html', {
        'problem': problem,
        'districts': districts,
        'addresses': addresses,
        'today': date.today(),
    })


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id)
    if request.user != booking.customer and request.user != booking.vendor and not request.user.is_admin_user:
        messages.error(request, _('You do not have permission to view this booking.'))
        return redirect('dashboard:home')

    status_logs = booking.status_logs.all()
    photos = booking.photos.all()
    review = getattr(booking, 'review', None)
    complaints = booking.complaints.all()
    eta = getattr(booking, 'vendor_eta', None)

    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'status_logs': status_logs,
        'photos': photos,
        'review': review,
        'complaints': complaints,
        'eta': eta,
    })


@login_required
def booking_list(request):
    if request.user.is_vendor:
        bookings = Booking.objects.filter(vendor=request.user).select_related('problem', 'customer', 'area')
    else:
        bookings = Booking.objects.filter(customer=request.user).select_related('problem', 'vendor', 'area')

    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    paginator = Paginator(bookings, 10)
    page = request.GET.get('page', 1)
    page_obj = paginator.get_page(page)
    return render(request, 'bookings/booking_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
    })


@vendor_required
def vendor_update_status(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id, vendor=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        valid_transitions = {
            Booking.STATUS_VENDOR_ASSIGNED: [Booking.STATUS_VENDOR_ACCEPTED, Booking.STATUS_CANCELLED],
            Booking.STATUS_VENDOR_ACCEPTED: [Booking.STATUS_VENDOR_EN_ROUTE],
            Booking.STATUS_VENDOR_EN_ROUTE: [Booking.STATUS_IN_PROGRESS],
            Booking.STATUS_IN_PROGRESS: [Booking.STATUS_WORK_COMPLETED],
        }
        allowed = valid_transitions.get(booking.status, [])
        if new_status in allowed:
            old_status = booking.status
            booking.status = new_status
            booking.save()
            BookingStatusLog.objects.create(
                booking=booking,
                from_status=old_status,
                to_status=new_status,
                changed_by=request.user,
                notes=notes
            )
            logger.info(f'Booking {booking.display_id} status: {old_status} → {new_status}')
            messages.success(request, _('Status updated to %(status)s') % {'status': new_status})
        else:
            messages.error(request, _('Invalid status transition.'))
    return redirect('bookings:detail', booking_id=booking_id)


@customer_required
def customer_confirm(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id, customer=request.user)
    if request.method == 'POST' and booking.status == Booking.STATUS_WORK_COMPLETED:
        old_status = booking.status
        booking.status = Booking.STATUS_CUSTOMER_CONFIRMED
        booking.save()
        BookingStatusLog.objects.create(
            booking=booking, from_status=old_status,
            to_status=Booking.STATUS_CUSTOMER_CONFIRMED,
            changed_by=request.user, notes='Customer confirmed completion'
        )
        # Auto-generate invoice
        from invoices.utils import generate_invoice
        generate_invoice(booking)
        booking.status = Booking.STATUS_INVOICE_GENERATED
        booking.save()
        messages.success(request, _('Thank you! Please leave a review.'))
    return redirect('bookings:detail', booking_id=booking_id)


@vendor_required
def upload_photos(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id, vendor=request.user)
    if request.method == 'POST':
        photo_type = request.POST.get('photo_type', BookingPhoto.PHOTO_AFTER)
        for f in request.FILES.getlist('photos'):
            BookingPhoto.objects.create(
                booking=booking,
                photo=f,
                photo_type=photo_type,
                uploaded_by=request.user,
                caption=request.POST.get('caption', '')
            )
        messages.success(request, _('Photos uploaded successfully.'))
    return redirect('bookings:detail', booking_id=booking_id)


@customer_required
def leave_review(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id, customer=request.user)
    if hasattr(booking, 'review'):
        messages.info(request, _('You have already reviewed this booking.'))
        return redirect('bookings:detail', booking_id=booking_id)
    if booking.status not in [Booking.STATUS_CUSTOMER_CONFIRMED, Booking.STATUS_INVOICE_GENERATED, Booking.STATUS_CLOSED]:
        messages.error(request, _('You can only review completed bookings.'))
        return redirect('bookings:detail', booking_id=booking_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        review_text = request.POST.get('review_text', '')
        Review.objects.create(
            booking=booking,
            customer=request.user,
            vendor=booking.vendor,
            rating=rating,
            review_text=review_text
        )
        # Update vendor rating
        if booking.vendor and hasattr(booking.vendor, 'vendor_profile'):
            booking.vendor.vendor_profile.update_rating()
            if booking.status == Booking.STATUS_INVOICE_GENERATED:
                booking.status = Booking.STATUS_CLOSED
                booking.save()
        messages.success(request, _('Review submitted! Thank you.'))
        return redirect('bookings:detail', booking_id=booking_id)
    return render(request, 'bookings/leave_review.html', {'booking': booking})


@customer_required
def raise_complaint(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id, customer=request.user)
    if request.method == 'POST':
        complaint_type = request.POST.get('complaint_type', 'other')
        description = request.POST.get('description', '')
        guarantee_claim = request.POST.get('guarantee_claim') == '1'
        Complaint.objects.create(
            booking=booking,
            raised_by=request.user,
            complaint_type=complaint_type,
            description=description,
            guarantee_claim=guarantee_claim
        )
        if booking.status not in [Booking.STATUS_CANCELLED]:
            old_status = booking.status
            booking.status = Booking.STATUS_DISPUTED
            booking.save()
            BookingStatusLog.objects.create(
                booking=booking, from_status=old_status,
                to_status=Booking.STATUS_DISPUTED,
                changed_by=request.user, notes='Complaint raised'
            )
        messages.success(request, _('Complaint registered. Our team will contact you within 24 hours.'))
        return redirect('bookings:detail', booking_id=booking_id)
    return render(request, 'bookings/raise_complaint.html', {'booking': booking})


def booking_status_api(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id)
    eta = getattr(booking, 'vendor_eta', None)
    data = {
        'status': booking.status,
        'updated_at': booking.updated_at.isoformat(),
    }
    if eta:
        data['eta'] = {
            'estimated_arrival': eta.estimated_arrival.isoformat(),
            'lat': float(eta.current_latitude) if eta.current_latitude else None,
            'lng': float(eta.current_longitude) if eta.current_longitude else None,
        }
    return JsonResponse(data)


@vendor_required
@require_POST
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id)
    if booking.vendor == request.user and booking.status == Booking.STATUS_VENDOR_ASSIGNED:
        old_status = booking.status
        booking.status = Booking.STATUS_VENDOR_ACCEPTED
        booking.save()
        BookingStatusLog.objects.create(
            booking=booking, from_status=old_status,
            to_status=Booking.STATUS_VENDOR_ACCEPTED,
            changed_by=request.user, notes='Vendor accepted'
        )
        messages.success(request, _('Booking accepted!'))
    return redirect('bookings:detail', booking_id=booking_id)


@customer_required
@require_POST
def create_razorpay_order(request, booking_id):
    """Create a Razorpay order for online payment and return order details as JSON."""
    booking = get_object_or_404(Booking, display_id=booking_id, customer=request.user)
    if booking.payment_status == Booking.PAYMENT_PAID:
        return JsonResponse({'error': 'Already paid'}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(booking.total_price * 100)  # Razorpay expects paise
    order_data = {
        'amount': amount_paise,
        'currency': 'INR',
        'receipt': booking.display_id,
        'notes': {
            'booking_id': booking.display_id,
            'customer': booking.customer.username,
        }
    }
    rz_order = client.order.create(data=order_data)
    return JsonResponse({
        'order_id': rz_order['id'],
        'amount': amount_paise,
        'currency': 'INR',
        'key': settings.RAZORPAY_KEY_ID,
        'booking_display_id': booking.display_id,
        'customer_name': booking.customer.get_full_name() or booking.customer.username,
        'customer_email': booking.customer.email,
        'customer_phone': booking.customer.phone_number or '',
    })


@customer_required
@require_POST
def verify_razorpay_payment(request, booking_id):
    """Verify Razorpay payment signature and mark booking as paid."""
    booking = get_object_or_404(Booking, display_id=booking_id, customer=request.user)
    try:
        data = json.loads(request.body)
        rz_order_id = data['razorpay_order_id']
        rz_payment_id = data['razorpay_payment_id']
        rz_signature = data['razorpay_signature']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Invalid payload'}, status=400)

    # Verify signature
    msg = f'{rz_order_id}|{rz_payment_id}'.encode()
    secret = settings.RAZORPAY_KEY_SECRET.encode()
    expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()  # type: ignore[attr-defined]
    if not hmac.compare_digest(expected, rz_signature):
        logger.warning(f'Razorpay signature mismatch for booking {booking_id}')
        return JsonResponse({'success': False, 'error': 'Signature verification failed'}, status=400)

    booking.payment_status = Booking.PAYMENT_PAID
    booking.save(update_fields=['payment_status'])
    logger.info(f'Payment verified for booking {booking.display_id} — {rz_payment_id}')
    return JsonResponse({'success': True, 'redirect': f'/bookings/{booking.display_id}/'})
