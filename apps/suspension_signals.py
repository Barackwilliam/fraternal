"""Taarifa ya kusitishwa kwa website — sehemu MOJA kwa njia zote.

TATIZO

Website inaweza kusitishwa kwa njia tano tofauti:

    apps/bulk_actions.py                      (vitendo vya pamoja)
    apps/management_views.py                  (kitufe cha admin)
    apps/hosting_service.py                   (auto-suspend ya AI)
    apps/management/commands/process_scheduled_actions.py   (mara mbili)
    apps/utils/email_notifications.py         (onyo la kila siku)

Kila moja ilikuwa inatuma barua yake YENYEWE, na kila moja ilikuwa na
sharti tofauti: `if notify`, `if request.POST.get('notify_client')`,
`if website.send_expiry_warnings`. Matokeo: mteja angeweza kukuta
website yake imezimwa bila kupata taarifa yoyote — kwa sababu mtu
hakuweka tiki, au kwa sababu bendera isiyohusiana ilikuwa imezimwa.

SULUHISHO

Signal inayoangalia mabadiliko ya `status`. Popote pale website
inapohifadhiwa ikiwa imesitishwa, mteja anapata barua. Hakuna tiki ya
kusahaulika, na code mpya itakayosimamisha website kesho inafunikwa
kiotomatiki.

`suspension_notified_at` inazuia kurudia: barua moja kwa kusitishwa
kumoja. Website ikirejeshwa, kumbukumbu inafutwa ili ikisitishwa tena
baadaye, taarifa itume tena.

Barua inatumwa kwenye thread ya nyuma. Kusitisha kupitia admin
hakupaswi kusubiri Brevo (timeout ya sekunde 20) kabla ukurasa
haujajibu.
"""
import logging
import threading

from django.db import connection
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)

_OLD_STATUS = '_jt_old_status'


@receiver(pre_save, sender='apps.ManagedWebsite')
def _remember_status(sender, instance, **kwargs):
    """Hifadhi hali ya zamani ili post_save ijue kama imebadilika."""
    if not instance.pk:
        setattr(instance, _OLD_STATUS, None)
        return
    try:
        setattr(instance, _OLD_STATUS,
                sender.objects.filter(pk=instance.pk)
                              .values_list('status', flat=True).first())
    except Exception:
        setattr(instance, _OLD_STATUS, None)


@receiver(post_save, sender='apps.ManagedWebsite')
def _notify_on_suspension(sender, instance, created, **kwargs):
    old = getattr(instance, _OLD_STATUS, None)

    # ── Imerejeshwa: futa kumbukumbu ili taarifa ifanye kazi tena ──
    if instance.status != 'suspended':
        if instance.suspension_notified_at:
            sender.objects.filter(pk=instance.pk).update(suspension_notified_at=None)
        return

    if created or old == 'suspended':
        return                      # si mabadiliko mapya
    if instance.suspension_notified_at:
        return                      # tayari amearifiwa kwa kusitishwa hii

    # Weka alama SASA HIVI (si kwenye thread) ili maombi mawili
    # yanayotokea kwa pamoja yasitume barua mbili.
    stamped = sender.objects.filter(
        pk=instance.pk, suspension_notified_at__isnull=True
    ).update(suspension_notified_at=timezone.now())
    if not stamped:
        return

    threading.Thread(
        target=_send_suspension_email,
        args=(instance.pk,),
        name=f'jt-suspend-mail-{instance.pk}',
        daemon=True,
    ).start()


def _send_suspension_email(website_pk):
    """Inakimbia kwenye thread ya nyuma — kamwe isichelewesha ombi."""
    from apps.models import ManagedWebsite
    from apps.utils.email_notifications import send_website_suspended
    try:
        site = (ManagedWebsite.objects
                .select_related('client')
                .filter(pk=website_pk).first())
        if not site:
            return
        if not (site.client and site.client.email):
            logger.warning('[Suspend] %s: mteja hana email — hakuna taarifa', site.name)
            # Bila email hakuna taarifa; ondoa alama ili ikiwekwa baadaye
            # barua iweze kutumwa.
            ManagedWebsite.objects.filter(pk=website_pk).update(suspension_notified_at=None)
            return

        ok = send_website_suspended(
            site, reason=site.suspension_reason or 'Hosting payment overdue')
        if ok:
            logger.info('[Suspend] taarifa imetumwa: %s -> %s', site.name, site.client.email)
        else:
            # Haikutumwa — ondoa alama ili jaribio lijalo lifanyike
            ManagedWebsite.objects.filter(pk=website_pk).update(suspension_notified_at=None)
            logger.error('[Suspend] taarifa imeshindwa: %s', site.name)
    except Exception:
        logger.exception('[Suspend] hitilafu kwenye taarifa ya kusitishwa')
        try:
            from apps.models import ManagedWebsite as MW
            MW.objects.filter(pk=website_pk).update(suspension_notified_at=None)
        except Exception:
            pass
    finally:
        connection.close()
