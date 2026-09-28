"""Safisha EmailLog zilizohifadhiwa kabla ya marekebisho.

1. `error` ilikuwa ikijazwa na `reason` ya Brevo hata kwa matukio ya
   kawaida — "sent" ilionekana kwa rangi nyekundu kana kwamba ni kosa.
2. Alert za mfumo zilikuwa zikiingia kama aina "other".
"""
from django.db import migrations

PROBLEM = ('bounced', 'spam', 'blocked', 'error', 'deferred')
ALERT_HINTS = ('ssl', 'tatizo', '[jamiitek]')


def forwards(apps, schema_editor):
    EmailLog = apps.get_model('apps', 'EmailLog')
    EmailLog.objects.exclude(status__in=PROBLEM).exclude(error='').update(error='')
    for log in EmailLog.objects.filter(category='other').only('pk', 'subject'):
        low = (log.subject or '').lower()
        if any(h in low for h in ALERT_HINTS):
            EmailLog.objects.filter(pk=log.pk).update(category='alert')


class Migration(migrations.Migration):
    dependencies = [('apps', '0040_email_log')]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
