"""
Baileys: BotConfig inapata session badala ya Meta phone number ID.

`session_name` ni `unique=True`. Ikiongezwa moja kwa moja, bot zote
zilizopo zingepata '' na constraint ingeanguka mara moja kwenye bot ya
pili. Kwa hiyo hatua ni tatu:

  1. Ongeza field BILA unique
  2. Jaza kwa kila bot iliyopo (mantiki ile ile ya `_make_session_name`)
  3. Ndipo weka unique

Jina linatokana na jina la biashara + herufi 6 za UUID. LISIBADILIKE
baadaye — ndiyo funguo ya jedwali `baileys_auth` la Supabase, na
likibadilika mteja analazimika kuscan QR upya.
"""
from django.db import migrations, models
from django.utils.text import slugify


def fill_session_names(apps, schema_editor):
    BotConfig = apps.get_model('chatbot', 'BotConfig')
    used = set()
    for bot in BotConfig.objects.all():
        if bot.session_name:
            used.add(bot.session_name)
            continue
        base = slugify(bot.business_name or bot.bot_name or 'bot')[:40] or 'bot'
        name = f"{base}-{str(bot.id)[:6]}"
        # Kinga: kama kwa bahati mbaya linarudiwa, ongeza herufi zaidi
        n = 6
        while name in used and n < 32:
            n += 2
            name = f"{base}-{str(bot.id)[:n]}"
        used.add(name)
        bot.session_name = name
        bot.save(update_fields=['session_name'])


def noop(apps, schema_editor):
    """Kurudi nyuma hakuhitaji kufuta majina — field yenyewe inaondoka."""


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0003_alter_botconfig_ai_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='botconfig',
            name='autostart',
            field=models.BooleanField(
                default=True,
                help_text='Bridge ikirestart, session hii ianzishwe upya yenyewe'),
        ),
        migrations.AddField(
            model_name='botconfig',
            name='connected_number',
            field=models.CharField(
                blank=True, editable=False, max_length=30,
                help_text='Namba iliyoscan QR, kutoka bridge'),
        ),
        migrations.AddField(
            model_name='botconfig',
            name='connection_status',
            field=models.CharField(
                default='disconnected', editable=False, max_length=20,
                help_text='starting | waiting_qr | connected | disconnected | logged_out'),
        ),
        migrations.AddField(
            model_name='botconfig',
            name='last_seen_at',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),

        # ── Hatua 1: bila unique ──
        migrations.AddField(
            model_name='botconfig',
            name='session_name',
            field=models.SlugField(
                blank=True, default='', max_length=60,
                help_text='Jina la session kwenye bridge. Linatengenezwa lenyewe.'),
        ),

        # ── Hatua 2: jaza ──
        migrations.RunPython(fill_session_names, noop),

        # ── Hatua 3: sasa unique ni salama ──
        migrations.AlterField(
            model_name='botconfig',
            name='session_name',
            field=models.SlugField(
                blank=True, unique=True, max_length=60,
                help_text='Jina la session kwenye bridge. Linatengenezwa lenyewe.'),
        ),

        migrations.AlterField(
            model_name='botconfig',
            name='whatsapp_phone_id',
            field=models.CharField(blank=True, max_length=50,
                                   help_text='Meta Phone Number ID (legacy)'),
        ),
        migrations.AlterField(
            model_name='botconfig',
            name='whatsapp_token',
            field=models.CharField(blank=True, max_length=500,
                                   help_text='WhatsApp Cloud API token (legacy)'),
        ),
    ]
