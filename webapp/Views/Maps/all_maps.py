from django.http import JsonResponse
from   django.shortcuts   import   redirect,render
from django.core.paginator import Paginator
from  webapp.models  import   *


def   view_locations(request):
    
    if  not    request.user.is_authenticated:
        return redirect('login')
    elif   not   request.user.is_superuser:
        return   render(request,'Denied/permission_denied.html') 
    else: 
        return   render(request,'Maps/map_one.html')
    

def mills_data_api(request):
    page = int(request.GET.get("page", 1))
    per_page = int(request.GET.get("per_page", 500))

    qs = Mills_Units.objects.filter(lat__isnull=False, lon__isnull=False)\
        .select_related("mill").order_by("-id")

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    data = list(page_obj.object_list.values(
        "id",
        "address",
        "lat",
        "lon",
        "ntn",
        "gst",
        "spindles_installed",
        "rotors_installed",
        "doubling_machines_installed",
        "mill__name",
    ))

    return JsonResponse({
        "mills": data,
        "has_next": page_obj.has_next(),
        "page": page
    })
