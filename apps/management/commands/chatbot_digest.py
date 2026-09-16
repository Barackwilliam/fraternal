"""
Muhtasari wa wiki kwa kila mmiliki wa bot, kupitia WhatsApp.

KWA NINI WHATSAPP NA SI EMAIL AU DASHBOARD

Mmiliki wa duka la Kariakoo hatafungua dashboard Jumapili jioni.
Lakini atasoma WhatsApp. Mapungufu yakikusanyika na hakuna
anayeyaona, mfumo wote wa kujifunza hauna maana — bot itabaki
ikishindwa kujibu swali lile lile kila wiki.

Muhtasari huu ndio unaomrudisha kwenye ukurasa wa maarifa.

Inaendeshwa na DailyTasksMiddleware kila siku 7. Hakuna cron ya nje.
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger('chatbot.digest')


class Command(BaseCommand):
    help = "Tuma muhtasari wa wiki kwa wamiliki wa bot"

    def add_arguments(self, parser):
        parser.add_argument('--bot', help='session_name ya bot moja')
        parser.add_argument('--days', type=int, default=7)
        parser.add_argument('--dry', action='store_true', help='onyesha tu, usitume')
        parser.add_argument('--quiet', action='store_true')

    def handle(self, *args, **opts):
        from apps.chatbot.models import BotConfig
        from apps.chatbot import bridge

        quiet = opts['quiet']
        days = opts['days']
        since = timezone.now() - timedelta(days=days)

        bots = BotConfig.objects.filter(is_active=True, status='active')
        if opts['bot']:
            bots = bots.filter(session_name=opts['bot'])

        if not opts['dry'] and not bridge.is_configured():
            if not quiet:
                self.stdout.write(self.style.WARNING('Bridge haijasanidiwa — imerukwa.'))
            return

        sent = skipped = 0

        for bot in bots.select_related('client'):
            text = self.build(bot, since, days)

            if not text:
                skipped += 1
                continue

            if opts['dry']:
                self.stdout.write(self.style.HTTP_INFO(f"\n── {bot.bot_name} ──"))
                self.stdout.write(text)
                sent += 1
                continue

            if not bot.owner_digits:
                skipped += 1
                continue

            # Muhtasari unatoka WhatsApp ya biashara yenyewe, kwenda
            # namba ya binafsi ya mmiliki
            handler = bridge.BaileysHandler(bot)
            res = handler.send_text(bot.owner_whatsapp, text)
            if res.get('success'):
                sent += 1
            else:
                skipped += 1
                logger.error('[%s] muhtasari haujatumwa: %s',
                             bot.session_name, res.get('error'))

        if not quiet:
            self.stdout.write(self.style.SUCCESS(
                f"Muhtasari: {sent} umetumwa, {skipped} umerukwa."))

    # ──────────────────────────────────────────────────────────

    def build(self, bot, since, days):
        """
        Inarudisha maandishi, au tupu kama hakuna cha kusema.

        Muhtasari usio na habari ni kelele. Bot isiyokuwa na
        mazungumzo wala mapungufu haistahili ujumbe — na mmiliki
        anayepokea "wiki hii: 0, 0, 0" ataacha kusoma.
        """
        convs = bot.conversations.filter(last_message_at__gte=since)
        new_convs = bot.conversations.filter(started_at__gte=since).count()
        msgs = _count_messages(bot, since)

        gaps = (bot.knowledge_gaps
                .filter(status__in=['open', 'drafted'])
                .order_by('-times_asked')[:5])
        gap_count = bot.knowledge_gaps.filter(status__in=['open', 'drafted']).count()

        waiting = bot.conversations.filter(is_human_handoff=True).count()
        answered = bot.knowledge_gaps.filter(status='answered').count()

        if not msgs and not gap_count and not waiting:
            return ''

        L = [f"📊 *{bot.bot_name}* — wiki iliyopita", ""]

        # Shughuli
        L.append(f"Mazungumzo mapya: *{new_convs}*")
        L.append(f"Jumbe: *{msgs}*")
        if convs.count():
            L.append(f"Wateja waliorudi: *{convs.count() - new_convs}*")
        L.append("")

        # Wanaosubiri — hii ndiyo ya dharura
        if waiting:
            worst = (bot.conversations
                     .filter(is_human_handoff=True, handoff_at__isnull=False)
                     .order_by('handoff_at').first())
            L.append(f"🙋 *Wateja {waiting} bado wanasubiri binadamu*")
            if worst:
                m = worst.handoff_waiting_minutes
                dur = (f"dakika {m}" if m < 60
                       else f"saa {m // 60}" if m < 1440
                       else f"siku {m // 1440}")
                who = worst.customer_name or worst.wa_contact_name or 'Mmoja'
                L.append(f"{who} amesubiri {dur}.")
            L.append("Andika `orodha` uone ni nani.")
            L.append("")

        # Mapungufu
        if gaps:
            L.append(f"❓ *Maswali {gap_count} bot haijui*")
            L.append("")
            for g in gaps:
                times = f" _(mara {g.times_asked})_" if g.times_asked > 1 else ""
                L.append(f"• {g.question[:90]}{times}")
            if gap_count > len(gaps):
                L.append(f"• _…na mengine {gap_count - len(gaps)}_")
            L.append("")
            L.append("Ukiyajibu mara moja, bot itayajua milele:")
            L.append(_portal_url())
            L.append("")
        elif answered:
            L.append(f"✅ Bot inajibu kila kitu. Umeshaifundisha majibu {answered}.")
            L.append("")

        L.append("_Muhtasari huu unakuja kila wiki._")
        return "\n".join(L)


def _count_messages(bot, since):
    from apps.chatbot.models import Message
    return Message.objects.filter(conversation__bot=bot, created_at__gte=since).count()


def _portal_url():
    """
    Portal ya chatbot iko `/chatbot/` kwenye tovuti kuu.

    NB: si `PORTAL_BASE_URL` — ile ni portal ya wateja wa tovuti
    (`/portal/`), kitu tofauti kabisa. Kuitumia kungetoa
    `/portal/chatbot/knowledge/` ambayo haipo.
    """
    from django.conf import settings
    base = (getattr(settings, 'SITE_URL', '') or 'https://jamiitek.com').rstrip('/')
    return f"{base}/chatbot/knowledge/"
