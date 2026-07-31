"""
Vuta data halisi kutoka providers wote.

    python manage.py sync_integrations
    python manage.py sync_integrations --website 3
    python manage.py sync_integrations --provider render

Endesha kila dakika 15 kupitia cron-job.org (bure) ikipiga endpoint
ya /manage/cron/sync/ yenye token, au Render Cron ukiwa nayo.

Integration moja ikishindwa, nyingine zinaendelea. Kosa linahifadhiwa
kwenye sync_error na UI inarudi kwenye data ya nyuma.
"""
import time

from django.core.management.base import BaseCommand

from apps.crypto import encryption_available
from apps.models import Integration

PAUSE = 0.4   # kuepuka rate limits


class Command(BaseCommand):
    help = 'Sync integrations zote zilizo hai.'

    def add_arguments(self, parser):
        parser.add_argument('--website', type=int, default=None)
        parser.add_argument('--provider', type=str, default=None)
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **opts):
        if not encryption_available():
            self.stderr.write(self.style.ERROR(
                'FERNET_KEY haijawekwa — credentials haziwezi kusomwa. Sync imesimama.'))
            return

        qs = Integration.objects.filter(
            is_active=True,
            website__status__in=['active', 'maintenance'],
        ).select_related('website')

        if opts['website']:
            qs = qs.filter(website_id=opts['website'])
        if opts['provider']:
            qs = qs.filter(provider=opts['provider'])

        ok = failed = 0
        for integ in qs:
            if integ.sync():
                ok += 1
                if not opts['quiet']:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✓ {integ.website.name} · {integ.provider}'))
            else:
                failed += 1
                self.stdout.write(self.style.WARNING(
                    f'  ✗ {integ.website.name} · {integ.provider} — {integ.sync_error[:80]}'))
            time.sleep(PAUSE)

        self.stdout.write(f'\nZimefanikiwa: {ok} · Zimeshindwa: {failed}')
