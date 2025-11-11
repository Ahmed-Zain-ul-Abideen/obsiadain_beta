from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib import messages
from  webapp.Views.utils   import  invalidate_user_tokens
from django.shortcuts import render, redirect

def set_password_view(request, uid, token):

    try:
        user = User.objects.get(pk=uid)
        print("user  exist")
    except User.DoesNotExist:
        print("user not  exist")
        messages.error(request, "User   does  not  Exist")
        return redirect("/")

    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm_password", "").strip()

        if not password or not confirm_password:
            messages.error(request, "Both fields required.")
            return redirect(request.path)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(request.path)

        user.set_password(password)
        user.save()

        messages.success(request, "Password set successfully. You may log in.")
        return  redirect("login") 
    else:  

        if not default_token_generator.check_token(user, token):
            print("user toke not  exist")
            messages.error(request, "The reset link is invalid or expired.")
            return redirect("/")
        else:
            print("link  is  valid")
            invalidate_user_tokens(user)

    

    return render(request, "Auths/set_password_form.html", {"user": user})
