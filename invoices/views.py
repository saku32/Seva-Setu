import os
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from bookings.models import Booking


@login_required
def download_invoice(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id)
    if request.user != booking.customer and request.user != booking.vendor and not request.user.is_admin_user:
        raise Http404

    invoice_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'INV-{booking_id}.pdf')
    
    if not os.path.exists(invoice_path):
        from .utils import generate_invoice
        invoice_path = generate_invoice(booking)
        if not invoice_path or not os.path.exists(invoice_path):
            from django.shortcuts import render
            return render(request, 'invoices/invoice_view.html', {'booking': booking})

    return FileResponse(
        open(invoice_path, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=f'SevaSetu-INV-{booking_id}.pdf'
    )


@login_required
def view_invoice(request, booking_id):
    booking = get_object_or_404(Booking, display_id=booking_id)
    if request.user != booking.customer and request.user != booking.vendor and not request.user.is_admin_user:
        raise Http404
    gst_amount = booking.total_price * 18 / 118
    return __import__('django.shortcuts', fromlist=['render']).render(
        request, 'invoices/invoice_view.html',
        {'booking': booking, 'gst_amount': gst_amount, 'gst_rate': 18}
    )
