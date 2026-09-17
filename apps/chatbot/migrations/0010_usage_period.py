"""
Kipindi cha kuhesabu jumbe.

`messages_used` ilikuwa inaongezeka tu — hakuna mahali ilirudishwa
sifuri. Plan ya jumbe 1,000 KWA MWEZI ilikuwa inaishia MILELE ikifika
1,000 tangu bot ilipoanzishwa.

Hesabu zilizopo ni za maisha yote, si za mwezi — hazina maana kwa
mfumo mpya. Tunaanzisha upya kila mtu kwa kipindi cha sasa. Mteja
aliyekuwa amezuiliwa bila haki anarudi kufanya kazi mara moja.
"""
from django.db import migrations, models


def start_periods(apps, schema_editor):
    import calendar
    from datetime import date
    from django.utils import timezone

    BotSubscription = apps.get_model('chatbot', 'BotSubscription')
    today = timezone.now().date()

    for sub in BotSubscription.objects.all().iterator():
        anchor = (sub.start_date or today).day
        last = calendar.monthrange(today.year, today.month)[1]
        day = min(anchor, last)
        this_month = date(today.year, today.month, day)

        if today >= this_month:
            start = this_month
        else:
            y, m = ((today.year, today.month - 1) if today.month > 1
                    else (today.year - 1, 12))
            start = date(y, m, min(anchor, calendar.monthrange(y, m)[1]))

        sub.usage_period_start = start
        sub.messages_used = 0
        sub.save(update_fields=['usage_period_start', 'messages_used'])


def noop(apps, schema_editor):
    """Kurudi nyuma: field inaondoka, hakuna cha kufanya."""


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0009_owner_lid'),
    ]

    operations = [
        migrations.AddField(
            model_name='botsubscription',
            name='usage_period_start',
            field=models.DateField(
                blank=True, null=True,
                help_text='Mwanzo wa kipindi cha sasa cha kuhesabu jumbe'),
        ),
        migrations.RunPython(start_periods, noop),
    ]
