from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from   django.conf    import  settings
from   webapp.models   import  *
from  webapp.Views.Invoices.thr_xhtmpd   import   test_generate_invoice_pdf
from django.http import JsonResponse
from  webapp.Views.utils   import   verify_email_smtp,send_html_email

def login_view(request):
    # If user already logged in → go to add mill
    if request.user.is_authenticated:
        if    request.user.is_superuser:
            return redirect('view_fbr_oficials')
        else: 
            return redirect('view_mills') 

    # Handle login POST
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip() 

        # Map form values → readable field names for user message
        fields = {
            "Username": username,
            "Password": password, 
        }

        # Detect empty fields
        missing_fields = [name for name, value in fields.items() if not value]

        if missing_fields:
            msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
            messages.warning(request, msg)
            #return redirect(request.META.get('HTTP_REFERER'))
        else: 


            try:
                user_obj = User.objects.get(username=username)
            except User.DoesNotExist:
                user_obj = None

            # Step 1: Check if username exists
            if user_obj is None:
                messages.error(request, "Invalid username or password.")
                # return redirect("login")  
            elif not user_obj.is_active:
                messages.error(request, "Your account is not activated. Please verify your signup email first.")
                # return redirect("login")
            else:

                # Step 3: Now authenticate since user is active
                user = authenticate(request, username=username, password=password)

                if user is not None:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('view_fbr_oficials')
                    else:
                        return redirect('view_mills')
                else:
                    messages.error(request, "Invalid password.")


            # user = authenticate(request, username=username, password=password)
            # print("user  nnot  none ",user)

            # if user is not None:
            #     # if   not   user.is_active:
            #     #     messages.error(request, "Verify  Signup  email  first!")
            #     # else:
            #     login(request, user)
            #     if    request.user.is_superuser:
            #         return redirect('view_fbr_oficials')
            #     else: 
            #         return redirect('view_mills')
            # else:
            #     messages.error(request, "Invalid username or password  or  Verify  Signup  first!")

     
    return render(request, 'Auths/login_vv.html')

def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error_type": "username"})

        if user.email.lower() != email.lower():
            return JsonResponse({"success": False, "error_type": "email"})

        # ✅ Send password reset link  
        

        try:
            # Generate password reset link
            token = default_token_generator.make_token(user)
            uid = user.pk

            reset_link = f"{settings.DOMAIN}{reverse('set_password', args=[uid, token])}"

            context = {
                "username": username,
                "reset_link": reset_link
            }

            # Send reset email
            send_html_email(
                subject="Reset Your Password",
                to_email=email,
                context=context,
                template_path="Emails/Forget_reset_password_email.html"
            )

            print("Success forget   password   reset   link  execution  ")

        except   Exception   as   e:
            print("Error   in  forget  password   reset   link  execution  ",e)

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


def logout_view(request):
    logout(request)
    return redirect('login') 

def index(request):
    settings = Master_Settings.objects.all().first()
    fbr_account = Paymentaccounts.objects.all().first()
    context ={'settings':settings,
              'fbr_account':fbr_account}
    return render(request, 'landing_page.html', context)


def  extra(request):
    #test_generate_invoice_pdf(8)
    User.objects.filter(pk=10).delete()
    # Invoice.objects.filter(pk=12).delete()
    #users =  User.objects.all()
    # for  user  in   users:
    #     print("user  ",user.username)
    settings = Master_Settings.objects.all().first()
    fbr_account = Paymentaccounts.objects.all().first()
    context ={'settings':settings,
              'fbr_account':fbr_account}
    return render(request, 'landing_page.html', context)



def  view_users_login_logout_activities_log(request):

    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not  request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')
    else:

        users_login_logout_activities_log =  False
        if    UsersLoginLogoutActivitiesLog.objects.exists():
            users_login_logout_activities_log  =  UsersLoginLogoutActivitiesLog.objects.all()

         
        context ={'users_login_logout_activities_log':users_login_logout_activities_log}

        return  render(request, 'Others/user_activity_log.html', context)