"""
Kuunganisha maswali yanayofanana kwenye KnowledgeGap.

`normalize()` inaunganisha maswali yanayofanana KABISA. Lakini
"mnafungua saa ngapi" na "mnafanya kazi mpaka saa ngapi" ni swali
moja kwa mteja, na mawili kwenye database — mmiliki anaona orodha
ndefu ya vitu vinavyorudiwa.

AI inayapanga. Yaliyounganishwa yanaondoka kwenye orodha na hesabu
zao zinahamia kwenye swali kuu, kwa hiyo mmiliki anaona "mara 9"
badala ya mara 3 mahali tatu — na anajua lipi la kujibu kwanza.

Inaendeshwa kabla ya muhtasari wa wiki, si baada — orodha inayotumwa
WhatsApp iwe tayari imesafishwa.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Unganisha maswali yanayofanana kwenye orodha ya mapungufu"

    def add_arguments(self, parser):
        parser.add_argument('--bot', help='session_name ya bot moja')
        parser.add_argument('--min', type=int, default=3,
                            help='Idadi ya chini ya mapungufu kabla ya kuunganisha')
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **opts):
        from apps.chatbot.models import BotConfig
        from apps.chatbot import knowledge

        bots = BotConfig.objects.filter(is_active=True, status='active')
        if opts['bot']:
            bots = bots.filter(session_name=opts['bot'])

        total = 0
        for bot in bots:
            open_count = bot.knowledge_gaps.filter(
                status__in=['open', 'drafted']).count()
            if open_count < opts['min']:
                continue
            merged = knowledge.cluster_gaps(bot)
            total += merged
            if merged and not opts['quiet']:
                self.stdout.write(f"  {bot.bot_name}: {merged} yameunganishwa")

        if not opts['quiet']:
            self.stdout.write(self.style.SUCCESS(
                f"Jumla: maswali {total} yameunganishwa."))
