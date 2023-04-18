"""
https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from lacommunaute.utils.urls import urlize


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


@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def urlizetrunc_target_blank(value, limit, autoescape=True):
    """
    Convert URLs into clickable links, truncating URLs to the given character
    limit, and adding 'rel=nofollow' attribute to discourage spamming.

    Argument: Length to truncate URLs to.
    """
    urlized = urlize(value, trim_url_limit=int(limit), nofollow=True, autoescape=autoescape)
    return mark_safe(urlized.replace("<a ", '<a target="_blank" '))


@register.filter(is_safe=True)
@stringfilter
def img_fluid(value):
    return mark_safe(value.replace("<img ", '<img class="img-fluid" '))
