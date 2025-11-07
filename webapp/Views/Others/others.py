from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group 
from django.contrib import messages
from  webapp.models   import   *

def add_inspector(request):
    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if  not  request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password1", "").strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("add_inspector")

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        

        # Add to Inspector group
        inspector_group, created = Group.objects.get_or_create(name="Inspectors")
        user.groups.add(inspector_group)
        user.save()

         

        messages.success(request, "Inspector registered successfully")
        return redirect("view_mills")

    return render(request, "Others/add_inspector.html")


def assign_inspector(request, unit_id):

    if  not    request.user.is_authenticated:
        return redirect('login')

    if  not  request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html')

    this_mil  = Mills_Units.objects.filter(pk=unit_id).first() 

    inspectors = False 
    if     User.objects.filter(groups__name="Inspectors").exists(): 
        
        inspectors =  User.objects.filter(groups__name="Inspectors")
     

    if request.method == "POST":
        inspector_id = request.POST.get("inspector_id")
        print("inspector_id  i am herw",inspector_id,"  ",unit_id)
        if inspector_id:  

            Mills_Units.objects.filter(pk=unit_id).update(mill_unit_inspectors_id=inspector_id)
            messages.success(request, "Inspector assigned successfully")
            return redirect("view_mills")
    

    print("inspectors ",inspectors)
    context = { 
        "inspectors": inspectors,
        "this_mil":this_mil
    }

    return render(request, "Others/assign_inspector.html", context)



def add_inspection_report(request, mill_id, unit_id):  

    if  not    request.user.is_authenticated:
        return redirect('login')
    
    if  not  request.user.groups.filter(name="Inspectors").exists():
        return   render(request,'Denied/permission_denied.html')

    if request.method == "POST":
        # Extract & clean fields
        num_camera_installed = request.POST.get("num_camera_installed", "").strip()
        cameras_online = request.POST.get("cameras_online", "").strip()
        cameras_offline = request.POST.get("cameras_offline", "").strip()
        cpu_online = request.POST.get("cpu_online", "").strip()
        cpu_offline = request.POST.get("cpu_offline", "").strip()
        gpu_online = request.POST.get("gpu_online", "").strip()
        gpu_offline = request.POST.get("gpu_offline", "").strip()
        tnt_software_online = request.POST.get("tnt_software_online", "").strip()
        tnt_software_offline = request.POST.get("tnt_software_offline", "").strip()
        

       

        # Validation — check missing required fields
        fields = {
            "Number of Cameras Installed": num_camera_installed,
            "Cameras Online": cameras_online,
            "Cameras Offline": cameras_offline,
            "CPU Online": cpu_online,
            "CPU Offline": cpu_offline,
            "GPU Online": gpu_online,
            "GPU Offline": gpu_offline,
            "TnT Software Online": tnt_software_online,
            "TnT Software Offline": tnt_software_offline,
        }

        missing_fields = [field for field, value in fields.items() if not value]

        if missing_fields:
            msg = ", ".join(missing_fields) + (" is missing" if len(missing_fields)==1 else " are missing")
            messages.warning(request, msg)
            return redirect(request.META.get('HTTP_REFERER'))
        
        

        # Save inspection record
        Inspection_Reports.objects.create(
            inspector_id=request.user.pk,
            mill_id=mill_id,
            mill_unit_id=unit_id,
            num_camera_installed=int(num_camera_installed),
            cameras_online=int(cameras_online),
            cameras_offline=int(cameras_offline),
            cpu_online=int(cpu_online),
            cpu_offline=int(cpu_offline),
            gpu_online=int(gpu_online),
            gpu_offline=int(gpu_offline),
            tnt_software_online=int(tnt_software_online),
            tnt_software_offline=int(tnt_software_offline),
            
        )

        messages.success(request, "Inspection report submitted successfully!")
 
        return redirect("view_inspection_reports")  # Change this URL if needed
    mill = Mills.objects.filter(pk=mill_id).first()
    unit = Mills_Units.objects.filter(id=unit_id).first()
    context = { 
        "mill":mill,
        "unit":unit
    }
    return render(request, "Others/add_inspection_report.html", context )



def    list_inspectors(request):

    if  not    request.user.is_authenticated:
        return redirect('login')

    if  request.user.is_superuser:
        inspectors  =  False
        if      User.objects.filter(groups__name="Inspectors").exists():
            inspectors =   User.objects.filter(groups__name="Inspectors").all().order_by('-id')

        return   render(request,'Others/inspector_list.html',{"inspectors":inspectors}) 
    else:
        return   render(request,'Denied/permission_denied.html') 

 
def   view_inspection_reports(request):

    if  not    request.user.is_authenticated:
        return redirect('login')

    if  request.user.is_superuser:
        reports  =  False
        if     Inspection_Reports.objects.exists():
            reports = Inspection_Reports.objects.all().order_by('-id') 
    elif  request.user.groups.filter(name="Inspectors").exists():
        reports  =  False
        if    Inspection_Reports.objects.filter(inspector=request.user).exists():
            reports = Inspection_Reports.objects.filter(
                inspector=request.user
            ).select_related(
                "inspector", "mill", "mill_unit"
            ).order_by("-id")
         

        # reports = Inspection_Reports.objects.filter(inspector=inspector_profile)\
        #          .select_related("inspector","mill","mill_unit").order_by('-id')

    elif  request.user.groups.filter(name="Mill_owners").exists():
        # Owner: Show reports for mills owned by this user
        mills = Mills.objects.filter(owner=request.user)
        reports   =  False
        if    Inspection_Reports.objects.filter(mill__in=mills).exists(): 
            reports = Inspection_Reports.objects.filter(mill__in=mills).order_by('-id')
    else:
        return   render(request,'Denied/permission_denied.html')


    return render(request, "Others/view_inspection_reports.html", {"reports": reports})




def   assign_unit_to_me_inspector(request, unit_id,insp_id):

    if  not    request.user.is_authenticated:
        return redirect('login')

    if  not  request.user.groups.filter(name="Inspectors").exists():
        return   render(request,'Denied/permission_denied.html')  

    # if request.method == "POST":   

    Mills_Units.objects.filter(pk=unit_id).update(mill_unit_inspectors_id=insp_id)
        # messages.success(request, "Inspector assigned successfully")
        # return redirect(request.META.get('HTTP_REFERER')) 
    messages.success(request, "Unit  Assigned  to   this  Inspector")
    return   redirect("view_mills")
    # return   render(request,'Denied/permission_denied.html')