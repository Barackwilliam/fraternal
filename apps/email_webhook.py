"""Webhook ya Brevo — hatima halisi ya kila barua.

Code yetu inajua tu kwamba Brevo ameipokea barua. Kilichotokea baadaye
— imeingia inbox, imefunguliwa, imerudi (bounce), au imeingia spam —
anakijua Brevo pekee, na anatuambia hapa.

KUSANIDI (mara moja)

    Brevo > Settings > Webhooks > Add a webhook
    URL:  https://www.jamiitek.com/webhooks/brevo/?token=<BREVO_WEBHOOK_TOKEN>
    Chagua: Sent, Delivered, Opened, Clicked, Soft bounce, Hard bounce,
            Invalid email, Deferred, Spam, Blocked, Error

    Kisha weka BREVO_WEBHOOK_TOKEN kwenye Render.

MAMBO MAWILI YA MUHIMU

1. Brevo HURUDIA matukio (inajaribu tena ikipata 5xx, na inaweza
   kutuma tukio lile lile mara mbili). `apply_event` imeandikwa
   kuwa salama kurudiwa.

2. Sehemu ya message id inaitwa `message-id` (yenye kistari) kwenye
   matukio ya transactional. Tunakubali majina kadhaa kwa usalama.
"""
import json
import logging
import os
from datetime import datetime, timezone as dt_timezone

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger('jamiitek.email')

# Majina yanayoweza kubeba message id kwenye payload
_ID_KEYS = ('message-id', 'messageId', 'message_id', 'messageid')


def _message_id(payload):
    for k in _ID_KEYS:
        val = payload.get(k)
        if val:
            return str(val).strip()
    return ''


def _timestamp(payload):
    """`ts` (sekunde), `ts_event`, au `date` kama maandishi."""
    for key in ('ts_event', 'ts', 'ts_epoch'):
        raw = payload.get(key)
        if raw:
            try:
                secs = int(raw)
                if secs > 10_000_000_000:        # millisekunde
                    secs //= 1000
                return datetime.fromtimestamp(secs, tz=dt_timezone.utc)
            except (TypeError, ValueError):
                pass
    raw = payload.get('date') or payload.get('date_event')
    if raw:
        from django.utils.dateparse import parse_datetime
        parsed = parse_datetime(str(raw))
        if parsed:
            return parsed
    from django.utils import timezone as tz
    return tz.now()


@csrf_exempt
@require_POST
def brevo_webhook(request):
    from apps.models import EmailLog

    expected = os.getenv('BREVO_WEBHOOK_TOKEN', '')
    if expected and request.GET.get('token') != expected:
        logger.warning('[brevo-webhook] token si sahihi')
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)

    try:
        data = json.loads(request.body or b'{}')
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'invalid json'}, status=400)

    # Brevo inaweza kutuma tukio moja au orodha ya matukio
    events = data if isinstance(data, list) else [data]
    applied = unknown = 0

    for payload in events:
        if not isinstance(payload, dict):
            continue
        event = (payload.get('event') or '').strip()
        email = (payload.get('email') or '').strip()
        mid = _message_id(payload)
        reason = (payload.get('reason') or payload.get('error')
                  or payload.get('description') or '')

        log = None
        if mid:
            log = EmailLog.objects.filter(message_id=mid).order_by('-created_at').first()
        if log is None and email:
            # Barua za zamani (kabla ya kuhifadhi message_id) — tumia
            # barua ya mwisho kwa anwani hiyo.
            log = (EmailLog.objects
                   .filter(to_email__iexact=email)
                   .order_by('-created_at').first())
            if log and mid and not log.message_id:
                log.message_id = mid[:255]
                log.save(update_fields=['message_id'])

        if log is None:
            unknown += 1
            continue

        if log.apply_event(event, at=_timestamp(payload), reason=reason):
            applied += 1

    # Daima 200: jibu la 5xx linamfanya Brevo arudie tukio lile lile
    # bila kikomo, na tukio lisilojulikana si hitilafu yetu.
    return JsonResponse({'ok': True, 'applied': applied, 'unknown': unknown})
