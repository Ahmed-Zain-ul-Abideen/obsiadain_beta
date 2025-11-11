from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def add_attrs(field, attr_string):
    """
    Usage:
        {{ field|add_attrs:"class=form-control text-center,placeholder=Enter Item Name" }}
    """
    attrs = {}
    for pair in attr_string.split(','):
        key, value = pair.split('=', 1)
        attrs[key.strip()] = value.strip()
    return field.as_widget(attrs=attrs)