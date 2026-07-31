"""
Angalia matatizo na tuma alerts.

    python manage.py check_alerts
    python manage.py check_alerts --dry-run

Endesha kila dakika 30 (baada ya sync_integrations).
"""
from django.core.management.base import BaseCommand

from apps import alerts
from apps.notify import is_configured


class Command(BaseCommand):
    help = 'Angalia kanuni za alerts na tuma zilizogusa.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        dry = opts['dry_run']
        if not dry and not is_configured():
            self.stderr.write(self.style.WARNING(
                'Hakuna backend ya taarifa. Weka TELEGRAM_BOT_TOKEN au GREEN_API_ID.'))

        found = alerts.collect()
        sent = alerts.dispatch(found, dry_run=dry)

        colors = {'critical': self.style.ERROR,
                  'warning': self.style.WARNING,
                  'info': self.style.SUCCESS}
        for a in found:
            new = ' (imetumwa)' if a in sent else ' (imeshatumwa hivi karibuni)'
            self.stdout.write(colors[a.level](
                f'  [{a.level:8}] {a.website.name} — {a.title}{new}'))

        self.stdout.write(
            f'\nZimekutwa: {len(found)} · Zimetumwa: {len(sent)}'
            + (' (dry run)' if dry else ''))
