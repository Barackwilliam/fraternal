"""Malipo ya JamiiBot — sehemu MOJA ya kuongeza subscription.

KWA NINI

Kulikuwa na njia NNE tofauti za kuongeza subscription baada ya malipo, kila
moja na hesabu yake:

    Pesapal            miezi halisi, kuanzia leo au tarehe ya mwisho
    /manage/ (Verify)  siku 30 × miezi, kuanzia leo au tarehe ya mwisho
    /manage/ (Bulk)    siku 30 × miezi, kuanzia leo au tarehe ya mwisho
    Django admin       siku 30 × miezi, kuanzia TAREHE YA MWISHO HATA IKIWA
                       IMEPITA — mteja aliyechelewa siku 20 alipata siku 10

Na zote zilikosa vitu tofauti: hakuna iliyohifadhi mpango uliolipiwa, njia
tatu hazikurudisha hesabu ya jumbe, na "Verify" iliweza kubonyezwa mara
mbili na kutoa miezi miwili.

Sasa zote zinaita `apply_payment` na `verify_payment` hapa.
"""
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils import timezone

ALLOWED_MONTHS = (1, 3, 6, 12)
# Lazima zilingane na zinazoonyeshwa kwenye billing.html (5%, 10%, 15%)
MONTH_DISCOUNT = {1: 1.0, 3: 0.95, 6: 0.90, 12: 0.85}


def clean_months(raw):
    """'3' -> 3. Thamani yoyote isiyoruhusiwa ('abc', '0', '500') -> 1.

    Awali `int()` ya moja kwa moja: 'abc' ilileta Server Error, na '500'
    iliunda agizo la TZS 25,000,000 kwa website ya TZS 50,000/mwezi.
    """
    try:
        m = int(str(raw).strip())
    except (TypeError, ValueError):
        return 1
    return m if m in ALLOWED_MONTHS else 1


def parse_amount(raw):
    """'15,000' / '15 000' / 'TZS 15,000' / '15000.00' -> 15000. Isiyosomeka -> None.

    Watanzania wengi huandika kiasi kwa koma. `int('15,000')` ilileta
    Server Error kwenye fomu ya mteja.
    """
    s = re.sub(r'[^\d.]', '', str(raw or ''))
    if not s or s.count('.') > 1:
        return None
    try:
        v = int(round(float(s)))
    except ValueError:
        return None
    return v if v > 0 else None


def price_for(plan, months):
    months = clean_months(months)
    return int(round(int(plan.price_tzs) * months * MONTH_DISCOUNT[months]))


def apply_payment(sub, months, plan=None):
    """Ongeza subscription kwa malipo yaliyothibitishwa.

    - Kuanzia tarehe ya mwisho kama bado haijafika (mteja anayelipa mapema
      hapotezi siku), vinginevyo kuanzia leo.
    - Miezi halisi ya kalenda, si siku 30.
    - Mpango uliolipiwa unawekwa.
    - Hesabu ya jumbe inaanza upya — mteja aliyesimamishwa kwa kufikia
      kikomo anarudi hewani mara moja.
    - Bot iliyosimamishwa inarudishwa hewani.
    """
    today = timezone.now().date()
    months = int(months or 1)
    base = sub.end_date if (sub.end_date and sub.end_date > today) else today
    sub.end_date = base + relativedelta(months=months)
    sub.status = 'active'
    if plan is not None:
        sub.plan = plan
    sub.usage_period_start = today
    sub.messages_used = 0
    sub.save()

    bot = sub.bot
    # 'pending' = bado haijaunganishwa na WhatsApp — hiyo si kazi ya malipo
    if bot.status == 'suspended':
        bot.status = 'active'
        bot.is_active = True
        bot.save(update_fields=['status', 'is_active'])
    return sub


def verify_payment(pay, user=None, months=None):
    """Thibitisha malipo ya mkono. Inarudisha False kama tayari yalithibitishwa.

    Salama kubonyezwa mara mbili: rekodi inafungwa (select_for_update), na
    malipo yaliyokwisha kuthibitishwa hayaongezi muda tena.
    """
    from .models import SubscriptionPayment

    with transaction.atomic():
        locked = SubscriptionPayment.objects.select_for_update().get(pk=pay.pk)
        if locked.status == 'verified':
            return False
        months = clean_months(months if months is not None else locked.months_covered)
        locked.status = 'verified'
        locked.verified_at = timezone.now()
        locked.verified_by = user
        locked.months_covered = months
        locked.save()
        apply_payment(locked.subscription, months, plan=locked.plan)
    return True
