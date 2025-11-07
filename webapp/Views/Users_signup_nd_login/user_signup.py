from django.contrib.auth.models import User, Group
from   django.contrib   import   messages
from   webapp.models  import   MillOwnersProfile
from   django.shortcuts   import   redirect,render

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

            MillOwnersProfile.objects.create(
                owner_p_id=user.pk,
                company=company,
                designation=designation

            )

            messages.success(request, 'User  registered  successfully !')
            return redirect('login')
        except  Exception  as  e:

            print("exception  : ",e)
            messages.warning(request, 'User  registration  failed !')
            return redirect(request.META.get('HTTP_REFERER'))
        

    return render(request, 'Auths/register.html') 
    

        
