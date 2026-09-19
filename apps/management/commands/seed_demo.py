"""
python manage.py seed_demo --email demo@jamiitek.com

Jaza bot moja na demo data (Zawadi Electronics): huduma, FAQ, mazungumzo,
na analytics za siku 7.

Bila --email/--username/--bot-id, inatumia bot pekee kama kuna moja tu;
vinginevyo inauliza uchague.

NB: Kwenye Render free tier huwezi kuendesha command hii kwa mkono —
tumia URL /chatbot/seed-demo/ ukiwa umeingia (staff au mmiliki wa bot).
"""
from django.core.management.base import BaseCommand, CommandError

from apps.chatbot.models import BotConfig, ChatbotClient
from apps.chatbot.demo_seed import seed_demo_bot


class Command(BaseCommand):
    help = 'Seed demo data (Zawadi Electronics) into a JamiiBot bot'

    def add_arguments(self, parser):
        parser.add_argument('--email', help='Email ya ChatbotClient mwenye bot')
        parser.add_argument('--username', help='Username ya mtumiaji mwenye bot')
        parser.add_argument('--bot-id', help='UUID ya bot moja kwa moja')

    def handle(self, *args, **opts):
        bot = None
        if opts.get('bot_id'):
            bot = BotConfig.objects.filter(id=opts['bot_id']).first()
        elif opts.get('email'):
            c = ChatbotClient.objects.filter(email=opts['email']).first()
            bot = c.bots.first() if c else None
        elif opts.get('username'):
            c = ChatbotClient.objects.filter(user__username=opts['username']).first()
            bot = c.bots.first() if c else None
        else:
            qs = BotConfig.objects.all()
            if qs.count() == 1:
                bot = qs.first()
            else:
                raise CommandError(
                    f'Kuna bot {qs.count()}. Tumia --email, --username au --bot-id kuchagua.'
                )

        if not bot:
            raise CommandError('Bot haipatikani kwa vigezo ulivyotoa.')

        self.stdout.write(f'Inajaza demo kwenye: {bot.bot_name} ({bot.id}) ...')
        summary = seed_demo_bot(bot)
        self.stdout.write(self.style.SUCCESS(
            f"Imekamilika — {summary['business']}: "
            f"huduma {summary['services']}, FAQ {summary['faqs']}, "
            f"mazungumzo {summary['conversations']}, jumbe {summary['messages']}, "
            f"analytics siku {summary['analytics_days']}."
        ))
