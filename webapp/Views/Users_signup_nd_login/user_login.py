from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from   webapp.Views.Roles_related.create_roles   import  create_roles
from   webapp.models   import  *

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
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if    request.user.is_superuser:
                    return redirect('view_fbr_oficials')
                else: 
                    return redirect('view_mills')
            else:
                messages.error(request, "Invalid username or password")

     
    return render(request, 'Auths/login.html')




def logout_view(request):
    logout(request)
    return redirect('login') 

def index(request):
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