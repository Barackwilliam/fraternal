"""Mjulishe mmiliki wa website swali jipya linapofika.

KWA NINI

Awali `submit_inquiry` ilihifadhi swali tu. Mmiliki aliliona pale tu
alipoingia kwenye paneli — na wamiliki wengi wa biashara ndogo hawaingii
kila siku. Kwa biashara, swali lisilojibiwa kwa siku mbili ni mteja
aliyekwenda kwa mshindani.

Barua inabeba kila kitu kinachohitajika kujibu papo hapo kutoka kwenye
simu: kitufe cha WhatsApp chenye ujumbe tayari, kupiga simu, na "Reply"
ya email inayokwenda moja kwa moja kwa mgeni.

INAPOKWENDA
    1. contact_email ya website (ndiyo inayoonekana kwa wateja)
    2. email ya akaunti ya mmiliki
Zote mbili zikiwa tofauti, zote zinapata. Hakuna yoyote — hakuna barua,
lakini swali bado limehifadhiwa kwenye paneli.

KINGA
    - Barua inatumwa kwenye thread ya nyuma: mgeni hasubiri Brevo.
    - Kikomo cha barua 10 kwa saa kwa kila website, juu ya kikomo cha
      maswali 30 kwa saa kilichopo. Bot ikipita kinga hizo, sanduku la
      mmiliki halijazwi.
"""
import logging
import re
import threading
from urllib.parse import quote

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import connection
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

MAX_PER_HOUR = 10


def _recipients(site):
    seen, out = set(), []
    for addr in (getattr(site, 'contact_email', '') or '',
                 getattr(site.owner, 'email', '') or ''):
        a = addr.strip()
        if a and '@' in a and a.lower() not in seen:
            seen.add(a.lower())
            out.append(a)
    return out


def whatsapp_number(phone):
    """'0754 000 111' -> '255754000111' (Tanzania), '+255 754…' -> '255754…'."""
    digits = re.sub(r'\D', '', phone or '')
    if digits.startswith('0') and len(digits) == 10:
        digits = '255' + digits[1:]
    return digits if len(digits) >= 9 else ''


def _allowed(site_id):
    """Kikomo cha barua kwa saa. `add` na `incr` ni salama kwa maombi ya pamoja."""
    key = f'inq_mail:{site_id}'
    cache.add(key, 0, timeout=3600)
    try:
        return cache.incr(key) <= MAX_PER_HOUR
    except ValueError:            # key imeisha katikati
        cache.set(key, 1, timeout=3600)
        return True


def notify_owner(inquiry):
    """Anza kutuma kwenye thread ya nyuma. Inarudi papo hapo."""
    threading.Thread(target=_send, args=(inquiry.pk,),
                     name=f'jt-inquiry-mail-{inquiry.pk}', daemon=True).start()


def _send(inquiry_pk):
    from .models import SiteInquiry
    try:
        inq = (SiteInquiry.objects.select_related('website', 'website__owner', 'item')
               .filter(pk=inquiry_pk).first())
        if not inq:
            return
        site = inq.website
        to = _recipients(site)
        if not to:
            logger.info('[inquiry] %s: hakuna email ya mmiliki — swali liko kwenye paneli tu', site.subdomain)
            return
        if not _allowed(site.id):
            logger.warning('[inquiry] %s: kikomo cha barua kwa saa kimefikiwa', site.subdomain)
            return

        base = (getattr(settings, 'SITE_URL', '') or 'https://www.jamiitek.com').rstrip('/')
        wa = whatsapp_number(inq.phone)
        greeting = (f'Hello {inq.name}, thank you for contacting {site.site_name}. '
                    f'We received your message')
        if inq.item:
            greeting += f' about "{inq.item.title}"'
        greeting += '.'

        ctx = {
            'site': site,
            'inq': inq,
            'wa_link': f'https://wa.me/{wa}?text={quote(greeting)}' if wa else '',
            'tel_link': f'tel:{re.sub(r"[^0-9+]", "", inq.phone)}',
            'inbox_url': f'{base}/builder/site/{site.id}/inquiries/',
        }
        subject = f'📩 New inquiry from {inq.name}' + (f' — {inq.item.title}' if inq.item else '')
        subject += f' · {site.site_name}'

        text = render_to_string('builder/emails/new_inquiry.txt', ctx)
        html = render_to_string('builder/emails/new_inquiry.html', ctx)
        msg = EmailMultiAlternatives(
            subject=subject[:200], body=text, to=to,
            reply_to=[inq.email] if inq.email else None,
            headers={'X-JT-Category': 'inquiry'},
        )
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=True)
        logger.info('[inquiry] taarifa imetumwa: %s -> %s', site.subdomain, ', '.join(to))
    except Exception:
        logger.exception('[inquiry] taarifa kwa mmiliki imeshindwa')
    finally:
        connection.close()
