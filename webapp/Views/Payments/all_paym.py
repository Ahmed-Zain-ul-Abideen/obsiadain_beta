from django.shortcuts import render, redirect 
from django.contrib.auth.models import User, Group 
from django.contrib import messages
from  webapp.models   import   *
from   webapp.Views.utils   import  send_html_email

def   view_inspection_of_payment(request, payment_id=None): 

    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   request.user.is_superuser:
        try:
            payment = PaymentsRecords.objects.get(id=payment_id)
        except  PaymentsRecords.DoesNotExist:
            payment = None
        
        return   render(request,'Payments/view_inspection_of_payment.html',{"payment":payment})
    elif      request.user.groups.filter(name="Mill_owners").exists():
        try:
            payment = PaymentsRecords.objects.get(id=payment_id)
        except  PaymentsRecords.DoesNotExist:
            payment = None
        
        return   render(request,'Payments/view_inspection_of_payment.html',{"payment":payment})
    else:
        return   render(request,'Denied/permission_denied.html')
    
        
def  analyze_invoice_payment(request, invoice_id=None): 

    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not      request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')
    else:   

        try:
            payment = InvoicesPaymentsRecords.objects.get(invoice_id=invoice_id)
        except  PaymentsRecords.DoesNotExist:
            payment = None

        if request.method == 'POST' and payment:
 
            status_title = request.POST.get("status_title", "").strip() 

            # Validate required fields
            fields = { 
                "Status": status_title
            }

            missing_fields = [field for field, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + (" is missing" if len(missing_fields)==1 else " are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))

             
            
            payment.status_title = status_title
            payment.is_approved = True 

            payment.save()


            
            try:

                unit_address = payment.invoice.mill_unit_invoices.address

                print("unit_address  ",unit_address)  

                context = {
                    "invoice_no":   payment.invoice.invoice_no,
                    "remittance_amount": payment.invoice.remittance_amount,
                    "site_location": payment.invoice.site_location,
                    "status":status_title,
                    "unit_address":unit_address,

                }

                email  =  payment.invoice.mill_unit_invoices.mill.owner.email

                print("mill  owner  email  ",email)

                # Send reset email
                send_html_email(
                    subject="Invoice  Payment  Anaylzed",
                    to_email=email,
                    context=context,
                    template_path="Emails/payment_inspection_email.html"
                )

                print("Success  inspection   update  email  ")

            except   Exception   as   e:
                print("Failure  inspection   update  email  ",e)
    
            return   redirect("payment_records")
            # return redirect('inspect_payment', payment_id=payment.id)

        return render(request, 'Payments/inspect_payment.html', {
            "payment": payment
        })
       

def  inspect_payment(request, payment_id=None): 

    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not      request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')
    else:   

        try:
            payment = PaymentsRecords.objects.get(id=payment_id)
        except  PaymentsRecords.DoesNotExist:
            payment = None

        if request.method == 'POST' and payment:

            # total_amount = request.POST.get("total_amount", "").strip()
            # paid_amount = request.POST.get("paid_amount", "").strip()
            # unpaid_amount = request.POST.get("unpaid_amount", "").strip()
            status_title = request.POST.get("status_title", "").strip()
            # is_approved = request.POST.get("is_approved", "")

            # Validate required fields
            fields = {
                # "Total Amount": total_amount,
                # "Paid Amount": paid_amount,
                # "Unpaid Amount": unpaid_amount,
                "Status": status_title
            }

            missing_fields = [field for field, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + (" is missing" if len(missing_fields)==1 else " are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))

            # ✅ Convert fields safely
            # try:
            #     total_amount = float(total_amount)
            #     paid_amount = float(paid_amount)
            #     unpaid_amount = float(unpaid_amount)
            # except ValueError:
            #     messages.error(request, "Amounts must be valid numbers")
            #     return redirect(request.META.get('HTTP_REFERER'))

            # ✅ Update fields
            # payment.total_amount = total_amount
            # payment.paid_amount = paid_amount
            # payment.unpaid_amount = unpaid_amount
            payment.status_title = status_title
            payment.is_approved = True 

            payment.save()


            
            try:

                unit_address = payment.unit.address

                print("unit_address  ",unit_address)  

                context = {
                    "total_amount":  total_amount,
                    "paid_amount": paid_amount,
                    "unpaid_amount": unpaid_amount,
                    "status":status_title,
                    "is_approved":is_approved,
                    "unit_address":unit_address,

                }

                email  =  payment.mill.owner.email

                print("mill  owner  email  ",email)

                # Send reset email
                send_html_email(
                    subject="Payment  Inspection Update",
                    to_email=email,
                    context=context,
                    template_path="Emails/payment_inspection_email.html"
                )

                print("Success  inspection   update  email  ")

            except   Exception   as   e:
                print("Failure  inspection   update  email  ",e)
    
            return   redirect("payment_records")
            # return redirect('inspect_payment', payment_id=payment.id)

        return render(request, 'Payments/inspect_payment.html', {
            "payment": payment
        })

def payment_records_list(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    elif     request.user.groups.filter(name="Mill_owners").exists():
        payments  =  False
        if    PaymentsRecords.objects.filter(mill__owner__id=request.user.pk).exists():
            payments = PaymentsRecords.objects.filter(mill__owner__id=request.user.pk).order_by('-id')
        return render(request, "Payments/payment_records_list.html", {"payments": payments})  
    elif  request.user.is_superuser:
        payments = PaymentsRecords.objects.all().order_by('-id')
        return render(request, "Payments/payment_records_list.html", {"payments": payments})  
    else:
        return   render(request,'Denied/permission_denied.html')
    
    
from django.db.models import Q
from django.http import JsonResponse
def  search_payments_list(request): 
    query = request.GET.get('query') or None   
    searched_payments_exist = PaymentsRecords.objects.filter(name__icontains=query).exists()
    if searched_payments_exist:    
        searched_payments = list(PaymentsRecords.objects.filter(name__icontains=query).values())          
        context = {'ven':  searched_payments}  
        return JsonResponse({"success": True,"response":context}) 
    else:  
        return JsonResponse({"success": False})
    


def  add_payment_record_to_invoice(request,invoice_id):
    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not   request.user.groups.filter(name="Mill_owners").exists():
        return   render(request,'Denied/permission_denied.html')
    else:
        pass
    
    if request.method == "POST":
        attachment = request.FILES.get("attachment")
        if   not   attachment:
            messages.warning(request,  "Attachment   is   missing")
            return redirect(request.META.get('HTTP_REFERER'))
        

        allowed_types = ["application/pdf", "image/jpeg", "image/png"]

        if attachment and attachment.content_type not in allowed_types:
            messages.error(request, "Invalid file! Only PDF, JPG, JPEG, PNG are allowed.")
            return redirect(request.META.get('HTTP_REFERER'))
        

        InvoicesPaymentsRecords.objects.create(
            invoice_id  = invoice_id,
            attachment=attachment

        )

         

        messages.success(request, "Payment record  against  invoice  added successfully!")
        return redirect("view_mills")

    return   render(request,'Payments/add_payment_record.html')


def  add_payment_record(request,mill_id,unit_id):
    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not   request.user.groups.filter(name="Mill_owners").exists():
        return   render(request,'Denied/permission_denied.html')
    else:
        pass
    
    if request.method == "POST":
        attachment = request.FILES.get("attachment")
        if   not   attachment:
            messages.warning(request,  "Attachment   is   missing")
            return redirect(request.META.get('HTTP_REFERER'))
        

        allowed_types = ["application/pdf", "image/jpeg", "image/png"]

        if attachment and attachment.content_type not in allowed_types:
            messages.error(request, "Invalid file! Only PDF, JPG, JPEG, PNG are allowed.")
            return redirect(request.META.get('HTTP_REFERER'))

        PaymentsRecords.objects.create(
            mill_id=mill_id,
            unit_id=unit_id,
            # paid_to_account_id=1,
            # total_amount=1000,
            # paid_amount=1000,
            # unpaid_amount= 0,
            # status_title= "Full  Paid",
            attachment=attachment
        )

        messages.success(request, "Payment record added successfully!")
        return redirect("view_mills")

    return   render(request,'Payments/add_payment_record.html')

def   list_fbr_payment_accounts(request):
    
    if  not    request.user.is_authenticated:
        return redirect('login')

    if   request.user.is_superuser:
        pass
    elif    request.user.groups.filter(name="Mill_owners").exists(): 
        pass
    else:
        return   render(request,'Denied/permission_denied.html')
    
    payment_accs =  False
    if    Paymentaccounts.objects.exists():
        payment_accs  =  Paymentaccounts.objects.all().order_by('-id')

    print("payment_accs", payment_accs)
    
    return   render(request,'Payments/fbr_bank_details_list.html',{'payment_accs':payment_accs})


def  add_fbr_payment_account(request):

    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if   request.user.is_superuser:
        pass
    else:
        return   render(request,'Denied/permission_denied.html')

    if request.method == "POST":
        iban_number = request.POST.get("iban_number", "").strip()
        account_title = request.POST.get("account_title", "").strip()
        bank_name = request.POST.get("bank_name", "").strip() 
        fields = {
            "iban_number": iban_number,
            "account_title": account_title,
            "bank_name": bank_name
                
        }

        missing_fields = [field for field, value in fields.items() if not value]

        if missing_fields:
            msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
            messages.warning(request, msg)
            return redirect(request.META.get('HTTP_REFERER'))
 

        Paymentaccounts.objects.create(
            added_by_user_id  = request.user.pk,
            iban_number =  iban_number,
            account_title = account_title,
            bank_name = bank_name
        )

        messages.success(request, "FBR  payment  account  added  successfully")
        return redirect("view_mills")

    return render(request, "Payments/add_fbr_bank_details.html")