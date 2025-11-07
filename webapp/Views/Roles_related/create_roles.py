from django.contrib.auth.models import Group

def   create_roles():

    roles = ["Mill_owners", "Inspectors", "FBR_officials"]

    for role in roles:
        Group.objects.get_or_create(name=role)

    return  True

