from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.core.paginator import Paginator
from datetime import date, timedelta


@login_required
def home(request):
    if request.user.is_vendor:
        return vendor_dashboard(request)
    elif request.user.is_admin_user:
        return admin_dashboard(request)
    else:
        return user_dashboard(request)


@login_required
def user_dashboard(request):
    from bookings.models import Booking
    from subscriptions.models import UserSubscription
    from notifications.models import Notification

    active_bookings = Booking.objects.filter(
        customer=request.user,
        status__in=[
            Booking.STATUS_REQUESTED, Booking.STATUS_VENDOR_ASSIGNED,
            Booking.STATUS_VENDOR_ACCEPTED, Booking.STATUS_VENDOR_EN_ROUTE,
            Booking.STATUS_IN_PROGRESS, Booking.STATUS_WORK_COMPLETED,
        ]
    ).select_related('vendor', 'problem', 'area').order_by('-created_at')[:5]

    recent_bookings = Booking.objects.filter(
        customer=request.user
    ).select_related('vendor', 'problem').order_by('-created_at')[:10]

    active_subs = UserSubscription.objects.filter(
        customer=request.user, is_active=True
    ).select_related('plan')

    notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).order_by('-created_at')[:5]

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    # Smart reminders (simple logic)
    reminders = []
    from services.models import ServiceCategory
    last_ac = Booking.objects.filter(
        customer=request.user,
        problem__category__name_en='AC & Appliance Repair',
        status=Booking.STATUS_CLOSED
    ).order_by('-created_at').first()
    if last_ac and (date.today() - last_ac.preferred_date).days > 90:
        reminders.append({
            'message': _('Your AC was last serviced over 3 months ago. Book maintenance?'),
            'slug': 'ac-appliance-repair'
        })

    from services.models import ServiceCategory as SC
    categories = SC.objects.filter(is_active=True)[:6]

    return render(request, 'dashboard/user_dashboard.html', {
        'active_bookings': active_bookings,
        'recent_bookings': recent_bookings,
        'active_subs': active_subs,
        'notifications': notifications,
        'unread_count': unread_count,
        'reminders': reminders,
        'categories': categories,
    })


@login_required
def vendor_dashboard(request):
    from bookings.models import Booking

    today = date.today()
    today_bookings = Booking.objects.filter(
        vendor=request.user, preferred_date=today
    ).select_related('customer', 'problem', 'area').order_by('preferred_time_slot')

    pending_bookings = Booking.objects.filter(
        vendor=request.user,
        status__in=[Booking.STATUS_VENDOR_ASSIGNED, Booking.STATUS_VENDOR_ACCEPTED]
    ).select_related('customer', 'problem', 'area').order_by('preferred_date')[:5]

    active_jobs = Booking.objects.filter(
        vendor=request.user,
        status__in=[Booking.STATUS_VENDOR_EN_ROUTE, Booking.STATUS_IN_PROGRESS]
    ).select_related('customer', 'problem')

    week_start = today - timedelta(days=today.weekday())
    week_earnings = Booking.objects.filter(
        vendor=request.user,
        status=Booking.STATUS_CLOSED,
        updated_at__date__gte=week_start
    ).aggregate(total=Sum('total_price'))['total'] or 0

    month_start = today.replace(day=1)
    month_earnings = Booking.objects.filter(
        vendor=request.user,
        status=Booking.STATUS_CLOSED,
        updated_at__date__gte=month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0

    total_completed = Booking.objects.filter(
        vendor=request.user, status=Booking.STATUS_CLOSED
    ).count()

    avg_rating = Booking.objects.filter(
        vendor=request.user
    ).aggregate(avg=Avg('review__rating'))['avg'] or 0

    try:
        vendor_profile = request.user.vendor_profile
    except Exception:
        vendor_profile = None

    from notifications.models import Notification
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    return render(request, 'dashboard/vendor_dashboard.html', {
        'today_bookings': today_bookings,
        'pending_bookings': pending_bookings,
        'active_jobs': active_jobs,
        'week_earnings': week_earnings * 0.8,  # 80% commission
        'month_earnings': month_earnings * 0.8,
        'total_completed': total_completed,
        'avg_rating': round(avg_rating, 1),
        'vendor_profile': vendor_profile,
        'notifications': notifications,
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        return redirect('dashboard:home')

    from bookings.models import Booking
    from accounts.models import User, VendorProfile
    today = date.today()

    total_users = User.objects.filter(role='customer').count()
    total_vendors = User.objects.filter(role='vendor').count()
    pending_vendors = VendorProfile.objects.filter(is_verified=False).count()
    today_bookings = Booking.objects.filter(created_at__date=today).count()
    today_revenue = Booking.objects.filter(
        created_at__date=today, payment_status='paid'
    ).aggregate(total=Sum('total_price'))['total'] or 0
    open_complaints = Booking.objects.filter(
        complaints__status__in=['open', 'investigating']
    ).distinct().count()

    recent_bookings = Booking.objects.all().select_related(
        'customer', 'vendor', 'problem'
    ).order_by('-created_at')[:10]

    pending_vendor_profiles = VendorProfile.objects.filter(is_verified=False).select_related('user')[:10]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'pending_vendors': pending_vendors,
        'today_bookings': today_bookings,
        'today_revenue': today_revenue,
        'open_complaints': open_complaints,
        'recent_bookings': recent_bookings,
        'pending_vendor_profiles': pending_vendor_profiles,
    })


@login_required
def notifications_list(request):
    from notifications.models import Notification
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    paginator = Paginator(notifs, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'dashboard/notifications.html', {'page_obj': page_obj})


@login_required
def notifications_api(request):
    from notifications.models import Notification
    from django.http import JsonResponse
    notifs = list(Notification.objects.filter(user=request.user, is_read=False)
                  .values('id', 'title', 'message', 'link', 'created_at')
                  .order_by('-created_at')[:10])
    return JsonResponse({'notifications': notifs, 'count': len(notifs)})
