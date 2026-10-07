"""
Ripoti ya William kama email iliyopambwa.

Inatumika wILife isipopatikana. Ripoti imeandikwa kwa alama za WhatsApp
(*nzito*, _laini_, "  • kipengele", "────" kwa post ya Grace); hapa inageuzwa
kuwa HTML ya template ya email ya JamiiTek, badala ya maandishi ghafi yenye nyota.
"""
import logging
import os
import re
from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

SECTION_RE = re.compile(r'^(?P<icon>[^\w\s*_]{1,3})\s*\*(?P<title>[^*]+)\*\s*(?P<rest>.*)$')
ITEM_RE = re.compile(r'^\s*[•\-]\s+(?P<body>.+)$')
RULE_RE = re.compile(r'^\s*[─━]{4,}\s*$')
LINK_LINE_RE = re.compile(r'^(?P<label>[^:]{2,40}):\s*(?P<url>https?://\S+)\s*$')
URL_RE = re.compile(r'(https?://[^\s<]+)')


def plain(text):
    """Ondoa alama za WhatsApp (kwa kichwa cha email)."""
    return re.sub(r'[*_]', '', text or '').strip()


def _inline(text):
    out = escape(text)
    out = re.sub(r'\*([^*\n]+)\*', r'<b>\1</b>', out)
    out = re.sub(r'(?<![\w/])_([^_\n]+)_(?![\w/])', r'<i>\1</i>', out)
    return URL_RE.sub(r'<a href="\1" style="color:#2563eb">\1</a>', out)


def blocks(text):
    """Gawa ripoti kuwa vipande: title, subtitle, section, item, para, quote, button."""
    lines = (text or '').strip('\n').splitlines()
    result, quote = [], None
    for i, line in enumerate(lines):
        if RULE_RE.match(line):
            if quote is None:
                quote = []
            else:
                result.append({'kind': 'quote', 'html': _inline('\n'.join(quote)).replace('\n', '<br>')})
                quote = None
            continue
        if quote is not None:
            quote.append(line)
            continue
        if not line.strip():
            continue
        if i == 0:
            result.append({'kind': 'title', 'text': plain(line)})
            continue
        stripped = line.strip()
        if stripped.startswith('_') and stripped.endswith('_') and len(stripped) > 2:
            result.append({'kind': 'subtitle', 'text': stripped.strip('_')})
            continue
        m = LINK_LINE_RE.match(stripped)
        if m:
            result.append({'kind': 'button', 'label': m['label'], 'url': m['url']})
            continue
        m = SECTION_RE.match(stripped)
        if m:
            result.append({'kind': 'section', 'icon': m['icon'], 'title': m['title'].rstrip(':'),
                           'html': _inline(m['rest']) if m['rest'] else ''})
            continue
        m = ITEM_RE.match(line)
        if m:
            result.append({'kind': 'item', 'html': _inline(m['body'])})
            continue
        result.append({'kind': 'para', 'html': _inline(stripped)})
    if quote:
        result.append({'kind': 'quote', 'html': _inline('\n'.join(quote)).replace('\n', '<br>')})
    return result


def owner_email():
    return (os.getenv('ALERT_EMAIL', '') or os.getenv('EMAIL_HOST_USER', '')).strip()


def send(text):
    """Tuma ripoti kwa email ya mmiliki. Rudisha True ikifanikiwa."""
    to = owner_email()
    if not to:
        return False
    parts = blocks(text)
    title = next((b['text'] for b in parts if b['kind'] == 'title'), 'Ripoti ya timu')
    subtitle = next((b['text'] for b in parts if b['kind'] == 'subtitle'), '')
    subject = f'{title} · {subtitle}' if subtitle else title
    html = render_to_string('emails/ripoti.html', {'subject': subject, 'blocks': parts})
    try:
        msg = EmailMultiAlternatives(
            subject=subject[:150], body=plain(text),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'JamiiTek <info@jamiitek.com>'),
            to=[to])
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.warning('[wafanyakazi] ripoti email: %s', exc)
        return False
