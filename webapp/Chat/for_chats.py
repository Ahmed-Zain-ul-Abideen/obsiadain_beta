from django.contrib.auth.models import User
from django.shortcuts import render,redirect
 
def  Chat_user_list(request):
    if  not    request.user.is_authenticated:
        return  redirect('login')
    
    if  not   request.user.groups.filter(name__in=["Mill_owners", "Inspectors", "FBR_officials"]).exists():
        return   render(request,'Denied/permission_denied.html')
    
    users = User.objects.filter(groups__name__in=["Mill_owners", "Inspectors", "FBR_officials"]).exclude(id=request.user.id).distinct()
    return render(request, "Chat/Chat_with_users.html", {"users": users})


def chat_room(request, username):
    if  not    request.user.is_authenticated:
        return  redirect('login')
    
    if  not   request.user.groups.filter(name__in=["Mill_owners", "Inspectors", "FBR_officials"]).exists():
        return   render(request,'Denied/permission_denied.html')
    
    return render(request, "chat/Here_chat.html", {"other_user": User.objects.get(username=username)})
