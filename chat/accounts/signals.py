from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, CustomerProfile, VendorProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.ROLE_CUSTOMER:
            CustomerProfile.objects.get_or_create(user=instance)
