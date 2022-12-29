import datetime

from django import template
from django.template.defaultfilters import date, time
from django.utils.timesince import timesince
from django.utils.timezone import is_aware


register = template.Library()


@register.filter(is_safe=False)
def relativetimesince_fr(d):

    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)

    now = datetime.datetime.now(datetime.timezone.utc if is_aware(d) else None)

    if d < now - datetime.timedelta(days=6):
        return f"le {date(d)}, {time(d)}"

    if d < now - datetime.timedelta(days=1):
        return f"{date(d,'l')}, {time(d)}"

    return f"il y a {timesince(d)}"
