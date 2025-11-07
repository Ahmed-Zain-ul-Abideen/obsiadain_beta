from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from    webapp.models  import   UsersLoginLogoutActivitiesLog


@receiver(user_logged_in)
def on_user_login(sender, request, user, **kwargs):
    try:
        ip = get_client_ip(request)
    except:
        ip =  None

    try:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    except:
        user_agent  =  None

    UsersLoginLogoutActivitiesLog.objects.create(
        user=user,
        activity_type="login",
        ip_address=ip,
        user_agent=user_agent,
        timestamp=timezone.now()
    )


@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    try:
        ip = get_client_ip(request)
    except:
        ip =  None

    try:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    except:
        user_agent  =  None

    UsersLoginLogoutActivitiesLog.objects.create(
        user=user,
        activity_type="logout",
        ip_address=ip,
        user_agent=user_agent,
        timestamp=timezone.now()
    )


def get_client_ip(request):
    """Extract client IP safely even behind proxy"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
