"""Kitufe cha pili cha slide ya JamiiBot -> bot ya demo (`whatsapp:bot`).

Slide ilibadilishwa kupitia admin ("See How It Works"), kwa hiyo 0044 —
iliyogusa namba zilizoondolewa pekee — haikuigusa. Sasa inatumia njia fupi
`whatsapp:bot`, inayogeuzwa na apps/templatetags/jt_contact.py kuwa namba ya
bot kutoka apps/contact.py: ukibadilisha namba kwenye Render, kitufe kinafuata.
"""
from django.db import migrations

BOT_WORDS = ('jamiibot', 'chatbot', 'whatsapp bot')


def forwards(apps, schema_editor):
    HeroSlide = apps.get_model('apps', 'HeroSlide')
    for h in HeroSlide.objects.all():
        blob = f'{h.eyebrow} {h.headline}'.lower()
        if h.cta2_label and any(w in blob for w in BOT_WORDS) and h.cta2_url != 'whatsapp:bot':
            h.cta2_url = 'whatsapp:bot'
            h.save(update_fields=['cta2_url'])


class Migration(migrations.Migration):
    dependencies = [('apps', '0044_contact_numbers')]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
