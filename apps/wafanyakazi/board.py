"""
Ubao wa kazi — jinsi wafanyakazi wanavyoandika na kufunga kazi.

    found(...)   hali imeonekana: unda kazi (mara moja tu kwa `key`)
    settle(...)  hali haipo tena (invoice imelipwa, lead imegeuzwa proposal):
                 funga kazi zake zilizobaki wazi
"""
from django.conf import settings
from django.utils import timezone

from .models import Kazi


def site(path=''):
    base = (getattr(settings, 'SITE_URL', '') or 'https://www.jamiitek.com').rstrip('/')
    return f'{base}{path}'


def found(worker, key, title, *, draft=None, **fields):
    """
    Rudisha (kazi, imeundwa_sasa).

    `draft` inaweza kuwa callable — inaitwa TU kazi inapoundwa, ili AI
    isiitwe kila mzunguko kwa kazi ileile. Kazi yenye rasimu inaanza
    ikisubiri idhini; isiyo na rasimu inaanza wazi.
    """
    kazi = Kazi.objects.filter(key=key).first()
    if kazi:
        if kazi.is_live:
            changed = []
            for name in ('title', 'detail', 'priority', 'link'):
                value = title if name == 'title' else fields.get(name)
                if value is not None and getattr(kazi, name) != value:
                    setattr(kazi, name, value)
                    changed.append(name)
            if changed:
                kazi.save(update_fields=changed + ['updated_at'])
        return kazi, False

    text = draft() if callable(draft) else (draft or '')
    subject = ''
    if isinstance(text, tuple):
        subject, text = text
    kazi = Kazi.objects.create(
        worker=worker, key=key, title=title[:200], draft=text or '', subject=subject[:200],
        status=Kazi.AWAITING if text else Kazi.OPEN, **fields)
    return kazi, True


def settle(worker, prefix, seen, result='Hali imebadilika — haihitajiki tena.'):
    """Funga kazi hai za `worker` zenye `key` inayoanza na `prefix` ambazo hazikuonekana."""
    stale = (Kazi.objects.filter(worker=worker, key__startswith=prefix, status__in=Kazi.LIVE)
             .exclude(key__in=list(seen)))
    count = 0
    for kazi in stale:
        kazi.close(Kazi.DONE, result)
        count += 1
    return count


def money(value, currency='TZS'):
    try:
        return f'{currency} {float(value):,.0f}'
    except (TypeError, ValueError):
        return f'{currency} {value}'


def now_local(now=None):
    return timezone.localtime(now) if now else timezone.localtime()
