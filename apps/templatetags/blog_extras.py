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


# ─────────────────────────────────────────────
# Picha zenye ukubwa sahihi (kasi). Unsplash inatoa ukubwa wowote kupitia URL
# (w, q, auto=format → WebP/AVIF). Picha zingine (Supabase) zinarudi kama zilivyo —
# hizo zinapunguzwa wakati wa kupakia (widget ya admin).
# ─────────────────────────────────────────────
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode  # noqa: E402


def _is_resizable(url):
    return bool(url) and 'images.unsplash.com' in url


def _sized(url, w, ratio=None):
    parts = urlsplit(url)
    q = {k: v for k, v in parse_qsl(parts.query) if k not in ('w', 'h', 'q', 'fm', 'auto', 'fit', 'crop', 'ar', 'dpr')}
    q.update({'w': str(w), 'q': '70', 'auto': 'format', 'fit': 'crop'})
    if ratio:
        q['ar'] = ratio
    return urlunsplit(parts._replace(query=urlencode(q)))


@register.filter
def img(url, width=800):
    """{{ post.cover_image|img:400 }} → URL ya picha yenye upana huo (Unsplash)."""
    if not _is_resizable(url):
        return url or ''
    return _sized(url, int(width))


@register.filter
def srcset(url, widths='400,800,1200'):
    """{{ post.cover_image|srcset:"480,800,1200" }} → 'url 480w, url 800w, …' (au '')."""
    if not _is_resizable(url):
        return ''
    return ', '.join(f'{_sized(url, int(w))} {int(w)}w' for w in str(widths).split(','))


@register.filter
def img_ratio(url, ratio='16:9'):
    """Picha iliyokatwa kwa uwiano (kwa JSON-LD: 1:1, 4:3, 16:9)."""
    if not _is_resizable(url):
        return url or ''
    return _sized(url, 1200, ratio)


@register.filter
def img_host(url):
    """https://host — kwa <link rel=preconnect>."""
    if not url:
        return ''
    p = urlsplit(url)
    return f'{p.scheme}://{p.netloc}' if p.netloc else ''
