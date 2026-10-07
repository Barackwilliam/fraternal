"""
Mzunguko mmoja wa timu.

    Diana → Selvester → Ibrahimu → Grace   (wanagundua kazi, wanaandaa rasimu)
    → rasimu mpya zinapelekwa wILife kuomba idhini
    → William (kumbusho na ripoti)

Unaanzishwa na:
  • DailyTasksMiddleware — kila dakika 30 mtu anapotembelea tovuti
  • /tasks/wafanyakazi/?token=TASKS_TOKEN — cron-job.org (inapendekezwa)
  • kitufe cha "Endesha sasa" kwenye /manage/wafanyakazi/ au API ya wILife
  • `python manage.py wafanyakazi`
"""
import importlib
import logging
import threading

from django.core.cache import cache
from django.db import connection
from django.utils import timezone

from . import ai
from .models import Alama, Kazi
from .team import ORDER

logger = logging.getLogger(__name__)

LOCK = 'jamiitek:wafanyakazi:lock'
LOCK_TTL = 10 * 60
PUSH_PER_RUN = 5


def _push_approvals():
    from .wilife import is_configured, push_approval

    if not is_configured():
        return 0
    pushed = 0
    qs = (Kazi.objects.filter(status=Kazi.AWAITING, pushed_at__isnull=True,
                              channel__in=['email', 'whatsapp', 'faq'])
          .order_by('priority', 'created_at')[:PUSH_PER_RUN])
    for kazi in qs:
        if push_approval(kazi):
            pushed += 1
        else:
            break   # wILife haipatikani — tutajaribu mzunguko ujao
    return pushed


def run_all(now=None, force_report=None):
    """Endesha timu nzima mara moja. Rudisha muhtasari (dict)."""
    if not cache.add(LOCK, '1', LOCK_TTL):
        return {'status': 'already_running'}
    now = timezone.localtime(now) if now else timezone.localtime()
    ai.reset_budget()
    summary = {'status': 'ok', 'at': now.isoformat(timespec='seconds')}
    try:
        for slug in ORDER:
            if slug == 'william':
                try:
                    summary['approvals_pushed'] = _push_approvals()
                except Exception:
                    logger.exception('[wafanyakazi] kupeleka idhini wILife')
            module = importlib.import_module(f'apps.wafanyakazi.{slug}')
            try:
                if slug == 'william':
                    summary[slug] = module.run(now, force_report=force_report)
                else:
                    summary[slug] = module.run(now)
                Alama.put(f'run:{slug}', now.isoformat(timespec='seconds'))
            except Exception as exc:
                logger.exception('[wafanyakazi] %s ameshindwa', slug)
                summary[slug] = {'error': f'{type(exc).__name__}: {exc}'[:300]}
                Alama.put(f'error:{slug}', f"{now:%d/%m %H:%M} {type(exc).__name__}: {exc}")
        Alama.put('run:last', now.isoformat(timespec='seconds'))
    finally:
        cache.delete(LOCK)
    return summary


def run_in_background(**kwargs):
    def target():
        try:
            run_all(**kwargs)
        except Exception:
            logger.exception('[wafanyakazi] mzunguko wa nyuma')
        finally:
            connection.close()

    threading.Thread(target=target, name='jamiitek-wafanyakazi', daemon=True).start()
