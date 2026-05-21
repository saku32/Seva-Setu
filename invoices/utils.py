import os
import logging
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger('sevasetu')


def generate_invoice(booking):
    try:
        from weasyprint import HTML, CSS
        html_content = render_to_string('invoices/invoice_template.html', {
            'booking': booking,
            'gst_rate': 18,
            'gst_amount': booking.total_price * 18 / 118,
        })
        
        invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
        os.makedirs(invoice_dir, exist_ok=True)
        invoice_path = os.path.join(invoice_dir, f'INV-{booking.display_id}.pdf')
        
        HTML(string=html_content).write_pdf(invoice_path)
        logger.info(f'Invoice generated: {invoice_path}')
        return invoice_path
    except ImportError:
        logger.warning('WeasyPrint not installed. Skipping PDF generation.')
        return None
    except Exception as e:
        logger.error(f'Invoice generation error: {e}')
        return None
