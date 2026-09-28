"""Simamia webhook ya Brevo bila kuingia kwenye dashboard yao.

Kwa nini command hii ipo: sehemu ya webhooks kwenye Brevo si rahisi
kuipata — iko chini ya Transactional > Email > Settings > Webhook, si
kwenye Settings za akaunti, na UI yao hubadilika. API haibadiliki.

    python manage.py brevo_webhook --list       # angalia zilizopo
    python manage.py brevo_webhook --create     # unda mpya
    python manage.py brevo_webhook --delete 42  # futa

Baada ya kuunda, tuma barua moja ya majaribio kisha fungua
/manage/emails/. Hali ikibadilika kutoka "Imetumwa" kwenda "Imefika",
kila kitu kiko sawa.
"""
import json
import os

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

API = 'https://api.brevo.com/v3/webhooks'

# Matukio yote tunayoyashughulikia kwenye apps/email_webhook.py
EVENTS = ['request', 'delivered', 'hardBounce', 'softBounce', 'blocked',
          'spam', 'invalid', 'deferred', 'click', 'opened', 'uniqueOpened']


class Command(BaseCommand):
    help = 'Unda, orodhesha au futa webhook ya Brevo inayofuatilia barua'

    def add_arguments(self, parser):
        parser.add_argument('--create', action='store_true')
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--delete', type=int, metavar='ID')
        parser.add_argument('--url', default='', help='Badilisha URL (si lazima)')

    def handle(self, *args, **opts):
        key = getattr(settings, 'BREVO_API_KEY', '') or os.getenv('BREVO_API_KEY', '')
        if not key:
            self.stderr.write(self.style.ERROR(
                'BREVO_API_KEY haijawekwa. Iweke kwenye .env au Render.'))
            return
        headers = {'api-key': key, 'content-type': 'application/json',
                   'accept': 'application/json'}

        if opts['delete']:
            r = requests.delete(f"{API}/{opts['delete']}", headers=headers, timeout=20)
            self.stdout.write(self.style.SUCCESS(f"Imefutwa ({r.status_code})")
                              if r.status_code in (200, 204)
                              else self.style.ERROR(f'{r.status_code}: {r.text[:200]}'))
            return

        if opts['create']:
            token = os.getenv('BREVO_WEBHOOK_TOKEN', '')
            if not token:
                self.stderr.write(self.style.WARNING(
                    'BREVO_WEBHOOK_TOKEN haijawekwa — webhook itakuwa wazi kwa yeyote.\n'
                    'Tengeneza: python -c "import secrets; print(secrets.token_urlsafe(24))"'))
            base = (getattr(settings, 'SITE_URL', '') or 'https://www.jamiitek.com').rstrip('/')
            url = opts['url'] or f'{base}/webhooks/brevo/' + (f'?token={token}' if token else '')

            payload = {'type': 'transactional', 'url': url, 'events': EVENTS,
                       'description': 'JamiiTek — email delivery tracking'}
            r = requests.post(API, headers=headers, data=json.dumps(payload), timeout=20)
            if r.status_code in (200, 201):
                self.stdout.write(self.style.SUCCESS(f'Webhook imeundwa: {r.json()}'))
                self.stdout.write(f'  URL: {url}')
                self.stdout.write('  Sasa tuma barua ya majaribio na uangalie /manage/emails/')
            else:
                self.stderr.write(self.style.ERROR(f'{r.status_code}: {r.text[:400]}'))
            return

        # --list ndiyo chaguo-msingi
        r = requests.get(f'{API}?type=transactional', headers=headers, timeout=20)
        if r.status_code != 200:
            self.stderr.write(self.style.ERROR(f'{r.status_code}: {r.text[:300]}'))
            return
        hooks = (r.json() or {}).get('webhooks', [])
        if not hooks:
            self.stdout.write(self.style.WARNING(
                'Hakuna webhook ya transactional. Endesha: '
                'python manage.py brevo_webhook --create'))
            return
        for h in hooks:
            self.stdout.write(self.style.SUCCESS(f"  #{h.get('id')}  {h.get('url')}"))
            self.stdout.write(f"      matukio: {', '.join(h.get('events', []))}")
