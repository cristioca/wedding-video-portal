from django import template

register = template.Library()

@register.filter
def attr(obj, attr_name):
    """Get attribute of an object dynamically using getattr"""
    try:
        return getattr(obj, attr_name)
    except AttributeError:
        return None
