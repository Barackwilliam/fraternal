"""{% contact "wa" %} — angalia apps/contact.py.

Ni template tag (si context processor tu) ili ifanye kazi pia kwenye barua
pepe, ambazo hutengenezwa bila `request`.
"""
from django import template

from apps.contact import contact as _contact

register = template.Library()


@register.simple_tag(name='contact')
def contact_tag(key):
    return _contact().get(key, '')
