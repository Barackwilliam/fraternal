"""
Kutuma taarifa — Telegram au WhatsApp (Green API).

Backend inachaguliwa na environment. Telegram ni bure kabisa bila kikomo;
Green API ina kikomo kwenye free tier. Weka moja au zote mbili.

    TELEGRAM_BOT_TOKEN=...
    TELEGRAM_CHAT_ID=...

    GREEN_API_ID=...
    GREEN_API_TOKEN=...
    GREEN_API_RECIPIENT=255XXXXXXXXX@c.us

Function moja tu inatumika popote: `notify(text)`. Kubadilisha backend
hakuhitaji kugusa code nyingine yoyote.
"""
import logging
import os

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 15


def _telegram(text):
    token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    if not token or not chat:
        return False
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat, 'text': text,
                  'parse_mode': 'HTML', 'disable_web_page_preview': True},
            timeout=TIMEOUT)
        return r.status_code == 200
    except Exception as e:
        logger.warning('Telegram imeshindikana: %s', type(e).__name__)
        return False


def _green_api(text):
    idi = os.getenv('GREEN_API_ID', '').strip()
    token = os.getenv('GREEN_API_TOKEN', '').strip()
    to = os.getenv('GREEN_API_RECIPIENT', '').strip()
    if not (idi and token and to):
        return False
    try:
        r = requests.post(
            f'https://api.green-api.com/waInstance{idi}/sendMessage/{token}',
            json={'chatId': to, 'message': _strip_html(text)},
            timeout=TIMEOUT)
        return r.status_code == 200
    except Exception as e:
        logger.warning('Green API imeshindikana: %s', type(e).__name__)
        return False


def _strip_html(text):
    import re
    text = re.sub(r'<b>(.*?)</b>', r'*\1*', text, flags=re.S)
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text, flags=re.S)
    return re.sub(r'<[^>]+>', '', text)


def _email(text):
    """
    Email kwa mmiliki.

    Telegram na Green API zinahitaji usanidi wa ziada. Email inafanya
    kazi tayari (Brevo), kwa hiyo hii ndiyo backend ya uhakika — na
    taarifa isiyofika si taarifa.

    ALERT_EMAIL ikiwekwa, inatumika. Vinginevyo EMAIL_HOST_USER.
    """
    to = (os.getenv('ALERT_EMAIL', '') or os.getenv('EMAIL_HOST_USER', '')).strip()
    if not to:
        return False
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        body = _strip_html(text)
        subject = body.splitlines()[0][:120] if body.strip() else 'Taarifa ya JamiiTek'
        send_mail(f'[JamiiTek] {subject}', body,
                  getattr(settings, 'DEFAULT_FROM_EMAIL', to), [to],
                  fail_silently=False)
        return True
    except Exception as e:
        logger.warning('notify email: %s', e)
        return False


BACKENDS = [_telegram, _green_api, _email]


def notify(text):
    """
    Tuma kwa backends zote zilizowekwa.
    Rudisha idadi iliyofanikiwa. Kamwe haitupi exception.
    """
    sent = 0
    for backend in BACKENDS:
        try:
            if backend(text):
                sent += 1
        except Exception as e:
            logger.warning('notify backend: %s', type(e).__name__)
    if not sent:
        logger.info('Hakuna backend ya taarifa iliyowekwa — ujumbe umerukwa.')
    return sent


def is_configured():
    return bool(
        (os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'))
        or (os.getenv('GREEN_API_ID') and os.getenv('GREEN_API_TOKEN'))
        or os.getenv('ALERT_EMAIL')
        or os.getenv('EMAIL_HOST_USER')
    )
