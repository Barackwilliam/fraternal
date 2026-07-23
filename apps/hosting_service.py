"""
Auto-suspend ya hosting + maintenance mode.

KANUNI KUU:
  • Tatizo la MALIPO (muda umeisha)      → status = suspended
  • Tatizo la KIUFUNDI / kimfumo         → status = maintenance

Hii ni muhimu: mteja hapaswi kuonekana "amesimamishwa" kwa kosa letu.
Kila tovuti inashughulikiwa peke yake — moja ikishindwa, nyingine
zinaendelea.
"""
import logging
from datetime import date

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

# Kama asilimia hii ya tovuti zitashindwa, tunachukulia ni tatizo la kimfumo
SYSTEMIC_FAILURE_RATIO = 0.5


def _notify(website, ntype, subject, message, actor=None):
    """Tuma taarifa kwa mteja. Kamwe isivunje mchakato."""
    try:
        from .management_views import _send_notification
        return _send_notification(website, ntype, subject, message, actor)
    except Exception as e:
        logger.warning('notification failed for %s: %s', website.pk, type(e).__name__)
        return None


def mark_maintenance(website, problem='', actor=None, notify=False, save=True):
    """
    Weka tovuti kwenye matengenezo (tatizo la kwetu, si la mteja).
    Rudisha ujumbe uliowekwa.
    """
    from . import hosting_ai
    _, msg = hosting_ai.maintenance_message(website, problem=problem)

    website.status = 'maintenance'
    website.suspension_message = msg
    website.suspension_reason = (
        f'[SYSTEM] {problem}'.strip() or '[SYSTEM] Technical issue detected.'
    )[:2000]
    if save:
        website.save(update_fields=['status', 'suspension_message', 'suspension_reason'])

    if notify:
        _notify(website, 'maintenance',
                f'Maintenance — {website.name}',
                f'Dear {website.client.name},\n\n{msg}\n\nJamiiTek Team',
                actor)
    return msg


def suspend_website(website, days_overdue=0, actor=None, notify=True):
    """
    Simamisha tovuti kwa sababu ya muda wa hosting kuisha.
    Rudisha dict ya taarifa.
    """
    from . import hosting_ai

    ai_ok_reason, reason = hosting_ai.suspension_reason(website, days_overdue)
    ai_ok_msg, message = hosting_ai.suspension_message(website, days_overdue)

    website.status = 'suspended'
    website.suspension_reason = reason[:2000]
    website.suspension_message = message
    website.save(update_fields=['status', 'suspension_reason', 'suspension_message'])

    if notify:
        _notify(website, 'suspension',
                f'Website Suspended — {website.name}',
                (f'Dear {website.client.name},\n\n{message}\n\n'
                 f'Expired: {website.hosting_end_date:%d %B %Y}\n'
                 f'Monthly cost: TZS {website.monthly_cost:,.0f}\n\n'
                 f'Renew here: https://jamiitek.com/portal/billing/\n\n'
                 f'JamiiTek Team'),
                actor)

    return {
        'website': website,
        'days_overdue': days_overdue,
        'reason': reason,
        'message': message,
        'ai_used': ai_ok_reason or ai_ok_msg,
    }


def find_expired(today=None):
    """Tovuti zinazostahili kusimamishwa leo."""
    from .models import ManagedWebsite
    today = today or date.today()
    return (ManagedWebsite.objects
            .filter(status='active',
                    auto_suspend_on_expiry=True,
                    hosting_end_date__lte=today)
            .select_related('client')
            .order_by('hosting_end_date'))


def run_auto_suspend(dry_run=False, notify=True, actor=None, today=None):
    """
    Endesha mchakato mzima. Rudisha ripoti.

    dry_run=True → inaonyesha itakachofanya bila kubadilisha chochote.
    """
    today = today or date.today()
    started = timezone.now()
    candidates = list(find_expired(today))

    report = {
        'checked': len(candidates),
        'suspended': [],
        'maintenance': [],
        'failed': [],
        'dry_run': dry_run,
        'ai_used': 0,
        'started_at': started,
    }

    if not candidates:
        report['finished_at'] = timezone.now()
        return report

    for website in candidates:
        days_overdue = (today - website.hosting_end_date).days
        try:
            if dry_run:
                report['suspended'].append({
                    'website': website, 'days_overdue': days_overdue,
                    'reason': '(dry run — hakuna kilichobadilishwa)',
                    'message': '', 'ai_used': False,
                })
                continue

            with transaction.atomic():
                result = suspend_website(website, days_overdue,
                                         actor=actor, notify=notify)
            report['suspended'].append(result)
            if result['ai_used']:
                report['ai_used'] += 1

        except Exception as e:
            # Tatizo la kimfumo — SI kosa la mteja. Usimsimamishe.
            logger.exception('auto-suspend failed for website %s', website.pk)
            problem = f'{type(e).__name__}: {e}'[:300]
            report['failed'].append({'website': website, 'error': problem})
            try:
                mark_maintenance(website, problem=problem, actor=actor, notify=False)
                report['maintenance'].append({'website': website, 'problem': problem})
            except Exception:
                logger.exception('could not set maintenance for website %s', website.pk)

    # Kama nyingi zimeshindwa, kuna tatizo kubwa la kimfumo
    if candidates and len(report['failed']) / len(candidates) >= SYSTEMIC_FAILURE_RATIO:
        report['systemic_failure'] = True
        logger.error('Systemic failure during auto-suspend: %d/%d failed',
                     len(report['failed']), len(candidates))

    report['finished_at'] = timezone.now()
    return report


def format_report(report):
    """Ripoti ya maandishi (kwa console au email)."""
    lines = []
    mode = ' [DRY RUN]' if report.get('dry_run') else ''
    lines.append(f'Auto-suspend{mode} — checked {report["checked"]} website(s)')

    if report['suspended']:
        lines.append(f'\nSuspended ({len(report["suspended"])}):')
        for r in report['suspended']:
            w = r['website']
            lines.append(f'  • {w.name} — {w.client.name} '
                         f'(expired {w.hosting_end_date:%d %b %Y}, '
                         f'{r["days_overdue"]} day(s) overdue)')

    if report['maintenance']:
        lines.append(f'\nSet to maintenance — system issue ({len(report["maintenance"])}):')
        for r in report['maintenance']:
            lines.append(f'  • {r["website"].name} — {r["problem"]}')

    if report.get('systemic_failure'):
        lines.append('\n⚠ SYSTEMIC FAILURE: most websites failed to process. '
                     'Check logs and the database connection.')

    if not report['suspended'] and not report['maintenance']:
        lines.append('\nNothing to do — no expired websites.')

    if report.get('ai_used'):
        lines.append(f'\nAI wrote notices for {report["ai_used"]} website(s).')

    return '\n'.join(lines)
