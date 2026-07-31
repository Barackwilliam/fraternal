"""
Angalia kama environment iko tayari kwa integrations.

    python manage.py check_env

Inaonyesha kila kitu kinachohitajika na kilichokosekana, pamoja na
namna ya kukirekebisha.
"""
import os

from django.core.management.base import BaseCommand

from apps.crypto import diagnose


class Command(BaseCommand):
    help = 'Thibitisha environment ya integrations.'

    def handle(self, *args, **opts):
        ok = self.style.SUCCESS
        bad = self.style.ERROR
        warn = self.style.WARNING

        self.stdout.write('')

        # ── FERNET_KEY (lazima) ──
        good, msg = diagnose()
        if good:
            self.stdout.write(ok(f'  ✓ FERNET_KEY        {msg}'))
        else:
            self.stdout.write(bad(f'  ✗ FERNET_KEY        {msg}'))
            self.stdout.write(
                '\n    Tengeneza:\n'
                '      python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"\n'
                '\n    Weka kwenye .env:\n'
                '      FERNET_KEY=<matokeo>\n'
                '\n    Kisha ANZISHA UPYA server. Django haisomi .env mpya '
                'bila kuanza upya.\n')

        # ── CRON_TOKEN ──
        if os.getenv('CRON_TOKEN', '').strip():
            self.stdout.write(ok('  ✓ CRON_TOKEN        imewekwa'))
        else:
            self.stdout.write(warn(
                '  ○ CRON_TOKEN        haipo — /cron/sync/ imezimwa '
                '(sync ya mkono bado inafanya kazi)'))

        # ── Taarifa ──
        tg = bool(os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
                  and os.getenv('TELEGRAM_CHAT_ID', '').strip())
        gr = bool(os.getenv('GREEN_API_ID', '').strip()
                  and os.getenv('GREEN_API_TOKEN', '').strip())
        if tg or gr:
            which = ' + '.join(filter(None, ['Telegram' if tg else '',
                                             'Green API' if gr else '']))
            self.stdout.write(ok(f'  ✓ Taarifa           {which}'))
        else:
            self.stdout.write(warn(
                '  ○ Taarifa           haipo — alerts hazitatumwa'))

        # ── Groq ──
        if os.getenv('GROQ_API_KEY', '').strip():
            self.stdout.write(ok('  ✓ GROQ_API_KEY      imewekwa'))
        else:
            self.stdout.write(warn(
                '  ○ GROQ_API_KEY      haipo — digest itatumia '
                'muhtasari wa kawaida'))

        # ── Libraries ──
        self.stdout.write('')
        for mod, why in [('cryptography', 'encryption'),
                         ('requests', 'providers'),
                         ('reportlab', 'ripoti ya PDF'),
                         ('psycopg2', 'metrics za Supabase')]:
            try:
                __import__(mod)
                self.stdout.write(ok(f'  ✓ {mod:16} {why}'))
            except ImportError:
                self.stdout.write(bad(f'  ✗ {mod:16} {why} — pip install {mod}'))

        # ── Hali ya integrations ──
        from apps.models import Integration
        total = Integration.objects.count()
        broken = Integration.objects.exclude(sync_error='').count()
        self.stdout.write('')
        self.stdout.write(f'  Integrations: {total} · zenye kosa: {broken}')
        for i in Integration.objects.exclude(sync_error='')[:5]:
            self.stdout.write(bad(
                f'    ✗ {i.website.name} · {i.provider} — {i.sync_error[:70]}'))
        self.stdout.write('')