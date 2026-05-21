import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def generate_booking_id():
    return 'SVS-' + str(uuid.uuid4()).upper()[:6]


class Booking(models.Model):
    STATUS_REQUESTED = 'REQUESTED'
    STATUS_VENDOR_ASSIGNED = 'VENDOR_ASSIGNED'
    STATUS_VENDOR_ACCEPTED = 'VENDOR_ACCEPTED'
    STATUS_VENDOR_EN_ROUTE = 'VENDOR_EN_ROUTE'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_WORK_COMPLETED = 'WORK_COMPLETED'
    STATUS_CUSTOMER_CONFIRMED = 'CUSTOMER_CONFIRMED'
    STATUS_INVOICE_GENERATED = 'INVOICE_GENERATED'
    STATUS_CLOSED = 'CLOSED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_DISPUTED = 'DISPUTED'

    STATUS_CHOICES = [
        (STATUS_REQUESTED, _('Requested')),
        (STATUS_VENDOR_ASSIGNED, _('Vendor Assigned')),
        (STATUS_VENDOR_ACCEPTED, _('Vendor Accepted')),
        (STATUS_VENDOR_EN_ROUTE, _('Vendor En Route')),
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_WORK_COMPLETED, _('Work Completed')),
        (STATUS_CUSTOMER_CONFIRMED, _('Customer Confirmed')),
        (STATUS_INVOICE_GENERATED, _('Invoice Generated')),
        (STATUS_CLOSED, _('Closed')),
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_DISPUTED, _('Disputed')),
    ]

    SLOT_MORNING = 'morning'
    SLOT_AFTERNOON = 'afternoon'
    SLOT_EVENING = 'evening'
    SLOT_CHOICES = [
        (SLOT_MORNING, _('Morning (8AM - 12PM)')),
        (SLOT_AFTERNOON, _('Afternoon (12PM - 4PM)')),
        (SLOT_EVENING, _('Evening (4PM - 8PM)')),
    ]

    PAYMENT_PENDING = 'pending'
    PAYMENT_PAID = 'paid'
    PAYMENT_REFUNDED = 'refunded'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, _('Pending')),
        (PAYMENT_PAID, _('Paid')),
        (PAYMENT_REFUNDED, _('Refunded')),
    ]

    PAYMENT_COD = 'cod'
    PAYMENT_ONLINE = 'online'
    PAYMENT_WALLET = 'wallet'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_COD, _('Cash on Delivery')),
        (PAYMENT_ONLINE, _('Online Payment')),
        (PAYMENT_WALLET, _('Wallet')),
    ]

    booking_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_id = models.CharField(max_length=15, unique=True, default=generate_booking_id, editable=False)
    customer = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE,
        related_name='customer_bookings', verbose_name=_('Customer')
    )
    vendor = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='vendor_bookings', verbose_name=_('Vendor')
    )
    problem = models.ForeignKey(
        'services.ServiceProblem', on_delete=models.PROTECT,
        verbose_name=_('Service Problem')
    )
    area = models.ForeignKey(
        'locations.Area', on_delete=models.PROTECT,
        verbose_name=_('Area')
    )
    address_line = models.TextField(verbose_name=_('Address'))
    landmark = models.CharField(max_length=200, blank=True, verbose_name=_('Landmark'))
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES,
        default=STATUS_REQUESTED, verbose_name=_('Status')
    )
    preferred_date = models.DateField(verbose_name=_('Preferred Date'))
    preferred_time_slot = models.CharField(
        max_length=15, choices=SLOT_CHOICES,
        default=SLOT_MORNING, verbose_name=_('Preferred Time Slot')
    )
    description = models.TextField(verbose_name=_('Problem Description'))
    voice_transcript = models.TextField(blank=True, verbose_name=_('Voice Transcript'))
    base_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Base Price'))
    spare_parts_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('Spare Parts Cost'))
    total_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_('Total Price'))
    discount_applied = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name=_('Discount'))
    payment_status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING, verbose_name=_('Payment Status')
    )
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_COD, verbose_name=_('Payment Method')
    )
    same_professional_requested = models.BooleanField(default=False, verbose_name=_('Same Professional Requested'))
    assigned_previous_vendor = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='preferred_by_bookings',
        verbose_name=_('Preferred Previous Vendor')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.display_id} - {self.customer.username} - {self.problem.title_en}'

    def get_status_color(self):
        colors = {
            self.STATUS_REQUESTED: 'yellow',
            self.STATUS_VENDOR_ASSIGNED: 'blue',
            self.STATUS_VENDOR_ACCEPTED: 'indigo',
            self.STATUS_VENDOR_EN_ROUTE: 'purple',
            self.STATUS_IN_PROGRESS: 'orange',
            self.STATUS_WORK_COMPLETED: 'teal',
            self.STATUS_CUSTOMER_CONFIRMED: 'green',
            self.STATUS_INVOICE_GENERATED: 'green',
            self.STATUS_CLOSED: 'gray',
            self.STATUS_CANCELLED: 'red',
            self.STATUS_DISPUTED: 'red',
        }
        return colors.get(self.status, 'gray')

    @property
    def can_be_reviewed(self):
        return self.status in [self.STATUS_CLOSED, self.STATUS_CUSTOMER_CONFIRMED] and not hasattr(self, '_review_cache')

    @property
    def is_active(self):
        return self.status not in [self.STATUS_CLOSED, self.STATUS_CANCELLED]

    @property
    def guarantee_expires_at(self):
        if self.status == self.STATUS_CLOSED:
            from datetime import timedelta
            return self.updated_at + timedelta(days=7)
        return None


class BookingStatusLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=30)
    to_status = models.CharField(max_length=30)
    changed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.booking.display_id}: {self.from_status} → {self.to_status}'


class BookingPhoto(models.Model):
    PHOTO_BEFORE = 'BEFORE'
    PHOTO_AFTER = 'AFTER'
    PHOTO_TYPE_CHOICES = [
        (PHOTO_BEFORE, _('Before')),
        (PHOTO_AFTER, _('After')),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='booking_photos/%Y/%m/')
    photo_type = models.CharField(max_length=6, choices=PHOTO_TYPE_CHOICES)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Booking Photo')
        verbose_name_plural = _('Booking Photos')

    def __str__(self):
        return f'{self.booking.display_id} - {self.photo_type}'


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='given_reviews')
    vendor = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(verbose_name=_('Review'))
    vendor_response = models.TextField(blank=True, verbose_name=_('Vendor Response'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking.display_id} - {self.rating}★'


class Complaint(models.Model):
    TYPE_QUALITY = 'quality'
    TYPE_DELAY = 'delay'
    TYPE_BEHAVIOR = 'behavior'
    TYPE_PRICING = 'pricing'
    TYPE_OTHER = 'other'
    TYPE_CHOICES = [
        (TYPE_QUALITY, _('Quality Issue')),
        (TYPE_DELAY, _('Delay')),
        (TYPE_BEHAVIOR, _('Unprofessional Behavior')),
        (TYPE_PRICING, _('Pricing Dispute')),
        (TYPE_OTHER, _('Other')),
    ]
    STATUS_OPEN = 'open'
    STATUS_INVESTIGATING = 'investigating'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, _('Open')),
        (STATUS_INVESTIGATING, _('Investigating')),
        (STATUS_RESOLVED, _('Resolved')),
        (STATUS_CLOSED, _('Closed')),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='complaints')
    raised_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    complaint_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_OPEN)
    resolution_notes = models.TextField(blank=True)
    guarantee_claim = models.BooleanField(default=False, verbose_name=_('7-Day Guarantee Claim'))
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Complaint')
        verbose_name_plural = _('Complaints')
        ordering = ['-created_at']

    def __str__(self):
        return f'Complaint: {self.booking.display_id} - {self.complaint_type}'


class VendorETA(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='vendor_eta')
    estimated_arrival = models.DateTimeField()
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'ETA for {self.booking.display_id}'
