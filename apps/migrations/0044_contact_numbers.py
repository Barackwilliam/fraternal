"""Rekebisha namba za simu zilizohifadhiwa kwenye database.

Template zimeelekezwa kwenye apps/contact.py, lakini baadhi ya viungo vinaishi
kwenye DATA — hasa kitufe cha "Try It on WhatsApp" kwenye hero ya JamiiBot,
kilichopandikizwa na 0033 kikielekeza 0629 712 678. Mgeni aliyetaka kuona bot
ikijibu aliishia kuongea na mtu. Sasa:

    hero ya JamiiBot / "Try…"  -> JamiiBot ya majaribio (0768 146 230)
    kila kitu kingine          -> namba ya timu       (0750 910 158)

Inagusa tu viungo vyenye namba zilizoondolewa (0629…, 0757…). Kama uliwahi
kubadilisha slide kupitia admin, mabadiliko yako mengine hayaguswi.
"""
import re
from urllib.parse import quote

from django.db import migrations

OLD = re.compile(r'255(?:629712678|757854907)')
TEAM = '255750910158'
BOT = '255768146230'
BOT_TEXT = quote('Habari JamiiBot, nataka kujaribu demo')


def _is_bot(*texts):
    blob = ' '.join(t or '' for t in texts).lower()
    return any(w in blob for w in ('jamiibot', 'chatbot', 'bot', 'try it', 'jaribu'))


def _fix(url, bot):
    if not url or not OLD.search(url):
        return url
    if bot and 'wa.me/' in url:
        return f'https://wa.me/{BOT}?text={BOT_TEXT}'
    return OLD.sub(TEAM, url)


def forwards(apps, schema_editor):
    HeroSlide = apps.get_model('apps', 'HeroSlide')
    for h in HeroSlide.objects.all():
        bot_slide = _is_bot(h.eyebrow, h.headline)
        new1 = _fix(h.cta_url, bot_slide and _is_bot(h.cta_label))
        new2 = _fix(h.cta2_url, bot_slide and _is_bot(h.cta2_label))
        if (new1, new2) != (h.cta_url, h.cta2_url):
            h.cta_url, h.cta2_url = new1, new2
            h.save(update_fields=['cta_url', 'cta2_url'])

    Service = apps.get_model('apps', 'Service')
    for s in Service.objects.all():
        new = _fix(getattr(s, 'link_url', ''), False)
        if new != s.link_url:
            s.link_url = new
            s.save(update_fields=['link_url'])


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0043_payment_plan'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
