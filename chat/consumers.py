import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.room_group_name = f'chat_{self.booking_id}'
        user = self.scope['user']

        if not user.is_authenticated:
            await self.close()
            return

        # Verify user has access to this chat room
        has_access = await self.check_access(user, self.booking_id)
        if not has_access:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        if not message:
            return

        user = self.scope['user']
        saved = await self.save_message(user, self.booking_id, message)
        if saved:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': user.id,
                    'sender_name': user.get_full_name() or user.username,
                    'timestamp': timezone.now().isoformat(),
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def check_access(self, user, booking_id):
        from bookings.models import Booking
        try:
            booking = Booking.objects.get(display_id=booking_id)
            return user == booking.customer or user == booking.vendor or user.is_admin_user
        except Booking.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, user, booking_id, message):
        from .models import ChatRoom, ChatMessage
        try:
            room = ChatRoom.objects.get(booking__display_id=booking_id)
            ChatMessage.objects.create(room=room, sender=user, message=message)
            return True
        except ChatRoom.DoesNotExist:
            return False
