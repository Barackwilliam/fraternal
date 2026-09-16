"""
Handoff — mteja anapohitaji binadamu.

SHERIA MOJA INAYOONGOZA KILA KITU HAPA:
Bot ikishasimama kwa mazungumzo fulani, HAIJIBU TENA hata mara moja
mpaka mmiliki aseme irudi. Si "inajibu kwa upole", si "inakumbusha
kila baada ya muda" — inanyamaza kabisa.

Sababu: mteja ameambiwa "nakuunganisha na mtu halisi". Bot ikiendelea
kuandika baada ya hapo, ahadi ile inakuwa uongo, na mteja anajua
anazungumza na mashine iliyodai imeondoka.

Zamani `is_human_handoff = True` iliwekwa na hakuna kilichofuata:
hakuna aliyearifiwa, na ujumbe uliofuata ulipita kwenye AI kama
kawaida.

MMILIKI ANAZUNGUMZA NA BOT KWA WHATSAPP
Bot inatuma taarifa kwenye namba ya mmiliki kutoka WhatsApp ya
biashara. Mmiliki anajibu pale pale kwa amri:

    orodha              — mazungumzo yanayosubiri
    endelea 255712...   — bot irudi kwa mteja huyo
    endelea             — bot irudi kwa aliyesubiri muda mrefu zaidi
    simamisha 255712... — simamisha bot kwa mteja huyo
    msaada              — orodha ya amri

Hakuna app ya kupakua, hakuna ukurasa wa kufungua. Mmiliki wa duka
la Kariakoo hatatafuta dashboard akiwa kwenye foleni ya benki — lakini
atajibu WhatsApp.
"""
import logging
import re

from django.utils import timezone

logger = logging.getLogger('chatbot.handoff')


# ══════════════════════════════════════════════════════════════
#  KUTAMBUA
# ══════════════════════════════════════════════════════════════
# Maneno haya yalikuwa mara mbili — `views.py` na `ai_engine.py` —
# na orodha hizo mbili hazikulingana. Sasa ziko hapa pekee.

TRIGGERS = [
    # Kiswahili
    'binadamu', 'mtu halisi', 'mtu mwenyewe', 'mwambie mtu', 'nizungumze na mtu',
    'naomba kuongea na', 'nipigie', 'nipigie simu', 'piga simu', 'namba ya mmiliki',
    'muuzaji', 'meneja', 'mwenye duka', 'mwenye biashara', 'sitaki kuongea na robot',
    'wewe ni robot', 'wewe ni mashine',
    # Kiingereza
    'human', 'real person', 'real human', 'agent', 'operator', 'representative',
    'speak to someone', 'talk to someone', 'call me', 'customer service',
    'manager', 'not a bot', 'youre a bot', "you're a bot",
]

# Mteja aliyekasirika — hapa AI haipaswi kujaribu kutuliza, mtu ahitajika
FRUSTRATION = [
    'hujanielewa', 'haujanielewa', 'sijaelewa kabisa', 'unanichosha',
    'hii haisaidii', 'mnanicheza', 'nimechoka',
    'you dont understand', "you don't understand", 'this is useless',
    'not helpful', 'stop wasting my time',
]


def detect(text):
    """
    Inarudisha (inahitajika, sababu) au (False, '').

    Ni kulinganisha maneno tu — haraka, bure, na haiwezi kukosea kwa
    njia ya hatari. AI nayo inaweza kuomba handoff yenyewe ikishindwa;
    hiyo inapita kwenye `by='ai'`.
    """
    low = (text or '').lower()

    for kw in TRIGGERS:
        if kw in low:
            return True, f"Mteja aliomba binadamu ({kw})"

    for kw in FRUSTRATION:
        if kw in low:
            return True, f"Mteja amekasirika ({kw})"

    return False, ''


# ══════════════════════════════════════════════════════════════
#  AMRI ZA MMILIKI
# ══════════════════════════════════════════════════════════════

CMD_RESUME = ['endelea', 'rudi', 'resume', 'continue', 'maliza', 'done']
CMD_PAUSE  = ['simamisha', 'simama', 'pause', 'stop', 'shika']
CMD_LIST   = ['orodha', 'list', 'wanaosubiri', 'pending', 'nani']
CMD_HELP   = ['msaada', 'help', 'amri', 'commands']


def parse_command(text):
    """
    Inarudisha (amri, namba) au (None, None).

    Namba ni ya hiari — 'endelea' bila namba inamaanisha aliyesubiri
    muda mrefu zaidi.
    """
    low = (text or '').strip().lower()
    if not low:
        return None, None

    first = low.split()[0]
    phone = None

    m = re.search(r'(\+?\d[\d\s\-]{7,17})', low)
    if m:
        phone = re.sub(r'\D', '', m.group(1))

    if first in CMD_RESUME:
        return 'resume', phone
    if first in CMD_PAUSE:
        return 'pause', phone
    if first in CMD_LIST:
        return 'list', None
    if first in CMD_HELP:
        return 'help', None
    return None, None


