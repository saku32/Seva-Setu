from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<str:booking_id>/', views.chat_room, name='room'),
]
