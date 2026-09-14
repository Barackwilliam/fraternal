"""
Kufuta app-state-sync-key za zamani kwenye jedwali `baileys_auth`.

Baileys inatengeneza funguo hizi mara kwa mara na hazifutwi zenyewe.
Zikikaa, jedwali linakua bila sababu na `keys.get()` inakuwa polepole.

Hii si kitendo cha dharura na haipaswi kuwa kitufe — hutakumbuka
kukibonyeza, na ukikumbuka utakuwa umechelewa. Inaendeshwa na
DailyTasksMiddleware kila siku 7, mtindo ule ule wa prune_snapshots.

Creds na funguo zinazotumika hazifutwi kamwe — LIKE inachuja
'app-state-sync-key-%' pekee.
"""
from django.core.management.base import BaseCommand

from apps.chatbot import bridge


class Command(BaseCommand):
    help = "Futa app-state-sync-key za Baileys zilizozeeka"

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30,
                            help='Umri wa chini wa funguo zitakazofutwa (default 30)')
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **opts):
        quiet = opts['quiet']

        if not bridge.is_configured():
            if not quiet:
                self.stdout.write(self.style.WARNING(
                    'Bridge haijasanidiwa (BRIDGE_URL / BRIDGE_API_KEY) — imerukwa.'))
            return

        result = bridge.prune_keys(days=opts['days'])

        if not result.get('success'):
            self.stderr.write(self.style.ERROR(
                f"Imeshindwa: {result.get('error', 'haijulikani')}"))
            return

        removed = result.get('removed', 0)
        if not quiet:
            self.stdout.write(self.style.SUCCESS(
                f"Funguo {removed} zimefutwa (zaidi ya siku {opts['days']})."))
