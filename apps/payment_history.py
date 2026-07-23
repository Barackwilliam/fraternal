"""
Historia ya malipo ya mteja — AWAMU, si jumla ya pesa.

Inaonyesha:
  • Awamu (phases) — kila malipo na kipindi kinachofunika
  • Alilipa lini dhidi ya alipopaswa kulipa (siku za kuchelewa)
  • Mapengo — siku ambazo huduma haikuwa imelipiwa
  • Mwenendo (trend) — je anaboreka au anachelewa zaidi?

Hakuna jumla ya pesa popote — hiyo ni kwa makusudi.
"""
from datetime import date

try:
    from dateutil.relativedelta import relativedelta
except ImportError:                                     # fallback bila dateutil
    relativedelta = None

# Siku za huruma — akilipa ndani ya hizi bado ni "kwa wakati"
GRACE_DAYS = 3


def _add_months(d, months):
    if relativedelta:
        return d + relativedelta(months=months)
    from datetime import timedelta
    return d + timedelta(days=30 * months)


def _classify(days_late):
    if days_late < 0:
        return 'early'
    if days_late <= GRACE_DAYS:
        return 'on_time'
    return 'late'


def website_phases(website):
    """
    Jenga upya awamu za malipo za tovuti moja.

    Kila malipo linafunika kipindi kinachofuata mfululizo kuanzia
    tarehe ya kuanza hosting. Tunalinganisha tarehe aliyolipa na
    tarehe kipindi hicho kilipoanza.
    """
    payments = list(website.payments.order_by('payment_date', 'pk'))
    if not payments or not website.hosting_start_date:
        return []

    cursor = website.hosting_start_date
    phases = []

    for i, p in enumerate(payments, start=1):
        months = int(p.months_covered or 1)
        period_start = cursor
        period_end = _add_months(period_start, months)
        days_late = (p.payment_date - period_start).days

        phases.append({
            'index': i,
            'website': website,
            'website_name': website.name,
            'payment': p,
            'paid_on': p.payment_date,
            'months': months,
            'period_start': period_start,
            'period_end': period_end,
            'days_late': days_late,
            'status': _classify(days_late),
            'method': p.get_payment_method_display() if hasattr(p, 'get_payment_method_display') else '',
            'reference': getattr(p, 'reference', '') or '',
        })
        cursor = period_end

    return phases


def website_gaps(phases):
    """
    Siku ambazo huduma haikuwa imelipiwa — kipindi kilianza lakini
    malipo yakachelewa.
    """
    gaps = []
    for ph in phases:
        if ph['days_late'] > GRACE_DAYS:
            gaps.append({
                'website_name': ph['website_name'],
                'from': ph['period_start'],
                'to': ph['paid_on'],
                'days': ph['days_late'],
                'phase_index': ph['index'],
            })
    return gaps


def build_history(client, websites=None):
    """
    Historia kamili ya mteja katika tovuti zake zote.
    Rudisha dict tayari kwa template.
    """
    from .models import ManagedWebsite

    if websites is None:
        websites = ManagedWebsite.objects.filter(client=client)

    all_phases, all_gaps = [], []
    for w in websites:
        ph = website_phases(w)
        all_phases.extend(ph)
        all_gaps.extend(website_gaps(ph))

    # Panga kwa tarehe ya kulipa
    all_phases.sort(key=lambda x: x['paid_on'])
    all_gaps.sort(key=lambda x: x['from'], reverse=True)

    total = len(all_phases)
    on_time = sum(1 for p in all_phases if p['status'] in ('early', 'on_time'))
    late = total - on_time
    late_phases = [p for p in all_phases if p['status'] == 'late']

    # Mwenendo: linganisha nusu ya kwanza na nusu ya pili
    trend = 'steady'
    if total >= 4:
        half = total // 2
        first_avg = sum(max(p['days_late'], 0) for p in all_phases[:half]) / half
        second = all_phases[half:]
        second_avg = sum(max(p['days_late'], 0) for p in second) / len(second)
        if second_avg < first_avg - 1:
            trend = 'improving'
        elif second_avg > first_avg + 1:
            trend = 'slipping'

    # Mfululizo wa sasa wa kulipa kwa wakati
    streak = 0
    for p in reversed(all_phases):
        if p['status'] in ('early', 'on_time'):
            streak += 1
        else:
            break

    # Mfululizo mrefu zaidi
    best, run = 0, 0
    for p in all_phases:
        run = run + 1 if p['status'] in ('early', 'on_time') else 0
        best = max(best, run)

    stats = {
        'total_phases': total,
        'on_time': on_time,
        'late': late,
        'on_time_pct': round(on_time / total * 100) if total else 0,
        'avg_days_late': round(sum(p['days_late'] for p in late_phases) / len(late_phases), 1) if late_phases else 0,
        'worst_delay': max((p['days_late'] for p in late_phases), default=0),
        'current_streak': streak,
        'best_streak': best,
        'trend': trend,
        'total_days_unpaid': sum(g['days'] for g in all_gaps),
        'months_covered': sum(p['months'] for p in all_phases),
    }

    # Data ya chart — siku za kuchelewa kwa kila awamu (si pesa)
    recent = all_phases[-12:]
    chart = {
        'labels': [p['paid_on'].strftime('%b %y') for p in recent],
        'values': [p['days_late'] for p in recent],
        'colors': [
            '#00ff88' if p['status'] in ('early', 'on_time') else '#ff3b5c'
            for p in recent
        ],
        'names': [p['website_name'] for p in recent],
    }

    return {
        'phases': list(reversed(all_phases)),   # mpya kwanza
        'gaps': all_gaps[:10],
        'stats': stats,
        'chart': chart,
        'has_data': total > 0,
    }


def coverage_bar(website, today=None):
    """
    Kipimo cha kuonyesha ni sehemu gani ya kipindi cha sasa imebaki.
    """
    today = today or date.today()
    start = website.hosting_start_date
    end = website.hosting_end_date
    if not start or not end or end <= start:
        return {'percent': 0, 'days_left': 0, 'expired': True}

    total_days = (end - start).days
    used = (today - start).days
    percent = max(0, min(100, round(used / total_days * 100))) if total_days else 100
    return {
        'percent': percent,
        'days_left': max((end - today).days, 0),
        'expired': end < today,
    }
