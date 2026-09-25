"""Vichujio vidogo vya blog: muda wa "3 HOURS AGO", herufi ya avatar, rangi ya avatar."""
from datetime import datetime

from django import template
from django.utils import timezone
from django.utils.dateformat import format as date_format

register = template.Library()


@register.filter
def ago(value):
    """'JUST NOW', '5 MIN AGO', '3 HOURS AGO', '2 DAYS AGO', au tarehe (zaidi ya wiki)."""
    if not value:
        return ''
    if not isinstance(value, datetime):
        return date_format(value, 'M j, Y')
    now = timezone.now()
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    secs = int((now - value).total_seconds())
    if secs < 60:
        return 'JUST NOW'
    mins = secs // 60
    if mins < 60:
        return f'{mins} MIN AGO'
    hours = mins // 60
    if hours < 24:
        return f'{hours} HOUR{"S" if hours != 1 else ""} AGO'
    days = hours // 24
    if days < 7:
        return f'{days} DAY{"S" if days != 1 else ""} AGO'
    return date_format(timezone.localtime(value), 'M j, Y').upper()


@register.filter
def initial(name):
    name = (name or '').strip()
    return name[:1].upper() if name else '?'


@register.filter
def avatar_hue(name):
    """Rangi ya kudumu kwa kila jina (0-359), ili avatar zitofautiane."""
    return sum(ord(c) for c in (name or '')) * 47 % 360
