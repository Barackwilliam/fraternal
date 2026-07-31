"""
Ripoti ya hali ya uhamiaji: field zipi ni live, zipi bado za mkono.

    python manage.py integration_status
    python manage.py integration_status --missing

Tumia hii kabla ya kufuta static field yoyote. Field iondolewe tu
ikiwa imekuwa `live` kwa clients WOTE kwa angalau wiki mbili.
"""
from django.core.management.base import BaseCommand

from apps.live_config import live_config
from apps.models import ManagedWebsite

FIELDS = [
    'hosting_status', 'server_location', 'uptime_percent',
    'ssl_expiry_date', 'ssl_issuer', 'monthly_visits',
    'last_backup', 'db_size_display', 'media_display',
]

MARK = {'live': '●', 'cached': '◐', 'manual': '○', 'unknown': '·'}


class Command(BaseCommand):
    help = 'Onyesha chanzo cha kila field kwa kila project.'

    def add_arguments(self, parser):
        parser.add_argument('--missing', action='store_true',
                            help='Onyesha projects zisizo na integration pekee.')

    def handle(self, *args, **opts):
        websites = (ManagedWebsite.objects
                    .exclude(status='terminated')
                    .prefetch_related('integrations')
                    .order_by('name'))

        if opts['missing']:
            for w in websites:
                if not w.integrations.filter(is_active=True).exists():
                    self.stdout.write(f'  {w.name} — {w.client.name}')
            return

        self.stdout.write('\n  ● live   ◐ cached   ○ manual   · haipo\n')
        head = 'Project'.ljust(22) + ''.join(f[:9].ljust(11) for f in FIELDS)
        self.stdout.write(self.style.HTTP_INFO(head))

        totals = {f: {'live': 0, 'manual': 0} for f in FIELDS}
        for w in websites:
            cfg = live_config(w)
            row = w.name[:21].ljust(22)
            for f in FIELDS:
                getattr(cfg, f, None)
                src = cfg.source_of(f)
                row += MARK.get(src, '·').ljust(11)
                if src in ('live', 'cached'):
                    totals[f]['live'] += 1
                elif src == 'manual':
                    totals[f]['manual'] += 1
            self.stdout.write(row)

        self.stdout.write('\n  Tayari kufutwa (live kwa wote, hakuna manual):')
        ready = [f for f, t in totals.items()
                 if t['live'] and not t['manual']]
        if ready:
            for f in ready:
                self.stdout.write(self.style.SUCCESS(f'    ✓ {f}'))
        else:
            self.stdout.write('    (hakuna bado)')

        pending = [f for f, t in totals.items() if t['manual']]
        if pending:
            self.stdout.write('\n  Bado zina data ya mkono:')
            for f in pending:
                self.stdout.write(f'    ○ {f} — projects {totals[f]["manual"]}')
        self.stdout.write('')
