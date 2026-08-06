# apps/account_billing.py
"""
Account-level view of what a client owes.

The balance is a *presentation* number only. Every amount inside it still
belongs to one specific ManagedWebsite, because hosting_end_date lives on the
website — if we merged the money we could no longer extend one site's expiry
without touching the others.

So: one balance on screen, separate records underneath.
"""

from django.utils import timezone

# Same window portal_billing already uses, kept in one place now.
DUE_SOON_DAYS = 14
URGENT_DAYS = 7


def _line_for(website):
    today = timezone.now().date()
    end = website.hosting_end_date
    days_left = (end - today).days

    if website.status == 'suspended':
        state, label, tone = 'suspended', 'Suspended', 'red'
    elif days_left < 0:
        over = abs(days_left)
        state, tone = 'overdue', 'red'
        label = f'Overdue {over} day{"" if over == 1 else "s"}'
    elif days_left <= URGENT_DAYS:
        state, tone = 'urgent', 'yellow'
        label = 'Due today' if days_left == 0 else f'Due in {days_left} days'
    elif days_left <= DUE_SOON_DAYS:
        state, tone = 'soon', 'yellow'
        label = f'Due in {days_left} days'
    else:
        state, tone = 'ok', 'green'
        label = f'{days_left} days left'

    payable = state in ('suspended', 'overdue', 'urgent', 'soon')

    return {
        'website': website,
        'state': state,
        'label': label,
        'tone': tone,
        'days_left': days_left,
        'amount': website.monthly_cost if payable else 0,
        'payable': payable,
        'options': website.billing_options,
    }


def build_account(client, websites):
    """
    Returns the account picture. `is_multi` decides which UI the portal shows —
    a client with one website keeps exactly the screen they had before.
    """
    lines = [_line_for(w) for w in websites]
    payable = [l for l in lines if l['payable']]

    # Most urgent first, so the thing that will actually be suspended is on top.
    order = {'suspended': 0, 'overdue': 1, 'urgent': 2, 'soon': 3, 'ok': 4}
    lines.sort(key=lambda l: (order[l['state']], l['days_left']))

    balance = sum(l['amount'] for l in payable)
    next_up = next((l for l in lines if l['state'] == 'ok'), None)

    return {
        'is_multi': len(lines) > 1,
        'lines': lines,
        'payable': payable,
        'balance': balance,
        'site_count': len(lines),
        'overdue_count': sum(1 for l in lines if l['state'] in ('overdue', 'suspended')),
        'urgent_count': sum(1 for l in lines if l['state'] == 'urgent'),
        'all_clear': balance == 0,
        'next_renewal': next_up['website'].hosting_end_date if next_up else None,
    }
