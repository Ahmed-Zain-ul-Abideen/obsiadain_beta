from django.contrib.auth.models import User, Group
from   django.contrib   import   messages
from   webapp.models  import   MillOwnersProfile
from   django.shortcuts   import   redirect,render
import  random
import   string
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes 
from   django.conf    import  settings
from  webapp.Views.utils   import   send_html_email
from django.utils import timezone

def generate_customerid():
    """Generate a unique alphanumeric NTN starting with 'MILL-'."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return  f"CUST-{suffix}"


def register_user(request):
    if   request.user.is_authenticated:
        return redirect('add_mill')
    
    if request.method == "POST":
        try:
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            email = request.POST.get("email", "").strip()
            designation = request.POST.get("designation", "").strip()
            company = request.POST.get("company_name", "").strip()
            name = request.POST.get("name", "").strip()

            # Map form values → readable field names for user message
            fields = {
                "Username": username,
                "Password": password,
                "Email": email,
                "designation": designation,
                "company":company,
                "name":name
            }

            # Detect empty fields
            missing_fields = [name for name, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))

            

            user = User.objects.create_user(username=username,email=email, password=password,first_name=name)
            role = "Mill_owners"
            # Assign user to selected group
            group = Group.objects.get(name=role)
            user.groups.add(group)

            user.save()

            customer_id  =  generate_customerid()  + '__' +  str(user.pk)

            MillOwnersProfile.objects.create(
                owner_p_id=user.pk,
                company=company,
                designation=designation,
                customer_id =  customer_id

            )

            messages.success(request, 'User  registered  successfully !')
            return redirect('login')
        except  Exception  as  e:

            print("exception  : ",e)
            messages.warning(request, 'User  registration  failed !')
            return redirect(request.META.get('HTTP_REFERER'))
        

    return render(request, 'Auths/register.html') 
    

        


def   verify_signup_email(request, uidb64, token):
    uid =  urlsafe_base64_decode(uidb64).decode()
    try:
        user = User.objects.get(pk=uid)
        print("user  exist")
    except User.DoesNotExist:
        print("user not  exist")
        messages.warning(request, "User   does  not  Exist")
        return redirect("/")
    

    if default_token_generator.check_token(user, token):
        print("Signup  verified successfully")
        user.is_active = True
        user.last_login = timezone.now()
        user.save(update_fields=['last_login','is_active'])
        messages.success(request, "Signup  verified successfully")
        return  redirect("/") 
    else:
        print("The  verify  link is invalid or expired.")
        messages.warning(request, "The  verify  link is invalid or expired.")
        return  redirect("/")


def   register_user_verify_signup(request):
    if   request.user.is_authenticated:
        return redirect('add_mill')
    
    if request.method == "POST":
        try:
            username = request.POST.get("username", "").strip()
            password = request.POST.get("password", "").strip()
            email = request.POST.get("email", "").strip()
            designation = request.POST.get("designation", "").strip()
            company = request.POST.get("company_name", "").strip()
            name = request.POST.get("name", "").strip()

            # Map form values → readable field names for user message
            fields = {
                "Username": username,
                "Password": password,
                "Email": email,
                "designation": designation,
                "company":company,
                "name":name
            }

            # Detect empty fields
            missing_fields = [name for name, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))
            

            if   User.objects.filter(username=username).exists():
                messages.warning(request,  "This  username  is  already  taken !")
                return redirect(request.META.get('HTTP_REFERER'))

            

            user = User.objects.create_user(username=username,email=email, password=password,first_name=name,is_active=False)
            role = "Mill_owners"
            # Assign user to selected group
            group = Group.objects.get(name=role)
            user.groups.add(group)

            user.save()

            # ✅ Send  verify  sign  up  link  
        

            try:
                # Generate password reset link
                token = default_token_generator.make_token(user)
                uid =  urlsafe_base64_encode(force_bytes(user.pk))

                reset_link = f"{settings.DOMAIN}{reverse('verify_signup_mail', args=[uid, token])}"

                current_year  = str(timezone.now().year)

                context = {
                    "username": username,
                    "reset_link": reset_link,
                    "current_year":current_year
                }

                # Send reset email
                send_html_email(
                    subject="Verify  Signup",
                    to_email=email,
                    context=context,
                    template_path="Emails/Verify_signup_email.html"
                )

                print("Success  Verify  Signup   link  execution  ")

            except   Exception   as   e:
                print("Error   in  Verify  Signup   link  execution  ",e)

            customer_id  =  generate_customerid()  + '__' +  str(user.pk)

            MillOwnersProfile.objects.create(
                owner_p_id=user.pk,
                company=company,
                designation=designation,
                customer_id =  customer_id

            )

            messages.success(request, 'User  registered  successfully , Check  Verify  Sign  Up   email !')
            return redirect('login')
        except  Exception  as  e:

            print("exception  : ",e)
            messages.warning(request, 'User  registration  failed !')
            return redirect(request.META.get('HTTP_REFERER'))
        

    return render(request, 'Auths/register.html') 