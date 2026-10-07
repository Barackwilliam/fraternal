"""
Daraja la wILife — msaidizi binafsi wa mmiliki.

JamiiTek  →  wILife   (POST {WILIFE_URL}/agent/jamiitek/)
    kind=report    ripoti ya William; wILife inakutumia kwa WhatsApp/email
    kind=approval  rasimu inayosubiri idhini; wILife inakupa "OK code",
                   ukijibu inaita API yetu (api_approve) kutuma

wILife  →  JamiiTek   (views.api_*)  — hali ya timu, idhinisha, kataa, endesha

Siri moja kwa pande zote mbili: WORKERS_API_TOKEN hapa = JAMIITEK_TOKEN kule,
kwenye header `X-Workers-Token`.

Kama WILIFE_URL haijawekwa, ripoti zinaenda kupitia apps.notify (Telegram /
Green API / email) kama taarifa nyingine za JamiiTek.
"""
import logging
import os
import re

import requests
from django.utils import timezone

from .team import member

logger = logging.getLogger(__name__)

TIMEOUT = 40   # wILife iko Render free — inaweza kuwa imelala


def token():
    return os.getenv('WORKERS_API_TOKEN', '').strip()


def url():
    return os.getenv('WILIFE_URL', '').strip().rstrip('/')


def is_configured():
    return bool(url() and token())


def _post(payload):
    try:
        r = requests.post(f'{url()}/agent/jamiitek/', json=payload, timeout=TIMEOUT,
                          headers={'X-Workers-Token': token()})
        if r.status_code != 200:
            logger.warning('[wafanyakazi] wILife %s: %s', r.status_code, r.text[:200])
            return None
        return r.json()
    except Exception as exc:
        logger.warning('[wafanyakazi] wILife haipatikani: %s', type(exc).__name__)
        return None


def _as_html(text):
    """WhatsApp markup → HTML ndogo ya apps.notify (Telegram)."""
    from html import escape
    return re.sub(r'\*([^*\n]+)\*', r'<b>\1</b>', escape(text))


def deliver_report(text):
    """Rudisha njia iliyotumika ('wilife', 'notify') au ''."""
    if is_configured() and _post({'kind': 'report', 'worker': 'william', 'text': text}):
        return 'wilife'
    # Bila wILife: email iliyopambwa + Telegram/Green API kama zimewekwa
    from apps import notify

    from . import ripoti_email
    used = []
    if ripoti_email.send(text):
        used.append('email')
    for backend in (notify._telegram, notify._green_api):
        try:
            if backend(_as_html(text)):
                used.append(backend.__name__.strip('_'))
        except Exception:
            pass
    return '+'.join(used)


def push_approval(kazi):
    """Omba idhini kupitia wILife. Rudisha True ikipokelewa."""
    if not is_configured():
        return False
    who = member(kazi.worker)
    to = kazi.recipient_email or kazi.recipient_phone
    data = _post({
        'kind': 'approval',
        'worker': kazi.worker,
        'task_id': kazi.pk,
        'title': kazi.title,
        'context': f"{who['name']} ({who['role']}) · {kazi.get_channel_display()}",
        'recipient_name': kazi.recipient_name,
        'recipient': to,
        'subject': kazi.subject,
        'body': kazi.draft,
    })
    if not data:
        return False
    kazi.pushed_at = timezone.now()
    kazi.wilife_code = str(data.get('code', ''))[:12]
    kazi.save(update_fields=['pushed_at', 'wilife_code', 'updated_at'])
    return True
