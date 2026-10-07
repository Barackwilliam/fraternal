"""
Ibrahimu — Mhudumu wa wateja.

Anafanya kazi juu ya JamiiBot ya JamiiTek yenyewe (bot zenye business_name
"JamiiTek", au zilizotajwa kwa WORKERS_BOT_IDS):

  • Wateja waliokabidhiwa binadamu na bado wanasubiri → kazi ya haraka
  • Maswali ambayo bot haikuyajua → rasimu ya jibu; ukikubali inakuwa FAQ
  • Wateja wanaouliza bei / wanaotaka kununua → anamkabidhi Selvester
"""
import os
import re
from datetime import timedelta

from .board import found, settle, site
from .team import signature

SLUG = 'ibrahimu'
HANDOFF_WAIT = timedelta(minutes=30)
GAPS_PER_RUN = 6

BUYING = re.compile(
    r'\b(bei|gharama|kiasi gani|shilingi ngapi|ngapi|nataka|nahitaji|kununua|nunua|kulipia|lipia|'
    r'kifurushi|package|price|cost|how much|order|quotation|quote)\b', re.I)


def bots():
    from apps.chatbot.models import BotConfig

    ids = [i.strip() for i in os.getenv('WORKERS_BOT_IDS', '').split(',') if i.strip()]
    if ids:
        return BotConfig.objects.filter(pk__in=ids)
    return BotConfig.objects.filter(business_name__icontains='jamiitek')


def _who(conv):
    return conv.customer_name or conv.wa_contact_name or conv.customer_phone


def _handoffs(now, bot_qs):
    from apps.chatbot.models import Conversation

    seen = []
    qs = Conversation.objects.filter(bot__in=bot_qs, is_human_handoff=True,
                                     handoff_at__lte=now - HANDOFF_WAIT).select_related('bot')
    for conv in qs[:30]:
        key = f'ibra:handoff:{conv.pk}:{conv.handoff_count}'
        seen.append(key)
        minutes = int((now - conv.handoff_at).total_seconds() // 60)
        wait = f'saa {minutes // 60}' if minutes >= 120 else f'dakika {minutes}'
        found(SLUG, key, f'{_who(conv)} anasubiri kuhudumiwa na binadamu ({wait})',
              ref=f'conv:{conv.pk}', priority=1,
              detail=conv.handoff_reason or conv.get_handoff_by_display(),
              link=site(f'/manage/chatbot/bots/{conv.bot_id}/'),
              recipient_name=_who(conv), recipient_phone=conv.customer_phone)
    settle(SLUG, 'ibra:handoff:', seen, 'Mteja amehudumiwa — bot imerudi kazini.')
    return len(seen)


def _gaps(now, bot_qs):
    from apps.chatbot import knowledge
    from apps.chatbot.models import KnowledgeGap

    seen, made = [], 0
    qs = (KnowledgeGap.objects.filter(bot__in=bot_qs, status__in=['open', 'drafted'],
                                      last_asked_at__gte=now - timedelta(days=30))
          .select_related('bot').order_by('-times_asked', '-last_asked_at'))
    for gap in qs[:40]:
        key = f'ibra:gap:{gap.pk}'
        seen.append(key)
        if made >= GAPS_PER_RUN:
            from .models import Kazi
            if not Kazi.objects.filter(key=key).exists():
                continue

        def draft(gap=gap):
            answer = gap.suggested_answer or knowledge.draft_answer(gap.bot, gap)
            if answer and not gap.suggested_answer:
                gap.suggested_answer = answer
                gap.status = 'drafted'
                gap.save(update_fields=['suggested_answer', 'status'])
            return answer

        times = f' (mara {gap.times_asked})' if gap.times_asked > 1 else ''
        _, created = found(SLUG, key, f'Bot haikujua: "{gap.question[:120]}"{times}',
                           draft=draft, ref=f'gap:{gap.pk}',
                           priority=1 if gap.times_asked >= 3 else 2,
                           detail=f'Bot ilijibu: {gap.bot_reply[:400]}' if gap.bot_reply else '',
                           link=site(f'/admin/chatbot/knowledgegap/{gap.pk}/change/'),
                           channel='faq')
        made += created
    settle(SLUG, 'ibra:gap:', seen, 'Swali limejibiwa au kuachwa.')
    return len(seen)


def _buyers(now, bot_qs):
    """Wateja wa siku 2 zilizopita walioonyesha nia ya kununua → kazi ya Selvester."""
    from apps.chatbot.models import Conversation, Message

    week = now.isocalendar()
    count = 0
    convs = (Conversation.objects.filter(bot__in=bot_qs, last_message_at__gte=now - timedelta(days=2))
             .order_by('-last_message_at')[:60])
    for conv in convs:
        said = list(Message.objects.filter(conversation=conv, role='user',
                                           created_at__gte=now - timedelta(days=2))
                    .order_by('-created_at').values_list('content', flat=True)[:8])
        hits = [m for m in said if BUYING.search(m or '')]
        if not hits:
            continue
        key = f'selv:chat:{conv.pk}:{week[0]}w{week[1]}'
        name = _who(conv)
        quote = ' | '.join(h[:160] for h in reversed(hits[:3]))

        def draft(name=name, quote=quote):
            from . import ai
            from .team import member
            who = member('selvester')
            body = ai.write(
                ai.persona(who['name'], who['role']),
                f"Mteja {name} aliandika kwenye JamiiBot ya JamiiTek: \"{quote}\". "
                "Andika ujumbe mfupi wa WhatsApp (sentensi 2-4) wa kumfuatilia kibinadamu, "
                "ukimwalika kuendelea na mazungumzo au simu. Usibuni bei.",
                max_tokens=220) or (
                f"Habari {name}, ni Selvester kutoka JamiiTek. Nimeona uliuliza kuhusu huduma zetu "
                "— ningependa kukusaidia moja kwa moja. Una muda wa kuzungumza leo?")
            return f"{body}\n\n— {signature('selvester').splitlines()[0]}, JamiiTek"

        _, created = found('selvester', key, f'Mteja wa JamiiBot ana nia ya kununua: {name}',
                           draft=draft, ref=f'conv:{conv.pk}', priority=1,
                           detail=f'Kutoka kwa Ibrahimu. Aliandika: {quote}',
                           link=site(f'/manage/chatbot/bots/{conv.bot_id}/'),
                           channel='whatsapp', recipient_name=name,
                           recipient_phone=conv.customer_phone)
        count += created
    return count


def run(now):
    bot_qs = bots()
    if not bot_qs.exists():
        return {'detail': 'hakuna JamiiBot ya JamiiTek (weka WORKERS_BOT_IDS)'}
    return {
        'handoffs': _handoffs(now, bot_qs),
        'gaps': _gaps(now, bot_qs),
        'buyers_to_selvester': _buyers(now, bot_qs),
    }
