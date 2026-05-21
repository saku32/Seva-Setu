from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Booking, BookingStatusLog, BookingPhoto, Review, Complaint, VendorETA
import csv
from django.http import HttpResponse


def export_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
    writer = csv.writer(response)
    writer.writerow(['Booking ID', 'Customer', 'Vendor', 'Problem', 'Area', 'Status',
                     'Date', 'Total Price', 'Payment Method', 'Created At'])
    for b in queryset:
        writer.writerow([
            b.display_id, b.customer.username,
            b.vendor.username if b.vendor else '',
            b.problem.title_en, str(b.area),
            b.status, b.preferred_date, b.total_price,
            b.payment_method, b.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    return response
export_as_csv.short_description = _('Export selected as CSV')


class BookingStatusLogInline(admin.TabularInline):
    model = BookingStatusLog
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'notes', 'timestamp')
    can_delete = False


class BookingPhotoInline(admin.TabularInline):
    model = BookingPhoto
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('display_id', 'customer', 'vendor', 'problem', 'area',
                    'status', 'preferred_date', 'total_price', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'payment_method', 'preferred_date')
    search_fields = ('display_id', 'customer__username', 'vendor__username', 'problem__title_en')
    readonly_fields = ('booking_id', 'display_id', 'created_at', 'updated_at')
    inlines = [BookingStatusLogInline, BookingPhotoInline]
    actions = [export_as_csv, 'assign_vendor', 'close_booking']

    def assign_vendor(self, request, queryset):
        # Admin can use this to manually trigger vendor assignment
        self.message_user(request, _('Please assign vendors individually.'))
    assign_vendor.short_description = _('Assign vendor')

    def close_booking(self, request, queryset):
        updated = queryset.filter(
            status=Booking.STATUS_INVOICE_GENERATED
        ).update(status=Booking.STATUS_CLOSED)
        self.message_user(request, f'{updated} bookings closed.')
    close_booking.short_description = _('Close selected bookings')

    def save_model(self, request, obj, form, change):
        if change and 'vendor' in form.changed_data and obj.vendor:
            if obj.status == Booking.STATUS_REQUESTED:
                old_status = Booking.STATUS_REQUESTED
                obj.status = Booking.STATUS_VENDOR_ASSIGNED
                BookingStatusLog.objects.create(
                    booking=obj, from_status=old_status,
                    to_status=Booking.STATUS_VENDOR_ASSIGNED,
                    changed_by=request.user, notes='Vendor assigned by admin'
                )
        super().save_model(request, obj, form, change)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('booking', 'raised_by', 'complaint_type', 'status', 'guarantee_claim', 'created_at')
    list_filter = ('status', 'complaint_type', 'guarantee_claim')
    search_fields = ('booking__display_id', 'raised_by__username')
    actions = ['resolve_complaints']

    def resolve_complaints(self, request, queryset):
        queryset.update(status=Complaint.STATUS_RESOLVED, resolved_at=timezone.now())
        self.message_user(request, _('Complaints marked as resolved.'))
    resolve_complaints.short_description = _('Mark as resolved')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'customer', 'vendor', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('booking__display_id', 'customer__username', 'vendor__username')
