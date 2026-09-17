"""
Kikomo cha matumizi ya AI.

TATIZO

Groq ya bure inatoa **tokens 6,000 kwa dakika** na **maombi 30 kwa
dakika** — kwa AKAUNTI NZIMA, si kwa kila bot. System prompt yenye
biashara, huduma, FAQs na kumbukumbu ya mteja inaweza kufika tokens
1,500 kwa ujumbe mmoja.

Mteja mmoja akituma jumbe kumi mfululizo, anafikisha kikomo — na bot
ZOTE zinanyamaza, si yake tu. Hakuna mtu mbaya anayehitajika; mteja
mwenye hamu anatosha.

TABAKA TATU

  1. Kila mteja, kwa dakika  — mtu mmoja asichome kila kitu
  2. Kila mteja, kwa saa     — kuzuia mtu anayeendelea taratibu
  3. Wote kwa pamoja         — mwavuli wa mwisho wa akaunti

KWA NINI CACHE NA SI DATABASE

Builder inatumia `AiUsageLog` kwenye database, na inafaa hapo — ni
kikomo cha kila siku, na rekodi inasaidia. Hapa ni kikomo cha dakika,
kinachoangaliwa kwa kila ujumbe. Kuandika database kila mara kwa
kitu kinachoisha baada ya sekunde 60 ni gharama bila faida.

Redis inashirikiwa na workers wote. Bila Redis (dev), LocMemCache
inafanya kazi kwa worker mmoja — si kamili, lakini si hatari.
"""
import logging
import os

from django.core.cache import cache

logger = logging.getLogger('chatbot.limit')

# Kila mteja, kwa dakika. Mtu anayeandika kwa mkono hafiki 8 kwa
# dakika akiwa na maana; anayefika ni mtu anayebonyeza bila kusoma.
PER_CUSTOMER_MINUTE = int(os.getenv('CHAT_LIMIT_CUSTOMER_MIN', '8'))

# Kila mteja, kwa saa. Mazungumzo marefu halisi hayazidi hii.
PER_CUSTOMER_HOUR = int(os.getenv('CHAT_LIMIT_CUSTOMER_HOUR', '60'))

# Wote kwa pamoja, kwa dakika. Groq ya bure inatoa 30 RPM; tunaacha
# nafasi kwa proposals, mikataba, digest na builder zinazoshiriki
# funguo ile ile.
GLOBAL_MINUTE = int(os.getenv('CHAT_LIMIT_GLOBAL_MIN', '20'))


def _hit(key, limit, seconds):
    """
    Inarudisha (inaruhusiwa, idadi_sasa).

    `cache.add` inaweka funguo pale tu isipokuwepo, kwa hiyo TTL
    inawekwa mara moja kwa kila dirisha. `incr` baada yake haibadilishi
    TTL — dirisha linaisha kama lilivyopangwa.
    """
    try:
        cache.add(key, 0, seconds)
        count = cache.incr(key)
    except ValueError:
        # Funguo imeisha kati ya `add` na `incr` — ni mwanzo wa dirisha
        cache.set(key, 1, seconds)
        count = 1
    except Exception:
        # Cache haipatikani — usimzuie mteja kwa sababu ya Redis
        logger.warning('cache haipatikani — kikomo kimerukwa')
        return True, 0
    return count <= limit, count


def check(bot, phone):
    """
    Je, ujumbe huu unaruhusiwa kwenda AI?

    Inarudisha (inaruhusiwa, sababu). `sababu` ni tupu ikiruhusiwa.
    """
    digits = ''.join(c for c in str(phone or '') if c.isdigit())
    if not digits:
        return True, ''

    ok, n = _hit(f'chat:lim:m:{bot.id}:{digits}', PER_CUSTOMER_MINUTE, 60)
    if not ok:
        logger.info('[%s] %s amefikia kikomo cha dakika (%d)',
                    bot.session_name, digits, n)
        return False, 'minute'

    ok, n = _hit(f'chat:lim:h:{bot.id}:{digits}', PER_CUSTOMER_HOUR, 3600)
    if not ok:
        logger.info('[%s] %s amefikia kikomo cha saa (%d)',
                    bot.session_name, digits, n)
        return False, 'hour'

    ok, n = _hit('chat:lim:global', GLOBAL_MINUTE, 60)
    if not ok:
        logger.warning('Kikomo cha jumla kimefikiwa (%d/dakika) — '
                       'bot zote zinapunguza kasi', n)
        return False, 'global'

    return True, ''


def message_for(reason, bot=None):
    """
    Ujumbe wa kumwambia mteja. Unatumwa MARA MOJA kwa kila dirisha.

    Hatumlaumu mteja — kwake, ameuliza tu maswali. Tunamwambia
    ukweli na tunampa njia nyingine.
    """
    if reason == 'global':
        return ("Samahani, tuna wateja wengi kwa sasa. Tafadhali jaribu tena "
                "baada ya dakika moja.")
    if reason == 'hour':
        phone = (getattr(bot, 'whatsapp_number', '') or '').strip()
        base = ("Umeuliza maswali mengi kwa muda mfupi. Tafadhali subiri "
                "kidogo, au ongea na mtu wa timu yetu moja kwa moja.")
        return f"{base}\n\n{phone}" if phone else base
    return ("Tafadhali nipe dakika moja nikushughulikie maswali yako "
            "ya awali. Andika tena baada ya muda mfupi.")


def already_warned(bot, phone, reason):
    """
    Je, tumeshamwambia mteja huyu kwenye dirisha hili?

    Bila hii, mteja anayebonyeza mara ishirini anapata onyo mara
    ishirini — ambayo ni kelele zaidi kuliko tatizo lenyewe, na
    inatumia bandwidth ya WhatsApp bila sababu.
    """
    digits = ''.join(c for c in str(phone or '') if c.isdigit())
    key = f'chat:warned:{reason}:{bot.id}:{digits}'
    ttl = 3600 if reason == 'hour' else 60
    try:
        if cache.get(key):
            return True
        cache.set(key, 1, ttl)
        return False
    except Exception:
        return False
