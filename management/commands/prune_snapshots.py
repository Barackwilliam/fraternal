"""
Punguza snapshots za zamani.

Sync ya kila dakika 15 = snapshots ~2,900 kwa integration kwa mwezi.
Hii inakua haraka. Kanuni:

  • siku 7 za mwisho  → hifadhi zote (kwa uchunguzi wa matatizo)
  • siku 8–90         → hifadhi moja kwa saa
  • zaidi ya siku 90  → futa

Uptime ya siku 30 haiathiriki kwa sababu tunahifadhi zote za wiki moja
na moja kwa saa baada ya hapo.

    python manage.py prune_snapshots
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.models import IntegrationSnapshot


class Command(BaseCommand):
    help = 'Futa snapshots za zamani ili database isikue bila kikomo.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **opts):
        now = timezone.now()
        week, quarter = now - timedelta(days=7), now - timedelta(days=90)

        old = IntegrationSnapshot.objects.filter(checked_at__lt=quarter)
        n_old = old.count()

        mid = (IntegrationSnapshot.objects
               .filter(checked_at__gte=quarter, checked_at__lt=week)
               .order_by('integration_id', 'checked_at'))

        keep, drop, last = set(), [], {}
        for s in mid.iterator():
            bucket = (s.integration_id, s.checked_at.replace(
                minute=0, second=0, microsecond=0))
            if bucket in last:
                drop.append(s.pk)
            else:
                last[bucket] = s.pk
                keep.add(s.pk)

        self.stdout.write(f'  Zaidi ya siku 90 : {n_old:,} → futa')
        self.stdout.write(f'  Siku 8–90        : {len(drop):,} → futa, '
                          f'{len(keep):,} zinabaki (moja kwa saa)')

        if opts['dry_run']:
            self.stdout.write(self.style.WARNING('\n  (dry run — hakuna kilichofutwa)'))
            return

        old.delete()
        for i in range(0, len(drop), 1000):
            IntegrationSnapshot.objects.filter(pk__in=drop[i:i + 1000]).delete()

        total = IntegrationSnapshot.objects.count()
        self.stdout.write(self.style.SUCCESS(f'\n  Zimebaki: {total:,}'))
