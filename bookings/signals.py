from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, BookingStatusLog
import logging

logger = logging.getLogger('sevasetu')


@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    if created:
        from .tasks import send_booking_confirmation
        try:
            send_booking_confirmation.delay(instance.display_id)
        except Exception as e:
            logger.warning(f'Could not send booking confirmation: {e}')

    # Auto-create chat room when vendor is assigned
    if not created and instance.vendor and instance.status == Booking.STATUS_VENDOR_ASSIGNED:
        from chat.models import ChatRoom
        ChatRoom.objects.get_or_create(
            booking=instance,
            defaults={
                'customer': instance.customer,
                'vendor': instance.vendor,
            }
        )

    # Update vendor stats when booking is closed
    if not created and instance.status == Booking.STATUS_CLOSED:
        if instance.vendor:
            try:
                vp = instance.vendor.vendor_profile
                vp.total_jobs_completed += 1
                # Credit vendor wallet (80% of total price)
                earning = instance.total_price * 0.8
                vp.wallet_balance += earning
                vp.save(update_fields=['total_jobs_completed', 'wallet_balance'])
                logger.info(f'Vendor {instance.vendor.username} credited ₹{earning}')
            except Exception as e:
                logger.error(f'Error updating vendor stats: {e}')
