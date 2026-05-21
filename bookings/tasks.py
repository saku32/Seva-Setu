from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger('sevasetu')


@shared_task
def send_booking_confirmation(booking_id):
    from .models import Booking
    try:
        booking = Booking.objects.select_related('customer', 'problem').get(display_id=booking_id)
        # In production: send SMS/email
        logger.info(f'Booking confirmation sent for {booking_id}')
    except Booking.DoesNotExist:
        logger.error(f'Booking not found: {booking_id}')


@shared_task
def generate_invoice_task(booking_id):
    from .models import Booking
    from invoices.utils import generate_invoice
    try:
        booking = Booking.objects.get(display_id=booking_id)
        generate_invoice(booking)
        logger.info(f'Invoice generated for {booking_id}')
    except Booking.DoesNotExist:
        logger.error(f'Booking not found: {booking_id}')


@shared_task
def send_booking_reminder():
    from .models import Booking
    from datetime import date, timedelta
    tomorrow = date.today() + timedelta(days=1)
    bookings = Booking.objects.filter(
        preferred_date=tomorrow,
        status__in=[Booking.STATUS_VENDOR_ACCEPTED, Booking.STATUS_VENDOR_ASSIGNED]
    ).select_related('customer', 'vendor')
    for booking in bookings:
        logger.info(f'Reminder: Booking {booking.display_id} scheduled for tomorrow')
