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


@register.filter(is_safe=True)
def convert_seconds_into_hours(value, default=None):
    if value is None:
        return "0h 00min"
    hours = value // 3600
    minutes = (value % 3600) // 60
    return f"{hours}h {minutes:02d}min"
