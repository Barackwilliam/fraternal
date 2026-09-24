"""
Fulfillment — kinachotokea baada ya malipo KUKAMILIKA.

Kila `purpose` ina handler yake. Zote ni idempotent: `tx.fulfilled` +
`select_for_update()` huhakikisha kazi inafanyika MARA MOJA tu, hata kama
callback na IPN zote mbili zikija (Pesapal hutuma zote).

Hakuna kitu kinachobadilishwa kwenye model zilizopo isipokuwa kuongeza
rekodi ya malipo na kusogeza tarehe ya mwisho — sawasawa na jinsi staff
walivyokuwa wanafanya kwa mkono.
"""
import logging
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


def _add_months(d, months):
    try:
        from dateutil.relativedelta import relativedelta
        return d + relativedelta(months=int(months))
    except ImportError:
        return d + timedelta(days=30 * int(months))


def fulfill(tx):
    """
    Elekeza kwenye handler sahihi. Inaitwa na callback NA ipn.
    Inarudisha True ikiwa fulfillment imefanyika sasa (mara ya kwanza).
    """
    if tx.status != 'completed':
        return False

    with transaction.atomic():
        # Funga rekodi ili callback + IPN zisigongane
        locked = type(tx).objects.select_for_update().get(pk=tx.pk)
        if locked.fulfilled:
            return False

        handler = {
            'chatbot_subscription': _fulfill_subscription,
            'hosting_renewal':      _fulfill_hosting,
            'invoice':              _fulfill_invoice,
        }.get(locked.purpose)

        if not handler:
            logger.error('Pesapal: purpose isiyojulikana %s', locked.purpose)
            return False

        try:
            handler(locked)
        except Exception:
            logger.exception('Pesapal fulfillment imeshindikana kwa %s', locked.merchant_reference)
            raise

        locked.fulfilled = True
        locked.completed_at = locked.completed_at or timezone.now()
        locked.save(update_fields=['fulfilled', 'completed_at'])

        # Risiti + email zitumwe MARA MOJA baada ya commit kufanikiwa
        # (nje ya lock) — hivyo hazitumwi kama transaction itarudishwa.
        def _issue():
            try:
                from .pesapal_receipt import issue_receipt
                issue_receipt(locked)
            except Exception:
                logger.exception('Pesapal: issue_receipt imeshindikana')
        transaction.on_commit(_issue)
        return True


# ─────────────────────────────────────────────
# CHATBOT SUBSCRIPTION
# ─────────────────────────────────────────────
def _fulfill_subscription(tx):
    from apps.chatbot.models import BotSubscription, SubscriptionPayment

    sub = BotSubscription.objects.select_for_update().filter(id=tx.target_id).first()
    if not sub:
        logger.error('Pesapal: BotSubscription %s haipo', tx.target_id)
        return

    months = int(tx.months or 1)
    ref = tx.confirmation_code or tx.merchant_reference

    # Epuka kurekodi mara mbili kwa transaction ile ile
    if not SubscriptionPayment.objects.filter(transaction_ref=ref).exists():
        SubscriptionPayment.objects.create(
            subscription=sub,
            amount=int(round(float(tx.amount))),
            months_covered=months,
            payment_method='Pesapal',
            transaction_ref=ref,
            status='verified',
            verified_at=timezone.now(),
            notes=f'Pesapal {tx.merchant_reference} ({tx.payment_method})',
        )

    today = timezone.now().date()
    base = sub.end_date if (sub.end_date and sub.end_date > today) else today
    sub.end_date = _add_months(base, months)
    sub.status = 'active'
    # Anzisha upya kipindi cha kuhesabu jumbe
    sub.usage_period_start = today
    sub.messages_used = 0
    sub.save(update_fields=['end_date', 'status', 'usage_period_start', 'messages_used'])
    logger.info('Pesapal: subscription %s imeongezwa hadi %s', sub.pk, sub.end_date)


# ─────────────────────────────────────────────
# HOSTING RENEWAL
# ─────────────────────────────────────────────
def _fulfill_hosting(tx):
    from apps.models import ManagedWebsite, HostingPayment

    site = ManagedWebsite.objects.select_for_update().filter(pk=tx.target_id).first()
    if not site:
        logger.error('Pesapal: ManagedWebsite %s haipo', tx.target_id)
        return

    months = int(tx.months or 1)
    ref = tx.confirmation_code or tx.merchant_reference

    if not HostingPayment.objects.filter(transaction_ref=ref).exists():
        HostingPayment.objects.create(
            website=site,
            amount=tx.amount,
            payment_date=timezone.now().date(),
            months_covered=months,
            payment_method='Pesapal',
            transaction_ref=ref,
            notes=f'Pesapal {tx.merchant_reference} ({tx.payment_method})',
        )

    today = timezone.now().date()
    base = site.hosting_end_date if (site.hosting_end_date and site.hosting_end_date > today) else today
    site.hosting_end_date = _add_months(base, months)
    if site.status in ('suspended', 'maintenance'):
        site.status = 'active'
    site.save(update_fields=['hosting_end_date', 'status'])
    logger.info('Pesapal: hosting %s imeongezwa hadi %s', site.pk, site.hosting_end_date)


# ─────────────────────────────────────────────
# INVOICE
# ─────────────────────────────────────────────
def _fulfill_invoice(tx):
    from apps.models import Invoice

    inv = Invoice.objects.select_for_update().filter(token=tx.target_id).first()
    if not inv:
        logger.error('Pesapal: Invoice %s haipo', tx.target_id)
        return

    inv.amount_paid = inv.grand_total
    inv.status = 'paid'
    inv.paid_at = timezone.now()
    inv.paid_reference = tx.confirmation_code or tx.merchant_reference
    inv.save(update_fields=['amount_paid', 'status', 'paid_at', 'paid_reference'])
    logger.info('Pesapal: invoice %s imelipwa', inv.invoice_number or inv.pk)
