"""
"Ofisi" — maisha ya timu kwa ukurasa wa /manage/wafanyakazi/.

Kila kitu hapa kinatoka kwenye data halisi (Kazi, Ripoti, Alama): mfanyakazi
anaonekana "kazini" tu kama mzunguko wake wa mwisho ulikuwa karibuni, na
"anachofanya sasa" ni kazi yake halisi iliyo juu kabisa.
"""
from datetime import datetime, timedelta

from django.db.models import Count, Q
from django.utils import timezone

from .models import Alama, Kazi, Ripoti
from .team import member

ONLINE = timedelta(minutes=50)   # mzunguko ni kila dakika 30 — tunaacha nafasi


def _when(value):
    try:
        return datetime.fromisoformat(value) if value else None
    except ValueError:
        return None


def _doing(w, top):
    if w['awaiting']:
        n = w['awaiting']
        return f"Anasubiri idhini yako — rasimu {n} {'ziko' if n > 1 else 'iko'} tayari"
    if top:
        return top.title
    return {
        'william': 'Anafuatilia timu — hakuna kilichokwama',
        'ibrahimu': 'Anafuatilia mazungumzo ya JamiiBot',
        'selvester': 'Anatafuta leads mpya',
        'grace': 'Anaandaa post ijayo',
        'diana': 'Hesabu ziko sawa — hakuna deni jipya',
    }.get(w['slug'], 'Yuko tayari')


def team(snapshot_rows, now=None):
    """Ongeza hali hai ya kila mfanyakazi kwenye safu za snapshot()."""
    now = now or timezone.now()
    start = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
    done = dict(Kazi.objects.filter(closed_at__gte=start, status__in=[Kazi.SENT, Kazi.DONE])
                .values_list('worker').annotate(n=Count('pk')))
    new = dict(Kazi.objects.filter(created_at__gte=start).values_list('worker').annotate(n=Count('pk')))
    for w in snapshot_rows:
        slug = w['slug']
        w['last_run'] = _when(Alama.get(f'run:{slug}'))
        w['error'] = Alama.get(f'error:{slug}')
        w['online'] = bool(w['last_run'] and now - w['last_run'] < ONLINE)
        top = (Kazi.objects.filter(worker=slug, status__in=Kazi.LIVE)
               .order_by('status', 'priority', '-created_at').first())
        w['doing'] = _doing(w, top)
        w['done_today'] = done.get(slug, 0)
        w['new_today'] = new.get(slug, 0)
        load = w['open'] + w['awaiting']
        w['state'] = ('error' if w['error'] and not w['online'] else
                      'waiting' if w['awaiting'] else
                      'busy' if load else 'clear')
    if snapshot_rows and snapshot_rows[0]['slug'] == 'william':
        lead = snapshot_rows[0]
        lead['team_load'] = sum(r['open'] + r['awaiting'] for r in snapshot_rows[1:])
        lead['team_stale'] = sum(r['stale'] for r in snapshot_rows[1:])
    return snapshot_rows


VERBS = {
    Kazi.AWAITING: 'ameandaa rasimu',
    Kazi.OPEN: 'ameona kazi mpya',
    Kazi.SENT: 'ametuma',
    Kazi.DONE: 'amekamilisha',
    Kazi.DISMISSED: 'umeachana na',
}


def feed(limit=14, now=None):
    """Shughuli za saa 48 zilizopita, mpya kwanza — kama mazungumzo ya ofisini."""
    now = now or timezone.now()
    since = now - timedelta(hours=48)
    events = []
    for k in Kazi.objects.filter(created_at__gte=since).order_by('-created_at')[:limit]:
        verb = VERBS[Kazi.AWAITING] if k.draft else VERBS[Kazi.OPEN]
        events.append({'at': k.created_at, 'who': member(k.worker), 'verb': verb, 'what': k.title,
                       'tone': 'draft' if k.draft else 'new'})
    for k in (Kazi.objects.filter(closed_at__gte=since).exclude(status__in=Kazi.LIVE)
              .order_by('-closed_at')[:limit]):
        events.append({'at': k.closed_at, 'who': member(k.worker), 'verb': VERBS[k.status],
                       'what': k.title, 'tone': k.status, 'you': k.status == Kazi.DISMISSED})
    for r in Ripoti.objects.filter(created_at__gte=since)[:4]:
        events.append({'at': r.created_at, 'who': member('william'),
                       'verb': 'ametuma', 'what': r.get_kind_display().lower(), 'tone': 'report'})
    events.sort(key=lambda e: e['at'], reverse=True)
    return events[:limit]


def william_says(now=None):
    """Sentensi ya William kwa mmiliki: kipaumbele cha ripoti ya leo, au hali ya timu."""
    now = now or timezone.localtime()
    report = Ripoti.objects.filter(date=now.date()).first() or Ripoti.objects.first()
    if report:
        for line in report.text.splitlines():
            if 'Kipaumbele' in line:
                return line.split(':*', 1)[-1].strip(' *'), report
    awaiting = Kazi.objects.filter(status=Kazi.AWAITING).exclude(channel='social').count()
    stale = Kazi.objects.filter(status__in=Kazi.LIVE, created_at__lt=now - timedelta(days=2)).count()
    if awaiting and stale:
        text = (f"Kuna rasimu {awaiting} zinazosubiri idhini yako, na kazi {stale} zimekaa zaidi "
                "ya siku mbili. Nimewakumbusha wahusika — tukianza na zilizo juu, tutamaliza leo.")
    elif awaiting:
        text = (f"Timu imeandaa rasimu {awaiting}. Zipitie ukipata nafasi — zikishakubaliwa, "
                "wateja wanazipokea papo hapo.")
    elif Kazi.objects.filter(status=Kazi.OPEN).exists():
        text = "Kila mmoja yuko kwenye kazi yake. Hakuna kinachohitaji uamuzi wako kwa sasa."
    else:
        text = "Mezani hakuna kazi iliyokwama. Tunaendelea kufuatilia data ya JamiiTek kila dakika 30."
    return text, report


def counts(now=None):
    now = now or timezone.now()
    start = timezone.localtime(now).replace(hour=0, minute=0, second=0, microsecond=0)
    return Kazi.objects.aggregate(
        awaiting=Count('pk', filter=Q(status=Kazi.AWAITING)),
        open=Count('pk', filter=Q(status=Kazi.OPEN)),
        done_today=Count('pk', filter=Q(closed_at__gte=start, status__in=[Kazi.SENT, Kazi.DONE])),
        new_today=Count('pk', filter=Q(created_at__gte=start)),
    )
