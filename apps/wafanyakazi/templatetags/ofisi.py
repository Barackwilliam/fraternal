from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def zamani(value):
    """Muda uliopita kwa Kiswahili: 'sasa hivi', 'dk 5 zilizopita', 'saa 3 zilizopita', 'jana'."""
    if not value:
        return ''
    seconds = int((timezone.now() - value).total_seconds())
    if seconds < 60:
        return 'sasa hivi'
    minutes = seconds // 60
    if minutes < 60:
        return f'dakika {minutes} zilizopita'
    hours = minutes // 60
    if hours < 24:
        return f'saa {hours} zilizopita'
    days = hours // 24
    if days == 1:
        return 'jana'
    if days < 30:
        return f'siku {days} zilizopita'
    return timezone.localtime(value).strftime('%d/%m/%Y')
