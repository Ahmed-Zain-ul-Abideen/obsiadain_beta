from   django.contrib   import   messages
from django.urls import reverse
from django.conf import settings
from   django.shortcuts   import   redirect,render
from   webapp.models   import  *
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from   django .utils   import   timezone
import  random
import   string
from django.utils.http import urlsafe_base64_encode  
from django.utils.encoding import force_bytes 
from  webapp.Views.utils   import   verify_email_smtp,send_html_email


def  generate_unitid():
    """Generate a unique alphanumeric NTN starting with 'MILL-'."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return  f"UNIT-{suffix}"


def   view_mills(request):

    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if   request.user.is_superuser:

        mills_data  =  False
        if  Mills.objects.exists():
            mills_data = Mills.objects.all().order_by('-id')
    elif  request.user.groups.filter(name="Inspectors").exists():
        mills_data  =  False
        if  Mills.objects.exists():
            mills_data = Mills.objects.all().order_by('-id') 
    elif  request.user.groups.filter(name="Mill_owners").exists():

        mills_data  =  False
        if  Mills.objects.filter(owner_id=request.user.id).exists():
            mills_data = Mills.objects.filter(owner_id=request.user.id).order_by('-id') 
    else:
        return   render(request,'Denied/permission_denied.html')
    
    return render(request, 'Mills/view_mills.html',  {"mills_data":mills_data})

    
 
def   register_mill_by_owner(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if   not   request.user.groups.filter(name="Mill_owners").exists():
        return   render(request,'Denied/permission_denied.html')


    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            address = request.POST.get("address", "").strip()
            lat = request.POST.get("lat", "").strip()
            lon = request.POST.get("lon", "").strip()
            print("lat   lon   :  ",lat,"   ",lon)
            ntn = request.POST.get("ntn", "").strip()
            gst = request.POST.get("gst", "").strip()
            spindles_installed = request.POST.get("spindles_installed", "").strip()
            rotors_installed = request.POST.get("rotors_installed", "").strip()
            doubling_machines_installed = request.POST.get("doubling_machines_installed", "").strip() 
    
            authorized_p_contact = request.POST.get("authorized_p_contact", "").strip()
            authorized_p_email = request.POST.get("authorized_p_email", "").strip()
            senior_p_contact = request.POST.get("senior_p_contact", "").strip()
            senior_p_email = request.POST.get("senior_p_email", "").strip() 

            fields = {
                "Name": name,
                "Address": address,
                "NTN": ntn,
                "GST": gst,
                "Spindles Installed": spindles_installed,
                "Rotors Installed": rotors_installed,
                "Doubling Machines Installed": doubling_machines_installed,
                "authorized_p_contact":authorized_p_contact,
                "authorized_p_email":authorized_p_email,
                "senior_p_contact":senior_p_contact,
                "senior_p_email":senior_p_email,
                "lat": lat,
                "lon":lon
                 
            }

            missing_fields = [field for field, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))


            if   Mills.objects.filter(name=name).exists():
                messages.warning(request, 'Mill  with   the  same  name  is  already  registered !')
                return redirect(request.META.get('HTTP_REFERER'))
                # mill =  Mills.objects.filter(name=name).first()
                # if   mill.units  ==  1:
                #     mill.units  = 2
                # else:
                #     mill.units   =   mill.units   +  1

                # mill.save()
            else: 
                mill = Mills.objects.create(name=name,owner_id  =   request.user.id)      
                mill.save()


            

            mill_unit  =  Mills_Units.objects.create(
                mill_id = mill.pk,
                address=address,ntn=ntn,gst=gst,spindles_installed=spindles_installed,
                rotors_installed=rotors_installed,doubling_machines_installed=doubling_machines_installed,
                authorized_p_contact = authorized_p_contact,authorized_p_email=authorized_p_email,
                senior_p_contact = senior_p_contact,senior_p_email=senior_p_email,
                lat =  lat, lon = lon 
            )

            
            unit_id  =  generate_unitid()  + '__' +  str(mill_unit.pk)

            mill_unit.unit_id   =   unit_id

            mill_unit.save()

            messages.success(request, 'Mill  registered  successfully !')
            return redirect('view_mills')
            # return redirect(request.META.get('HTTP_REFERER')) 
        except  Exception  as   e:
            print("exception  :  ",e)
            messages.warning(request, 'Mill  registeration  failed !')
            return redirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'Mills/add_mill_v.html') 
    
 

def   register_mill_by_fbr_official(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if  not   request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')


    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            address = request.POST.get("address", "").strip()
            lat = request.POST.get("lat", "").strip()
            lon = request.POST.get("lon", "").strip()
            print("lat   lon   :  ",lat,"   ",lon)
            ntn = request.POST.get("ntn", "").strip()
            gst = request.POST.get("gst", "").strip()
            spindles_installed = request.POST.get("spindles_installed", "").strip()
            rotors_installed = request.POST.get("rotors_installed", "").strip()
            doubling_machines_installed = request.POST.get("doubling_machines_installed", "").strip()
            username = request.POST.get("username", "").strip() 
            email = request.POST.get("email", "").strip() 


            authorized_p_contact = request.POST.get("authorized_p_contact", "").strip()
            authorized_p_email = request.POST.get("authorized_p_email", "").strip()
            senior_p_contact = request.POST.get("senior_p_contact", "").strip()
            senior_p_email = request.POST.get("senior_p_email", "").strip()

            fields = {
                "Name": name,
                "Address": address,
                "NTN": ntn,
                "GST": gst,
                "Spindles Installed": spindles_installed,
                "Rotors Installed": rotors_installed,
                "Doubling Machines Installed": doubling_machines_installed,
                "authorized_p_contact":authorized_p_contact,
                "authorized_p_email":authorized_p_email,
                "senior_p_contact":senior_p_contact,
                "senior_p_email":senior_p_email,
                "Username": username, 
                "Email": email,
                "lat": lat,
                "lon":lon 
                 
            }

            missing_fields = [field for field, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))
            
            
            if   Mills.objects.filter(name=name).exists():
                messages.warning(request, 'Mill  with   the  same  name  is  already  registered !')
                return redirect(request.META.get('HTTP_REFERER')) 

            
            # verify_response = verify_email_smtp(email)
            # if  verify_response:
            #     if   verify_response   ==  4975:
            #         messages.warning(request, "Email   verification  server  is  down.")
            #         return redirect(request.META.get("HTTP_REFERER"))
            # elif  not   verify_response:
            #     messages.warning(request, "Invalid email .")
            #     return redirect(request.META.get("HTTP_REFERER")) 
            # else:
            #     pass


            if   User.objects.filter(username=username).exists():
                messages.warning(request,  "This  username  is  already  taken !")
                return redirect(request.META.get('HTTP_REFERER'))

            user = User.objects.create_user(username=username, email=email)
            user.set_unusable_password() 

            # Assign user to selected group
            group = Group.objects.get(name="Mill_owners")
            user.groups.add(group)

            user.save()

            try:
                # Generate password reset link
                token = default_token_generator.make_token(user)
                uid =  urlsafe_base64_encode(force_bytes(user.pk))

                reset_link = f"{settings.DOMAIN}{reverse('set_password', args=[uid, token])}"

                current_year  = str(timezone.now().year)

                context = {
                    "username": username,
                    "reset_link": reset_link,
                    "current_year": current_year
                }

                # Send reset email
                send_html_email(
                    subject="Set Your Password",
                    to_email=email,
                    context=context,
                    template_path="Emails/set_password_email.html"
                )

                print("Success  password   reset   link  execution  ")

            except   Exception   as   e:
                print("Error   in  password   reset   link  execution  ",e)

             
             
            mill = Mills.objects.create(name=name,owner_id  =   user.pk)      
            mill.save()

            mill_unit  =  Mills_Units.objects.create(
                mill_id = mill.pk,
                address=address,ntn=ntn,gst=gst,spindles_installed=spindles_installed,
                rotors_installed=rotors_installed,doubling_machines_installed=doubling_machines_installed,
                authorized_p_contact = authorized_p_contact,authorized_p_email=authorized_p_email,
                senior_p_contact = senior_p_contact,senior_p_email=senior_p_email,
                lat =  lat, lon = lon
                
            )


            unit_id  =  generate_unitid()  + '__' +  str(mill_unit.pk)

            mill_unit.unit_id   =   unit_id

            mill_unit.save()

            messages.success(request, 'Mill  registered  successfully !')
            return redirect('view_mills')
            # return redirect(request.META.get('HTTP_REFERER')) 
        except  Exception  as   e:
            print("exception  :  ",e)
            messages.warning(request, 'Mill  registeration  failed !')
            return redirect(request.META.get('HTTP_REFERER'))
        
    return render(request, 'Mills/add_mill.html') 



def   edit_mill_only(request, mill_id):

    if not request.user.is_authenticated:
        return redirect("login")
    

    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            if   not   name:
                messages.warning(request, "Mill   name   is  required")
                return redirect(request.META.get("HTTP_REFERER"))

            Mills.objects.filter(pk=mill_id).update(name=name)
            return   redirect("view_mills") 
        except Exception as e:

            print("Edit error:", e)
            messages.error(request, "Failed to update mill  info.")
            return redirect(request.META.get("HTTP_REFERER"))
        
    mill =  Mills.objects.filter(pk=mill_id).first()
        
    return render(request, "Mills/edit_mill_only.html", {
        "mill": mill 
    })
            

    

    

def  edit_mill_unit(request, unit_id):
    if not request.user.is_authenticated:
        return redirect("login")

    unit = Mills_Units.objects.filter(id=unit_id).first()
    mill =  Mills.objects.filter(pk=unit.mill_id).first()
    if not unit:
        messages.error(request, "Unit not found.")
        return redirect(request.META.get("HTTP_REFERER"))
        # return redirect("view_mills")

    # mill = unit.mill

    if request.method == "POST":
        try:
            # name = request.POST.get("name", "").strip()
            address = request.POST.get("address", "").strip()
            address_changed  =  False
            if   not   unit.address  ==  address:
                address_changed   =   True
                
            ntn = request.POST.get("ntn", "").strip()
            gst = request.POST.get("gst", "").strip()
            spindles_installed = request.POST.get("spindles_installed", "").strip()
            rotors_installed = request.POST.get("rotors_installed", "").strip()
            doubling_machines_installed = request.POST.get("doubling_machines_installed", "").strip()

            authorized_p_contact = request.POST.get("authorized_p_contact", "").strip()
            authorized_p_email = request.POST.get("authorized_p_email", "").strip()
            senior_p_contact = request.POST.get("senior_p_contact", "").strip()
            senior_p_email = request.POST.get("senior_p_email", "").strip()

            if   address_changed:
                lat = request.POST.get("lat", "").strip()
                lon = request.POST.get("lon", "").strip()
                print("lat   lon   :  ",lat,"   ",lon)

                fields = { 
                    "Address": address,
                    "NTN": ntn,
                    "GST": gst,
                    "Spindles Installed": spindles_installed,
                    "Rotors Installed": rotors_installed,
                    "Doubling Machines Installed": doubling_machines_installed,
                    "authorized_p_contact":authorized_p_contact,
                    "authorized_p_email":authorized_p_email,
                    "senior_p_contact":senior_p_contact,
                    "senior_p_email":senior_p_email,
                    "lat": lat,
                    "lon": lon
                }
            else:

                fields = {
                    # "Name": name,
                    "Address": address,
                    "NTN": ntn,
                    "GST": gst,
                    "Spindles Installed": spindles_installed,
                    "Rotors Installed": rotors_installed,
                    "Doubling Machines Installed": doubling_machines_installed,
                }


            missing_fields = [f for f,v in fields.items() if not v]
            if missing_fields:
                messages.warning(request, ", ".join(missing_fields)+" is required")
                return redirect(request.META.get("HTTP_REFERER"))
            

            if    address_changed:
                unit.lat  =  lat
                unit.lon  =  lon

            # Update Mill
            # mill.name = name
            # mill.save()

            # Update Unit
            unit.address = address
            unit.ntn = ntn
            unit.gst = gst
            unit.spindles_installed = spindles_installed
            unit.rotors_installed = rotors_installed
            unit.doubling_machines_installed = doubling_machines_installed

            unit.authorized_p_contact = authorized_p_contact
            unit.authorized_p_email = authorized_p_email
            unit.senior_p_contact = senior_p_contact 
            unit.senior_p_email = senior_p_email
            unit.save()

            messages.success(request, "Mill unit  updated successfully!")
            return redirect("view_mills") 
        except Exception as e:
            print("Edit error:", e)
            messages.error(request, "Failed to update mill  unit.")
            return redirect(request.META.get("HTTP_REFERER"))

    return render(request, "Mills/edit_unit_to_mill.html", {
        "mill": mill,
        "unit": unit
    })




def   Add_unit_to_mill(request,mill_id):


    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if  not   request.user.groups.filter(name="Mill_owners").exists():
        return   render(request,'Denied/permission_denied.html')


    mill =  Mills.objects.filter(pk=mill_id).first()


    if request.method == "POST":
        try: 
            address = request.POST.get("address", "").strip()
            lat = request.POST.get("lat", "").strip()
            lon = request.POST.get("lon", "").strip()
            print("lat   lon   :  ",lat,"   ",lon)
            ntn = request.POST.get("ntn", "").strip()
            gst = request.POST.get("gst", "").strip()
            spindles_installed = request.POST.get("spindles_installed", "").strip()
            rotors_installed = request.POST.get("rotors_installed", "").strip()
            doubling_machines_installed = request.POST.get("doubling_machines_installed", "").strip() 

            authorized_p_contact = request.POST.get("authorized_p_contact", "").strip()
            authorized_p_email = request.POST.get("authorized_p_email", "").strip()
            senior_p_contact = request.POST.get("senior_p_contact", "").strip()
            senior_p_email = request.POST.get("senior_p_email", "").strip()

            fields = { 
                "Address": address,
                "NTN": ntn,
                "GST": gst,
                "Spindles Installed": spindles_installed,
                "Rotors Installed": rotors_installed,
                "Doubling Machines Installed": doubling_machines_installed,
                "authorized_p_contact":authorized_p_contact,
                "authorized_p_email":authorized_p_email,
                "senior_p_contact":senior_p_contact,
                "senior_p_email":senior_p_email,
                "lat": lat,
                "lon":lon
                 
            }

            missing_fields = [field for field, value in fields.items() if not value]

            if missing_fields:
                msg = ", ".join(missing_fields) + " " + ("is missing" if len(missing_fields)==1 else "are missing")
                messages.warning(request, msg)
                return redirect(request.META.get('HTTP_REFERER'))


            # if   Mills.objects.filter(name=name).exists():
            
            #     if   mill.units  ==  0:
            #         mill.units  = 2
            #     else:
            #         mill.units   =   mill.units   +  1

            #     mill.save()
            # else: 
            #     mill = Mills.objects.create(name=name,owner_id  =   request.user.id)      
            #     mill.save()

            mill_unit  =  Mills_Units.objects.create(
                mill_id = mill_id,
                address=address,ntn=ntn,gst=gst,spindles_installed=spindles_installed,
                rotors_installed=rotors_installed,doubling_machines_installed=doubling_machines_installed,
                authorized_p_contact = authorized_p_contact,authorized_p_email=authorized_p_email,
                senior_p_contact = senior_p_contact,senior_p_email=senior_p_email,
                lat =  lat, lon = lon 
                
            )

            unit_id  =  generate_unitid()  + '__' +  str(mill_unit.pk)

            mill_unit.unit_id   =   unit_id

            mill_unit.save()

            mill =  Mills.objects.filter(pk=mill_id).first()
            mill.units   =  mill.units  +  1
            mill.save()

            messages.success(request, 'Mill  unit  added  successfully !')
            return redirect('view_mills')
            # return redirect(request.META.get('HTTP_REFERER')) 
        except  Exception  as   e:
            print("exception  :  ",e)
            messages.warning(request, 'Mill  unit  addition  failed !')
            return redirect(request.META.get('HTTP_REFERER'))
    context = {'mill': mill}
    return render(request, 'Mills/add_unit_to_mill.html',context) 
    
    # else:
    #     messages.warning(request, 'Login  first !')
    #     return redirect(request.META.get('HTTP_REFERER'))




# def mills_list(request):
#     mills = Mills.objects.prefetch_related('mills_units').all()
#     return render(request, 'Mills/mills_list.html', {'mills': mills})



def   mills_list(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if   request.user.is_superuser:
        mills_data  =  False
        if  Mills.objects.exists():
            mills_data = Mills.objects.all().order_by('-id')

    elif  request.user.groups.filter(name="Inspectors").exists():
        mills_data  =  False
        if  Mills.objects.filter(mills_units__mill_unit_inspectors=request.user).exists():
            mills_data = Mills.objects.filter(mills_units__mill_unit_inspectors=request.user).order_by('-id')

    else: 
        mills_data  =  False
        if  Mills.objects.filter(owner_id=request.user.id).exists():
            mills_data = Mills.objects.filter(owner_id=request.user.id).order_by('-id')

    return render(request, 'Mills/mills_list.html',  {"mills":mills_data})