HELP_TEXT = (
    "*Amri za bot*\n\n"
    "`orodha` — ona mazungumzo yanayosubiri\n"
    "`endelea` — bot irudi kwa aliyesubiri muda mrefu zaidi\n"
    "`endelea 255712345678` — bot irudi kwa mteja huyo\n"
    "`simamisha 255712345678` — simamisha bot kwa mteja huyo\n"
    "`msaada` — ujumbe huu"
)


def handle_owner_command(bot, wa, from_phone, text):
    """
    Inashughulikia ujumbe kutoka kwa mmiliki.

    Inarudisha True kama ujumbe ulikuwa amri (kwa hiyo usipite kwenye
    AI), au False kama ni mazungumzo ya kawaida.

    NB: mmiliki anaweza kuwa mteja wa bot yake mwenyewe. Ndiyo maana
    ujumbe usio amri unaachwa upite kama kawaida badala ya kuzuiwa.
    """
    from .models import Conversation

    cmd, phone = parse_command(text)
    if not cmd:
        return False

    if cmd == 'help':
        wa.send_text(from_phone, HELP_TEXT)
        return True

    waiting = (Conversation.objects
               .filter(bot=bot, is_human_handoff=True)
               .order_by('handoff_at'))

    if cmd == 'list':
        if not waiting.exists():
            wa.send_text(from_phone, "Hakuna mteja anayesubiri. Bot inashughulikia wote.")
            return True
        lines = [f"*Wanaosubiri ({waiting.count()})*", ""]
        for c in waiting[:10]:
            who = c.customer_name or c.wa_contact_name or 'Hajulikani'
            mins = c.handoff_waiting_minutes
            dur = f"dakika {mins}" if mins < 60 else f"saa {mins // 60}"
            lines.append(f"• *{who}* — {c.customer_phone}")
            lines.append(f"  amesubiri {dur} · {c.handoff_reason or 'hakuna sababu'}")
        lines.append("")
        lines.append("Andika `endelea <namba>` bot irudi.")
        wa.send_text(from_phone, "\n".join(lines))
        return True

    if cmd == 'resume':
        conv = _find(waiting, phone) if phone else waiting.first()
        if not conv:
            wa.send_text(from_phone,
                         f"Sijampata mteja {phone} anayesubiri." if phone
                         else "Hakuna mteja anayesubiri.")
            return True
        conv.resume_bot()
        who = conv.customer_name or conv.customer_phone
        wa.send_text(from_phone, f"Sawa. Bot imerudi kwa *{who}* ({conv.customer_phone}).")
        logger.info('[%s] handoff imemalizwa: %s', bot.session_name, conv.customer_phone)
        return True

    if cmd == 'pause':
        if not phone:
            wa.send_text(from_phone, "Andika namba: `simamisha 255712345678`")
            return True
        conv = Conversation.objects.filter(bot=bot).filter(
            customer_phone__endswith=phone[-9:]).first()
        if not conv:
            wa.send_text(from_phone, f"Sijampata mteja {phone}.")
            return True
        conv.start_handoff(by='owner', reason='Mmiliki alisimamisha')
        who = conv.customer_name or conv.customer_phone
        wa.send_text(from_phone,
                     f"Bot imesimama kwa *{who}*. Haitajibu mpaka useme `endelea {conv.customer_phone}`.")
        return True

    return False


def _find(qs, phone):
    """Namba zinakuja kwa maumbo tofauti (0712..., 255712..., +255712...)."""
    if not phone:
        return None
    tail = phone[-9:]
    return qs.filter(customer_phone__endswith=tail).first()


# ══════════════════════════════════════════════════════════════
#  KUANZISHA HANDOFF
# ══════════════════════════════════════════════════════════════

def trigger(bot, wa, conv, from_phone, by='customer', reason=''):
    """
    Simamisha bot, mwambie mteja, mjulishe mmiliki.

    Inarudisha True kama handoff mpya imeanza.
    """
    started = conv.start_handoff(by=by, reason=reason)
    if not started:
        return False   # tayari ilikuwa imesimama

    # 1. Mteja — ahadi tunayoitimiza kwa kunyamaza baada ya hapa
    msg = bot.human_handoff_msg or (
        "Nimekuunganisha na mtu halisi wa timu yetu. "
        "Atakujibu hapa hivi punde — usifunge mazungumzo haya."
    )
    _send(wa, conv, from_phone, msg)

    # 2. Mteja kuhitaji binadamu NI kushindwa kwa bot. Hifadhi swali
    #    lililomfikisha hapo — mara nyingi ndilo bot isilolijua.
    if by == 'customer':
        try:
            from . import knowledge
            last = conv.messages.filter(role='user').order_by('-created_at').first()
            if last:
                knowledge.record(bot, conv, last.content, source='handoff')
        except Exception:
            logger.exception('kuhifadhi pengo kumeshindwa')

    # 3. Mmiliki
    notify_owner(bot, wa, conv, reason)

    logger.info('[%s] handoff: %s (%s)', bot.session_name, from_phone, reason)
    return True


