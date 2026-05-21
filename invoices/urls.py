from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('<str:booking_id>/', views.view_invoice, name='view'),
    path('<str:booking_id>/download/', views.download_invoice, name='download'),
]
