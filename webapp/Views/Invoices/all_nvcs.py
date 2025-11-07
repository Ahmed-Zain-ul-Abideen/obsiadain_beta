from django.shortcuts import render, redirect
from django.contrib import messages 
from   webapp.Views.Invoices.forms   import   InvoiceForm, InvoiceItemFormSet
from  webapp.models   import   *


def   Invoices_records_list(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    elif     request.user.groups.filter(name="Mill_owners").exists():
        invoices  =  False
        if Invoice.objects.filter(mill_unit_invoices__mill__owner_id=request.user.pk).exists():
            invoices = Invoice.objects.filter(mill_unit_invoices__mill__owner_id=request.user.pk).order_by('-id')
            for invoice in invoices:
                print("inv", invoice.id, invoice.customer_name)
        return render(request, "Payments/payment_records_list.html", {"invoices": invoices})
        # if    Invoice.objects.filter(mill_unit_invoices__mills_units__owner_id=request.user.pk).exists():
        #     invoices = Invoice.objects.filter(mill_unit_invoices__mills_units__owner_id=request.user.pk).order_by('-id')
        #     for  invoice   in   invoices:
        #         print("inv  ",invoice.id,"  ", invoice.customer_name)
        # return render(request, "Payments/payment_records_list.html", {"invoices": invoices})  
    # elif  request.user.is_superuser:
    #     payments = PaymentsRecords.objects.all().order_by('-id')
    #     return render(request, "Payments/payment_records_list.html", {"payments": payments})  
    else:
        return   render(request,'Denied/permission_denied.html')

def create_invoice(request,unit_id):

    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not  request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')
    else:
        pass

    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        
        sub = False
        sub2 = False
        if  form.is_valid():
            print("form   is   valid")
            sub =  True
        else:
            print("❌ InvoiceForm is invalid")
            print("Errors in InvoiceForm:")
            for field, errors in form.errors.items():
                print(f"  - {field}: {', '.join(errors)}")
            if form.non_field_errors():
                print("  Non-field errors:", form.non_field_errors())

        if  formset.is_valid():
            print("formset   is   valid")
            sub2 =  True
        else:
            print("❌ InvoiceItemFormSet is invalid")
            print("Formset management errors:", formset.non_form_errors())

            for i, form_item in enumerate(formset.forms):
                if not form_item.is_valid():
                    print(f"\nErrors in formset form #{i + 1}:")
                    for field, errors in form_item.errors.items():
                        print(f"  - {field}: {', '.join(errors)}")
                    if form_item.non_field_errors():
                        print("  Non-field errors:", form_item.non_field_errors())


        if  sub   and   sub2:
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.mill_unit_invoices_id = unit_id
            invoice.save()

            # Link each item to the invoice
            items = formset.save(commit=False)
            for i, item in enumerate(items, start=1):
                item.invoice = invoice
                item.serial_no = i
                item.save()

            # Update total amount
            total = sum([item.balance for item in invoice.invoice_items.all()])
            invoice.remittance_amount = total
            invoice.save()

            messages.success(request, "Invoice created successfully!")
            return redirect('generate_invoice_pdf', invoice_id=invoice.id)
        else:
            print("Both  form   is   invalid")
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    return render(request, 'Invoices/create_invoice_xv.html', {'form': form, 'formset': formset})


# def generate_invoice_pdf(request, invoice_id):

#     if  not    request.user.is_authenticated:
#         return redirect('login')
#     elif   not  request.user.is_superuser:
#         return   render(request,'Denied/permission_denied.html')
#     else:
#         pass 


#     invoice = get_object_or_404(Invoice, id=invoice_id)
#     html_content = render_to_string('Invoices/invoice_template.html', {'invoice': invoice})

#     with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
#         HTML(string=html_content).write_pdf(tmp.name)
#         tmp.seek(0)
#         file_name = f"{invoice.invoice_no}.pdf"

#         invoice.pdf_file.save(file_name, File(tmp), save=True)

#         response = HttpResponse(tmp.read(), content_type='application/pdf')
#         response['Content-Disposition'] = f'inline; filename="{file_name}"'
#         return response
