from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from bookings.models import Booking
from .models import ChatRoom, ChatMessage


@login_required
def chat_room(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id)
    if request.user != booking.customer and request.user != booking.vendor and not request.user.is_admin_user:
        from django.contrib import messages
        from django.utils.translation import gettext_lazy as _
        messages.error(request, _('Access denied.'))
        return __import__('django.shortcuts', fromlist=['redirect']).redirect('/')

    room, _ = ChatRoom.objects.get_or_create(
        booking=booking,
        defaults={'customer': booking.customer, 'vendor': booking.vendor}
    )
    messages_qs = room.messages.all().select_related('sender')
    # Mark messages as read
    messages_qs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    return render(request, 'chat/chat_room.html', {
        'booking': booking,
        'room': room,
        'messages': messages_qs,
    })
