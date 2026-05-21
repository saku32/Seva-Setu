from django.contrib import admin
from .models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('booking', 'customer', 'vendor', 'is_active', 'created_at')
    list_filter = ('is_active',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read',)
