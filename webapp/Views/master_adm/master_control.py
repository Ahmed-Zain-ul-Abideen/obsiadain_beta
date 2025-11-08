from   django.contrib   import   messages
from   django.shortcuts   import   redirect,render
from   webapp.models   import  *
from  django.contrib.auth.models   import   User
from django.contrib.auth.models import User, Group 
import re
 

def   master_settings_view(request):

    if  not    request.user.is_authenticated:
        return redirect('login')
    elif     request.user.is_superuser:
        settings_obj, created =  Master_Settings.objects.get_or_create(id=1)

        if request.method == "POST":
            contact = request.POST.get("contact", "").strip()
            # notif_doc_1= request.FILES.get("notif_doc_1")
            # if   not   notif_doc_1:
            #     messages.warning(request,  "Attachment   is   missing")
            #     return redirect(request.META.get('HTTP_REFERER'))
            

            # allowed_types = ["application/pdf", "image/jpeg", "image/png"]

            # if notif_doc_1 and notif_doc_1.content_type not in allowed_types:
            #     messages.error(request, "Invalid file! Only PDF, JPG, JPEG, PNG are allowed.")
            #     return redirect(request.META.get('HTTP_REFERER'))

            # Check empty input
            if not contact:
                messages.error(request, "Contact number is required.")
                return redirect(request.META.get("HTTP_REFERER"))

            # Regex for Pakistani PTCL or Mobile number
            pattern = r"^(03[0-9]{9}|0[0-9]{10})$"
            if not re.match(pattern, contact):
                messages.warning(request, "Invalid Pakistani phone number. Format examples: 03001234567 or 04212345678")
                return redirect(request.META.get("HTTP_REFERER"))

            # Save
            settings_obj.contact = contact
            settings_obj.save()
            messages.success(request, "Contact updated successfully!")
            return redirect("master_settings")

        return render(request, "Master_Adm/master_settings.html", {"settings": settings_obj})
    else:
        return   render(request,'Denied/permission_denied.html')



def   view_fbr_oficials(request):
    
    if  not    request.user.is_authenticated:
        return redirect('login')
    elif     request.user.is_superuser:
        fbr_oficials =  False
        if    Mills_Senior_Point_of_Contact.objects.exists():
            fbr_oficials  =  Mills_Senior_Point_of_Contact.objects.all().order_by('-id')
        
        return   render(request,'Master_Adm/fbr_officials_list.html',{'fbr_oficials':fbr_oficials})
    else: 
        return   render(request,'Denied/permission_denied.html')
    

    
def   add_fbr_oficials(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if not request.user.is_superuser:
        return redirect("view_mills")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        contact = request.POST.get("contact", "").strip()
        password = request.POST.get("password1", "").strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("add_fbr_oficials")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        

        # Add to Inspector group
        inspector_group, created = Group.objects.get_or_create(name="FBR_officials")
        user.groups.add(inspector_group)
        user.save()

        Mills_Senior_Point_of_Contact.objects.create(
            user_id  =  user.pk,
            contact =  str(contact)
        )

        messages.success(request, "FBR official registered successfully")
        return redirect("view_fbr_oficials")

    return render(request, "Master_Adm/add_fbr_officials.html")  