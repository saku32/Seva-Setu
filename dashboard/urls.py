from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('user/', views.user_dashboard, name='user'),
    path('vendor/', views.vendor_dashboard, name='vendor'),
    path('admin/', views.admin_dashboard, name='admin'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
]
