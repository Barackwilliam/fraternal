"""
Email backend inayotuma kupitia HTTPS badala ya SMTP.

KWA NINI

Render inazuia outbound traffic kwenda ports 25, 465 na 587 kwenye free
web services (tangu 26 Sep 2025). Muunganisho hauzuiliwi kwa kukataliwa
— unaachwa ukisubiri, hadi gunicorn inaua worker:

    File "smtplib.py", line 312, in _get_socket
        return socket.create_connection((host, port), timeout, ...)
    ...
    Worker (pid:79) was sent SIGKILL!

Port 443 haiwezi kuzuiliwa — server ingeshindwa kufanya kazi kabisa.
Kwa hiyo tunatuma kupitia REST API ya Brevo badala ya SMTP.

INAFANYA KAZI NA CODE ILIYOPO BILA KUBADILISHWA

Hii ni `BaseEmailBackend` kamili. `send_mail()`, `EmailMessage` na
`EmailMultiAlternatives` zote zinaendelea kufanya kazi kama kawaida —
`apps/utils/email_notifications.py` inatumia HTML alternative, na hiyo
inashughulikiwa.

KUSANIDI

    BREVO_API_KEY   = <kutoka app.brevo.com > SMTP & API > API Keys>
    EMAIL_HOST_USER = info@jamiitek.com   (lazima iwe imethibitishwa Brevo)

Brevo free: email 300 kwa siku. Sender lazima ithibitishwe —
Senders > Add a sender, kisha bonyeza kiungo kilichotumwa.
"""
import logging

import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

logger = logging.getLogger('jamiitek.email')

BREVO_URL = 'https://api.brevo.com/v3/smtp/email'
TIMEOUT = 20


class BrevoEmailBackend(BaseEmailBackend):
    """Inatuma kila EmailMessage kupitia HTTPS."""

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = getattr(settings, 'BREVO_API_KEY', '') or ''
        self.default_from = (
            getattr(settings, 'DEFAULT_FROM_EMAIL', '')
            or getattr(settings, 'EMAIL_HOST_USER', '')
            or 'info@jamiitek.com'
        )

    # ── Visaidizi ─────────────────────────────────────────────

    @staticmethod
    def _split(addr):
        """
        "JamiiTek <info@jamiitek.com>" -> {'name': 'JamiiTek', 'email': '...'}
        Brevo inadai muundo huu; Django inatumia maandishi.
        """
        addr = (addr or '').strip()
        if '<' in addr and addr.endswith('>'):
            name, email = addr.rsplit('<', 1)
            return {'name': name.strip().strip('"'), 'email': email[:-1].strip()}
        return {'email': addr}

    @staticmethod
    def _bodies(message):
        """
        Inarudisha (maandishi, html).

        `EmailMultiAlternatives` inaweka HTML kwenye `alternatives`, si
        kwenye `body`. Bila kuiangalia, email za onyo za wateja
        zingetoka bila muundo wowote.
        """
        text = message.body or ''
        html = ''
        for content, mimetype in getattr(message, 'alternatives', []) or []:
            if mimetype == 'text/html':
                html = content
                break
        if getattr(message, 'content_subtype', '') == 'html':
            html, text = text, ''
        return text, html

    # ── API ya Django ─────────────────────────────────────────

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.api_key:
            logger.error('BREVO_API_KEY haijawekwa — hakuna email itakayotoka')
            if not self.fail_silently:
                raise ValueError('BREVO_API_KEY haijawekwa')
            return 0

        sent = 0
        for message in email_messages:
            if self._send_one(message):
                sent += 1
        return sent

    def _send_one(self, message):
        recipients = list(message.to or [])
        if not recipients:
            return False

        text, html = self._bodies(message)

        payload = {
            'sender': self._split(message.from_email or self.default_from),
            'to': [{'email': a} for a in recipients],
            'subject': message.subject or '(hakuna kichwa)',
        }
        if html:
            payload['htmlContent'] = html
            if text:
                payload['textContent'] = text
        else:
            # Brevo inadai mojawapo. Maandishi matupu yanakataliwa.
            payload['textContent'] = text or ' '

        if message.cc:
            payload['cc'] = [{'email': a} for a in message.cc]
        if message.bcc:
            payload['bcc'] = [{'email': a} for a in message.bcc]
        if message.reply_to:
            payload['replyTo'] = self._split(message.reply_to[0])

        try:
            resp = requests.post(
                BREVO_URL,
                headers={
                    'api-key': self.api_key,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                json=payload,
                timeout=TIMEOUT,
            )
        except requests.RequestException as e:
            logger.error('Brevo: muunganisho umeshindwa — %s', e)
            if not self.fail_silently:
                raise
            return False

        if resp.status_code in (200, 201, 202):
            logger.info('Email imetumwa kwa %s: %s',
                        ', '.join(recipients), (message.subject or '')[:60])
            return True

        detail = resp.text[:300]
        logger.error('Brevo %s: %s', resp.status_code, detail)
        if not self.fail_silently:
            raise RuntimeError(f'Brevo imekataa ({resp.status_code}): {detail}')
        return False
