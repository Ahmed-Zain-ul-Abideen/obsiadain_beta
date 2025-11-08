import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.files import File
from xhtml2pdf import pisa
from io import BytesIO
from  webapp.models import Invoice
import  os
from   django.conf   import   settings


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths for xhtml2pdf (Windows-safe).
    """
    import os
    from django.conf import settings

    # Normalize slashes
    uri = uri.replace('\\', '/')

    # Ensure trailing slashes for matching
    static_url = settings.STATIC_URL
    media_url = settings.MEDIA_URL

    # Resolve base directories
    static_root = settings.STATIC_ROOT or os.path.join(settings.BASE_DIR, 'static')
    media_root = settings.MEDIA_ROOT or os.path.join(settings.BASE_DIR, 'media')

    # Check if it's a STATIC file
    if uri.startswith(static_url):
        path = os.path.join(static_root, uri[len(static_url):])
    # Check if it's a MEDIA file
    elif uri.startswith(media_url):
        path = os.path.join(media_root, uri[len(media_url):])
    # Handle file:// URIs
    elif uri.startswith('file://'):
        path = uri.replace('file://', '')
    else:
        return uri  # Return unchanged for absolute or external URLs

    # Normalize backslashes for Windows
    path = os.path.normpath(path)

    # 🔹 If STATIC_ROOT doesn’t physically exist (common in dev), fallback to BASE_DIR/static
    if not os.path.isfile(path):
        fallback_path = os.path.join(settings.BASE_DIR, 'static', uri[len(static_url):])
        fallback_path = os.path.normpath(fallback_path)
        if os.path.isfile(fallback_path):
            return fallback_path
        raise Exception(f"File not found: {path}")

    return path





def generate_invoice_html(request, invoice_id):

    # Permission checks
    if not request.user.is_authenticated:
        return redirect('login')
    elif not request.user.is_superuser:
        return render(request, 'Denied/permission_denied.html')

    # Fetch invoice
    invoice = get_object_or_404(Invoice, id=invoice_id) 

    # Render HTML template
    return     render(request,'Invoices/invoice_template_v.html', {'invoice': invoice})

def generate_invoice_pdf(request, invoice_id):

    # Permission checks
    if not request.user.is_authenticated:
        return redirect('login')
    elif not request.user.is_superuser:
        return render(request, 'Denied/permission_denied.html')

    # Fetch invoice
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # logo_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'images', 'obsidian_logo.png')

    # Render HTML template
    html_content = render_to_string('Invoices/invoice_template_vv.html', {'invoice': invoice})

    # Create a BytesIO buffer for PDF output
    pdf_buffer = BytesIO()

    # Generate PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(
        html_content, dest=pdf_buffer, encoding='utf-8',link_callback=link_callback,
    )

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    pdf_buffer.seek(0)
    file_name = f"{invoice.invoice_no}.pdf"

    # Save the generated PDF to your Invoice model
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
        tmp.write(pdf_buffer.getvalue())
        tmp.seek(0)
        invoice.pdf_file.save(file_name, File(tmp), save=True)

    # Return inline PDF response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{file_name}"'
    return response
