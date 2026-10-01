"""Namba za mawasiliano za JamiiTek — sehemu MOJA kwa mfumo mzima.

KWA NINI

Namba zilikuwa zimeandikwa moja kwa moja kwenye faili 25 tofauti, na namba
NNE tofauti zilitumika kama "rasmi": homepage ilisema 0629…, barua kwa wateja
0750…, Privacy Policy 0757…, na data ya Google (seo/schema.py) 0750…. Google
ikiona namba tofauti na ile iliyo kwenye site, inapunguza imani kwa biashara;
mteja aliyesimamishiwa website aliambiwa apige namba moja, homepage nyingine.

Sasa namba ni MBILI, zenye majukumu wazi:

    team      — simu, WhatsApp ya wateja, na M-Pesa  (JAMIITEK_PHONE)
    bot_demo  — JamiiBot ya majaribio               (JAMIIBOT_DEMO_WHATSAPP)

Kuzibadilisha: weka env var kwenye Render. Hakuna faili la kuhariri.

Kwenye templates:   {% load jt_contact %} … {% contact "wa" %}
Kwenye Python:      from apps.contact import contact; contact()['phone']
"""
import os
import re

DEFAULT_TEAM = '+255750910158'
DEFAULT_BOT_DEMO = '+255768146230'


def _e164(raw, fallback):
    digits = re.sub(r'\D', '', raw or '')
    if digits.startswith('0') and len(digits) == 10:
        digits = '255' + digits[1:]
    if len(digits) == 9:
        digits = '255' + digits
    if not (digits.startswith('255') and len(digits) == 12):
        digits = re.sub(r'\D', '', fallback)
    return digits                       # 255750910158


def _pretty(d):
    return f'+{d[:3]} {d[3:6]} {d[6:9]} {d[9:]}'   # +255 750 910 158


def contact():
    team = _e164(os.getenv('JAMIITEK_PHONE', ''), DEFAULT_TEAM)
    bot = _e164(os.getenv('JAMIIBOT_DEMO_WHATSAPP', ''), DEFAULT_BOT_DEMO)
    return {
        # Timu: simu, WhatsApp, M-Pesa
        'phone': '+' + team,             # tel:+255750910158
        'phone_display': _pretty(team),  # +255 750 910 158
        'wa': team,                      # https://wa.me/255750910158
        'mpesa': '0' + team[3:],         # 0750910158 (jinsi M-Pesa inavyoandikwa)
        # JamiiBot ya majaribio
        'bot_wa': bot,
        'bot_display': _pretty(bot),
    }
