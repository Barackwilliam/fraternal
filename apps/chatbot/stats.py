"""Hesabu za chati kwa swali MOJA.

Awali chati za siku 30 zilikuwa zinapiga swali moja kwa kila siku:

    for i in range(30):
        Message.objects.filter(created_at__date=day).count()

Maswali 30 kwa chati moja. Database iko Supabase (Stockholm), kwa hiyo
kila swali ni safari ya mtandao — /manage/chatbot/ ilikuwa na maswali 52,
31 kati yake yakiwa chati hii. Sasa ni `GROUP BY` moja.
"""
from datetime import date, timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate


def daily_counts(queryset, days, field='created_at', fmt='%d %b'):
    """[{'date': '12 Sep', 'count': 5}, ...] kwa siku `days` zilizopita, leo mwisho.

    Siku zisizo na rekodi zinapata 0, kama loop ya zamani ilivyofanya.
    `TruncDate` inatumia timezone ya sasa — sawa na `__date` ya zamani.
    """
    today = date.today()
    start = today - timedelta(days=days - 1)
    rows = (queryset
            .filter(**{f'{field}__date__gte': start})
            .annotate(_d=TruncDate(field))
            .values('_d')
            .annotate(n=Count('pk'))
            .order_by())
    by_day = {r['_d']: r['n'] for r in rows}
    return [
        {'date': (start + timedelta(days=i)).strftime(fmt),
         'count': by_day.get(start + timedelta(days=i), 0)}
        for i in range(days)
    ]
