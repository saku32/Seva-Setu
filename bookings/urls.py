from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('new/', views.booking_new, name='new'),
    path('<str:booking_id>/', views.booking_detail, name='detail'),
    path('<str:booking_id>/status/', views.vendor_update_status, name='update_status'),
    path('<str:booking_id>/confirm/', views.customer_confirm, name='confirm'),
    path('<str:booking_id>/photos/', views.upload_photos, name='upload_photos'),
    path('<str:booking_id>/review/', views.leave_review, name='review'),
    path('<str:booking_id>/complaint/', views.raise_complaint, name='complaint'),
    path('<str:booking_id>/accept/', views.accept_booking, name='accept'),
    path('api/<str:booking_id>/status/', views.booking_status_api, name='status_api'),
    path('<str:booking_id>/payment/create/', views.create_razorpay_order, name='payment_create'),
    path('<str:booking_id>/payment/verify/', views.verify_razorpay_payment, name='payment_verify'),
]
