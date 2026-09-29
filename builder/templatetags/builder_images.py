"""{{ url|img:600 }} — angalia builder/images.py kwa maelezo kamili."""
from django import template

from builder.images import image_url

register = template.Library()


@register.filter(name='img')
def img(url, size=None):
    """`{{ site.logo_url|img:80 }}` au `{{ site.logo_url|img:"64x64" }}`."""
    if size is None:
        return image_url(url)
    s = str(size)
    if 'x' in s:
        w, h = s.split('x', 1)
        return image_url(url, width=int(w) if w else None, height=int(h) if h else None)
    return image_url(url, width=int(s))
