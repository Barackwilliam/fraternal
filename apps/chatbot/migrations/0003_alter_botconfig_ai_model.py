"""
`BotConfig.ai_model` sasa INATUMIKA kweli na ai_engine.

Kabla, field hii ilikuwa mapambo: `ai_engine.py` ilikuwa na model
iliyo-hardcode, kwa hiyo thamani ya default 'claude-sonnet-4-5'
haikuwahi kutumwa popote. Sasa ikitumwa Groq itaangusha ombi.

Migration hii inasafisha thamani za zamani zisizo za Groq — bot hizo
zinarudi kwenye GROQ_MODEL ya mfumo (tabia ile ile waliyokuwa nayo).
Bot zilizowekewa model halali ya Groq kwa mkono hazijaguswa.
"""
from django.db import migrations, models

# Thamani zilizowahi kuwa default lakini si za Groq
LEGACY = ['claude-sonnet-4-5', 'gemini-1.5-flash']


def clear_legacy_models(apps, schema_editor):
    BotConfig = apps.get_model('chatbot', 'BotConfig')
    BotConfig.objects.filter(ai_model__in=LEGACY).update(ai_model='')


def noop(apps, schema_editor):
    """Hakuna cha kurudisha — thamani tupu ni sahihi pande zote mbili."""


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_alter_botconfig_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botconfig',
            name='ai_model',
            field=models.CharField(
                blank=True, default='', max_length=60,
                help_text='Groq model ya bot hii. Ikiachwa tupu, inatumia GROQ_MODEL ya mfumo.'),
        ),
        migrations.RunPython(clear_legacy_models, noop),
    ]
