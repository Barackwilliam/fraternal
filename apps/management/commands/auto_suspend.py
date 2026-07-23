"""
Simamisha tovuti zote zilizofikia mwisho wa muda wa hosting.

Matumizi:
    python manage.py auto_suspend                # endesha kawaida
    python manage.py auto_suspend --dry-run      # onyesha tu, usibadilishe
    python manage.py auto_suspend --no-notify    # usitume email kwa wateja
"""
from django.core.management.base import BaseCommand

from apps import hosting_service


class Command(BaseCommand):
    help = 'Suspend websites whose hosting period has ended (with AI-written notices)'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help='Show what would happen without changing anything')
        parser.add_argument('--no-notify', action='store_true',
                            help='Do not email clients')

    def handle(self, *args, **opts):
        report = hosting_service.run_auto_suspend(
            dry_run=opts['dry_run'],
            notify=not opts['no_notify'],
        )
        text = hosting_service.format_report(report)

        if report.get('systemic_failure'):
            self.stdout.write(self.style.ERROR(text))
        elif report['suspended'] or report['maintenance']:
            self.stdout.write(self.style.SUCCESS(text))
        else:
            self.stdout.write(text)