def notify_owner(bot, wa, conv, reason=''):
    """Taarifa kwenda namba ya mmiliki kupitia WhatsApp ya biashara."""
    if not bot.notify_handoff:
        return
    owner = bot.owner_digits
    if not owner:
        logger.warning('[%s] hakuna owner_whatsapp — hakuna aliyearifiwa', bot.session_name)
        return

    # Usimtumie mmiliki taarifa kuhusu mazungumzo yake mwenyewe
    if bot.is_owner(conv.customer_phone):
        return

    who = conv.customer_name or conv.wa_contact_name or 'Mteja'
    recent = conv.get_recent_messages(limit=4)

    # LID (tarakimu 15) si namba ya simu — huwezi kuipigia. Kumwonyesha
    # mmiliki `158351803576497` kama "namba" kunamdanganya. Tunamwelekeza
    # kwenye chat badala yake.
    ident = (conv.customer_phone or '')
    is_lid = len(ident) >= 15
    contact = 'fungua chat kwenye WhatsApp ya biashara' if is_lid else ident

    lines = [
        "🙋 *Mteja anahitaji binadamu*",
        "",
        f"*{who}* — {contact}",
        f"Sababu: {reason or 'Ameomba'}",
        "",
        "*Mazungumzo ya mwisho:*",
    ]
    for m in recent:
        tag = "Mteja" if m.role == 'user' else "Bot"
        body = (m.content or '')[:140]
        lines.append(f"_{tag}:_ {body}")
    lines += [
        "",
        "Bot imesimama kwa mteja huyu na haitajibu tena.",
        f"Ukimaliza, andika: `endelea {conv.customer_phone}`",
    ]

    res = wa.send_text(bot.owner_whatsapp, "\n".join(lines))
    if res.get('success'):
        conv.handoff_notified_at = timezone.now()
        conv.save(update_fields=['handoff_notified_at'])
    else:
        logger.error('[%s] taarifa kwa mmiliki imeshindwa: %s',
                     bot.session_name, res.get('error'))


def _send(wa, conv, to, text):
    """
    Tuma kwa MTEJA na hifadhi.

    `wa.jid` ni ya mazungumzo haya, kwa hiyo ni sahihi hapa. Kwa
    mmiliki (`notify_owner`) hatuitumii — jid ingepeleka taarifa kwa
    mteja badala ya mmiliki.
    """
    from .models import Message
    res = wa.send_text(to, text, jid=getattr(wa, 'jid', None))
    Message.objects.create(
        conversation=conv, role='assistant', content=text,
        wa_message_id=res.get('message_id', '') or '',
    )
    return res


# ══════════════════════════════════════════════════════════════
#  KUMKUMBUSHA MMILIKI
# ══════════════════════════════════════════════════════════════

REMIND_AFTER_MINUTES = 15


def remind_owner_if_stale(bot, wa, conv, latest_text=''):
    """
    Mteja anaendelea kuandika lakini hajajibiwa na mtu.

    Bot HAIMJIBU mteja — hiyo ndiyo sheria. Lakini inaweza kumgusa
    mmiliki tena, kwa sababu mteja anayeandika mara ya tatu bila
    jibu ndiye anayekaribia kuondoka.

    Kikomo cha dakika 15 ni cha makusudi: mmiliki akipokea taarifa
    kila ujumbe, ataacha kuzisoma zote.
    """
    if not bot.notify_handoff or not bot.owner_digits:
        return

    last = conv.handoff_notified_at or conv.handoff_at
    if not last:
        return

    mins = int((timezone.now() - last).total_seconds() // 60)
    if mins < REMIND_AFTER_MINUTES:
        return

    who = conv.customer_name or conv.wa_contact_name or 'Mteja'
    waited = conv.handoff_waiting_minutes
    dur = f"dakika {waited}" if waited < 60 else f"saa {waited // 60}"

    lines = [
        "⏰ *Bado anasubiri*",
        "",
        f"*{who}* — {conv.customer_phone}",
        f"Amesubiri {dur} na ameandika tena:",
        "",
        f"_{(latest_text or '')[:180]}_",
        "",
        f"Ukimaliza: `endelea {conv.customer_phone}`",
    ]

    res = wa.send_text(bot.owner_whatsapp, "\n".join(lines))
    if res.get('success'):
        conv.handoff_notified_at = timezone.now()
        conv.save(update_fields=['handoff_notified_at'])
