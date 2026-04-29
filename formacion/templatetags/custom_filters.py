from django import template

register = template.Library()

@register.filter
def zip_list(list1, list2):
    return zip(list1, list2)

@register.filter
def has_group(user, group_names):
    names = [g.strip() for g in group_names.split(',')]
    return user.is_authenticated and user.groups.filter(name__in=names).exists()
