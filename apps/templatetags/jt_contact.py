"""{% contact "wa" %} — angalia apps/contact.py.

Ni template tag (si context processor tu) ili ifanye kazi pia kwenye barua
pepe, ambazo hutengenezwa bila `request`.
"""
from urllib.parse import quote

from django import template

from apps.contact import contact as _contact

register = template.Library()


@register.simple_tag(name='contact')
def contact_tag(key):
    return _contact().get(key, '')


# Ujumbe unaoanza mazungumzo na bot ya demo — mgeni haanzi na skrini tupu
BOT_GREETING = 'Habari JamiiBot, nataka kujaribu demo'

SHORTCUTS = {
    'whatsapp:bot':  lambda c: f"https://wa.me/{c['bot_wa']}?text={quote(BOT_GREETING)}",
    'whatsapp:team': lambda c: f"https://wa.me/{c['wa']}",
    'tel:team':      lambda c: f"tel:{c['phone']}",
}


@register.filter(name='contact_url')
def contact_url(url):
    """Njia fupi za admin -> URL halisi kutoka apps/contact.py.

    Kwenye Django admin (Hero slides, n.k.) andika `whatsapp:bot` badala ya
    namba. Ukibadilisha namba kwenye Render, kitufe kinafuata — hakuna slide
    ya kuhariri tena.
    """
    key = (url or '').strip().lower()
    if key in SHORTCUTS:
        return SHORTCUTS[key](_contact())
    return url or '#'


@register.filter(name='is_external')
def is_external(url):
    """Kiungo kinachofunguka tab mpya: http(s), wa.me, au njia fupi ya WhatsApp."""
    u = (url or '').strip().lower()
    return u.startswith(('http://', 'https://', 'whatsapp:'))
