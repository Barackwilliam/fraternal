"""
JamiiTek Spotlight — makala 1 kuhusu JamiiTek (Jumatatu, Jumatano, Jumamosi).

    python manage.py jamiitek_spotlight            # inaandika tu kama leo ni siku yake
    python manage.py jamiitek_spotlight --force    # andika sasa hivi, siku yoyote
    python manage.py jamiitek_spotlight --list     # onyesha mada na mitazamo iliyotumika
    python manage.py jamiitek_spotlight --force --topic jamiibot

Kwa kawaida inaendeshwa na cron ya /tasks/news/ (ileile ya newsroom).
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'AI inaandika makala 1 maalum kuhusu JamiiTek (Jumatatu/Jumatano/Jumamosi)'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Andika hata kama leo si siku ya Spotlight')
        parser.add_argument('--topic', default=None, help='Lazimisha mada, mf. jamiibot, builder, service-3')
        parser.add_argument('--no-email', action='store_true', help='Usitume email ya kukagua')
        parser.add_argument('--list', action='store_true', help='Onyesha mada zote na zilizotumika')

    def handle(self, *args, **opts):
        from apps import spotlight_blog as sb

        if opts['list']:
            used = sb.used_keys()
            for key, (name, _facts) in sb.gather_topics().items():
                done = sorted(u.split(':', 1)[1] for u in used if u.split(':', 1)[0] == key)
                self.stdout.write(f'{key:22} {name}  —  used: {", ".join(done) or "none"}')
            return

        fn = sb.run if opts['no_email'] else sb.run_and_notify
        result = fn(force=opts['force'], topic=opts['topic'])
        if result['skipped']:
            self.stdout.write(f"Imerukwa: {result['skipped']}")
        for p in result['created']:
            self.stdout.write(self.style.SUCCESS(f'  ★ [{p.status}] {p.title}  ({p.source_name})'))
        for e in result['errors']:
            self.stdout.write(self.style.WARNING(f'  ! {e}'))
