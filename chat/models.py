from django.db import models
from django.utils.translation import gettext_lazy as _


class ChatRoom(models.Model):
    booking = models.OneToOneField(
        'bookings.Booking', on_delete=models.CASCADE, related_name='chat_room')
    customer = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='customer_chats')
    vendor = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='vendor_chats')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Chat Room')
        verbose_name_plural = _('Chat Rooms')

    def __str__(self):
        return f'Chat: {self.booking.display_id}'


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Chat Message')
        verbose_name_plural = _('Chat Messages')
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.sender.username}: {self.message[:50]}'
