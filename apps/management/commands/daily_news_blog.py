"""
AI Newsroom — kila siku inaandika RASIMU za habari kubwa (TZ + dunia).

    python manage.py daily_news_blog
    python manage.py daily_news_blog --count 3 --no-email

Inatengeneza BlogPost status='draft'. Baada ya kumaliza, inatuma email
kwa mmiliki kukumbusha kukagua na kuthibitisha. Endesha kwa cron/scheduler
au kupitia endpoint /tasks/news/?token=...
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'AI inaandika rasimu za habari kubwa za siku (Tanzania + kimataifa)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=None,
                            help='Rasimu ngapi za Tech & Business (default NEWSROOM_DAILY au 3)')
        parser.add_argument('--tz', type=int, default=None, help='(Mtindo wa zamani) habari za Tanzania')
        parser.add_argument('--world', type=int, default=None, help='(Mtindo wa zamani) habari za kimataifa')
        parser.add_argument('--no-email', action='store_true', help='Usitume email ya kukagua')

    def handle(self, *args, **opts):
        from apps import news_blog

        self.stdout.write('AI newsroom inaanza kukusanya na kuandika habari…')
        if opts['no_email']:
            result = news_blog.run(count=opts['count'], tz_count=opts['tz'], world_count=opts['world'])
        else:
            result = news_blog.run_and_notify(count=opts['count'], tz_count=opts['tz'], world_count=opts['world'])

        created = result['created']
        self.stdout.write(self.style.SUCCESS(
            f"Zimeandaliwa: {len(created)} · Zimerukwa: {result['skipped']} · "
            f"Hitilafu: {len(result['errors'])}"))
        for p in created:
            self.stdout.write(f'  • [{p.category.name if p.category else "—"}] {p.title}')
        for e in result['errors']:
            self.stdout.write(self.style.WARNING(f'  ! {e}'))

        return
