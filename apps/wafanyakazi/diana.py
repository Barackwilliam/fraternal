"""
Diana — Fedha na ofisi.

  • Invoice zilizopita tarehe ya kulipwa → rasimu ya kumkumbusha mteja
  • Invoice zinazoisha ndani ya siku 3 → rasimu ya ukumbusho wa upole
  • Malipo ya JamiiBot yanayosubiri kuthibitishwa → kazi ya ofisi
  • Hesabu za wiki (kwa ripoti ya William)
"""
from datetime import timedelta

from django.db.models import Sum

from . import ai
from .board import found, money, settle, site
from .team import member, signature

SLUG = 'diana'
DUE_SOON_DAYS = 3


def _reminder(inv, days_late):
    who = member(SLUG)
    balance = money(inv.balance_due, inv.currency)
    due = inv.due_date.strftime('%d/%m/%Y')
    link = site(inv.public_url)
    name = inv.client_name or (inv.client.name if inv.client else '') or 'Mteja'
    number = inv.invoice_number or f'#{inv.pk}'

    if days_late > 0:
        subject = f'Ukumbusho: invoice {number} ({balance})'
        facts = (f"Invoice {number} ({inv.title}) ya {name} ina salio la {balance}. "
                 f"Ilitakiwa kulipwa {due} — imechelewa siku {days_late}.")
        fallback = (f"Habari {name},\n\nTunakukumbusha kwa heshima kwamba invoice {number} "
                    f"({inv.title}) yenye salio la {balance} ilitakiwa kulipwa tarehe {due}. "
                    "Kama umeshalipa, tafadhali tutumie uthibitisho ili tusasishe kumbukumbu zetu.")
    else:
        subject = f'Invoice {number} inafika tarehe {due}'
        facts = (f"Invoice {number} ({inv.title}) ya {name} ina salio la {balance} "
                 f"na inatakiwa kulipwa {due}.")
        fallback = (f"Habari {name},\n\nHuu ni ukumbusho wa upole kwamba invoice {number} "
                    f"({inv.title}) yenye salio la {balance} inatakiwa kulipwa tarehe {due}.")

    body = ai.write(
        ai.persona(who['name'], who['role']),
        f"{facts}\nAndika ujumbe mfupi (aya 2) wa kumkumbusha mteja kulipa, kwa adabu, "
        f"ukianza na 'Habari {name},'. Usiweke link — itaongezwa.",
        max_tokens=300) or fallback
    return subject, f"{body}\n\nInvoice na njia za kulipa: {link}\n\nAsante,\n{signature(SLUG)}"


def _invoices(today):
    from apps.models import Invoice

    seen = []
    qs = (Invoice.objects.select_related('client')
          .exclude(status__in=['draft', 'paid', 'cancelled'])
          .filter(due_date__isnull=False, due_date__lte=today + timedelta(days=DUE_SOON_DAYS))
          .order_by('due_date')[:150])
    for inv in qs:
        if inv.balance_due <= 0:
            continue
        days_late = (today - inv.due_date).days
        stage = 'late' if days_late > 0 else 'soon'
        key = f'diana:inv:{inv.pk}:{stage}'
        seen.append(key)
        name = inv.client_name or (inv.client.name if inv.client else '') or 'Mteja'
        email = inv.display_email
        phone = inv.client_phone or (inv.client.phone if inv.client else '')
        balance = money(inv.balance_due, inv.currency)
        number = inv.invoice_number or f'#{inv.pk}'
        if days_late > 0:
            title = f'Invoice {number} ya {name} imechelewa siku {days_late} — {balance}'
            priority = 1 if days_late > 14 else 2
        else:
            title = f'Invoice {number} ya {name} inafika {inv.due_date:%d/%m} — {balance}'
            priority = 3
        found(SLUG, key, title,
              draft=(lambda inv=inv, d=days_late: _reminder(inv, d)) if (email or phone) else None,
              ref=f'invoice:{inv.pk}', priority=priority,
              detail=f'{inv.title} · salio {balance} · tarehe ya kulipa {inv.due_date:%d/%m/%Y}',
              link=site(f'/manage/invoices/{inv.pk}/edit/'),
              channel='email' if email else ('whatsapp' if phone else 'none'),
              recipient_name=name, recipient_email=email or '', recipient_phone=phone or '')
    settle(SLUG, 'diana:inv:', seen, 'Invoice imelipwa au imebadilishwa.')
    return len(seen)


def _bot_payments():
    from apps.chatbot.models import SubscriptionPayment

    seen = []
    for p in (SubscriptionPayment.objects.filter(status='pending')
              .select_related('subscription__bot')[:50]):
        key = f'diana:botpay:{p.pk}'
        seen.append(key)
        bot = p.subscription.bot
        found(SLUG, key, f'Thibitisha malipo ya JamiiBot: {bot.business_name} — {money(p.amount)}',
              ref=f'botpay:{p.pk}', priority=1,
              detail=f'{p.payment_method} · ref {p.transaction_ref} · miezi {p.months_covered}',
              link=site('/manage/chatbot/payments/'))
    settle(SLUG, 'diana:botpay:', seen, 'Malipo yamethibitishwa au kukataliwa.')
    return len(seen)


def numbers(now):
    """Hesabu za fedha kwa ripoti ya William."""
    from apps.models import Invoice
    from apps.pesapal_models import PesapalTransaction

    week_ago = now - timedelta(days=7)
    online = (PesapalTransaction.objects.filter(status='completed', completed_at__gte=week_ago)
              .aggregate(t=Sum('amount'))['t'] or 0)
    paid = Invoice.objects.filter(paid_at__gte=week_ago)
    invoices_paid = sum(inv.grand_total for inv in paid)
    open_qs = Invoice.objects.exclude(status__in=['draft', 'paid', 'cancelled'])
    outstanding = sum(inv.balance_due for inv in open_qs[:500])
    overdue = sum(1 for inv in open_qs[:500] if inv.is_overdue)
    return {
        'online_week': float(online),
        'invoices_paid_week': float(invoices_paid),
        'outstanding': float(outstanding),
        'overdue_count': overdue,
    }


def run(now):
    today = now.date()
    return {'invoices': _invoices(today), 'bot_payments': _bot_payments()}
