"""
Ripoti ya PDF ya mwezi kwa mteja.

    python manage.py monthly_report --website 3
    python manage.py monthly_report --all
    python manage.py monthly_report --all --month 2026-07 --out /tmp/reports
"""
import os
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps import reports
from apps.models import ManagedWebsite


class Command(BaseCommand):
    help = 'Tengeneza ripoti ya PDF ya mwezi.'

    def add_arguments(self, parser):
        parser.add_argument('--website', type=int)
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--month', type=str, help='YYYY-MM')
        parser.add_argument('--out', type=str, default='reports')

    def handle(self, *args, **opts):
        when = None
        if opts['month']:
            try:
                y, m = opts['month'].split('-')
                when = date(int(y), int(m), 1)
            except ValueError:
                raise CommandError('--month iwe YYYY-MM')

        if opts['website']:
            sites = ManagedWebsite.objects.filter(pk=opts['website'])
        elif opts['all']:
            sites = ManagedWebsite.objects.filter(status='active')
        else:
            raise CommandError('Weka --website au --all')

        os.makedirs(opts['out'], exist_ok=True)
        for w in sites.select_related('client'):
            try:
                pdf = reports.build_pdf(w, when)
            except Exception as e:
                self.stderr.write(self.style.ERROR(
                    f'  ✗ {w.name}: {type(e).__name__}: {e}'))
                continue
            path = os.path.join(opts['out'], reports.filename(w, when))
            with open(path, 'wb') as f:
                f.write(pdf)
            self.stdout.write(self.style.SUCCESS(
                f'  ✓ {path} ({len(pdf):,} bytes)'))
