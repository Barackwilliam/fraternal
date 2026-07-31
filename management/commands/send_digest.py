"""
Muhtasari wa asubuhi.

    python manage.py send_digest
    python manage.py send_digest --print

Endesha mara moja kwa siku, saa 1 asubuhi (04:00 UTC).
"""
from django.core.management.base import BaseCommand

from apps import digest


class Command(BaseCommand):
    help = 'Tuma muhtasari wa asubuhi.'

    def add_arguments(self, parser):
        parser.add_argument('--print', action='store_true',
                            dest='show', help='Onyesha bila kutuma.')

    def handle(self, *args, **opts):
        text = digest.build()
        if opts['show']:
            self.stdout.write(text)
            return
        sent = digest.send()
        self.stdout.write(self.style.SUCCESS(f'Imetumwa kwa backends {sent}.')
                          if sent else
                          self.style.WARNING('Hakuna backend iliyowekwa.'))
