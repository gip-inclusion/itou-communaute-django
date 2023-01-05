"""
https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
"""
from django import template
from django.urls import reverse
from django.utils.http import urlencode


register = template.Library()


@register.filter(is_safe=False)
def pluralizefr(value, arg="s"):
    """
    Return a plural suffix if the value is greater than 1
    NB : the basic django pluralize filter returns the plural suffix for value==0
    """
    try:
        return arg if float(value) > 1 else ""
    except ValueError:  # Invalid string that's not a number.
        pass
    except TypeError:  # Value isn't a string or a number; maybe it's a list?
        try:
            return arg if len(value) > 1 else ""
        except TypeError:  # len() of unsized object.
            pass
    return ""


@register.simple_tag
def inclusion_connect_url(next_url, anchor=None):
    if anchor:
        next_url = f"{next_url}#{anchor}"
    params = {"next_url": next_url}
    return f"{reverse('inclusion_connect:authorize')}?{urlencode(params)}"
