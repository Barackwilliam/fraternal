import json

from django.core.management.base import BaseCommand

from apps.wafanyakazi.runner import run_all


class Command(BaseCommand):
    help = 'Endesha timu ya wafanyakazi wa AI (William, Ibrahimu, Selvester, Grace, Diana).'

    def add_arguments(self, parser):
        parser.add_argument('--ripoti', choices=['asubuhi', 'jioni'],
                            help='Lazimisha ripoti ya William itumwe sasa')

    def handle(self, *args, **opts):
        result = run_all(force_report=opts.get('ripoti'))
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2, default=str))
