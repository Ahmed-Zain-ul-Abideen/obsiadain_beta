import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.files import File
from xhtml2pdf import pisa
from io import BytesIO
from  webapp.models import Invoice


def generate_invoice_pdf(request, invoice_id):

    # Permission checks
    if not request.user.is_authenticated:
        return redirect('login')
    elif not request.user.is_superuser:
        return render(request, 'Denied/permission_denied.html')

    # Fetch invoice
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Render HTML template
    html_content = render_to_string('Invoices/invoice_template.html', {'invoice': invoice})

    # Create a BytesIO buffer for PDF output
    pdf_buffer = BytesIO()

    # Generate PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(
        html_content, dest=pdf_buffer, encoding='utf-8'
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
