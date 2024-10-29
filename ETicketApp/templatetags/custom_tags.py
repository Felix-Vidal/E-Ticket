from django import template

register = template.Library()

@register.filter
def in_groups(user, group_names):
    group_list = group_names.split(",")  # Dividir a string em uma lista de grupos
    return user.groups.filter(name__in=group_list).exists()