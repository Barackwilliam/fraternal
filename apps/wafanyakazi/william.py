"""
William — Kiongozi mkuu.

Anafanya kazi wa mwisho kila mzunguko:

  • Kumbusho: kazi iliyokaa wazi zaidi ya siku 2 → anamkumbusha mhusika
    (inaonekana kwenye panel na kwenye ripoti), mara moja kwa siku
  • Asubuhi (WORKERS_MORNING_HOUR, saa 1): mpango wa siku — zinazosubiri
    idhini, hali ya kila mfanyakazi, post ya Grace tayari kunakiliwa
  • Jioni (WORKERS_EVENING_HOUR, saa 12): kilichofanyika leo na kilichobaki

Ripoti zinakufikia kupitia wILife (au apps.notify kama wILife haijawekwa).
"""
import os
from datetime import timedelta

from django.db.models import Count, Q

from . import ai, diana
from .board import money, site
from .models import Kazi, Ripoti
from .team import ORDER, TEAM, member

SLUG = 'william'
STALE = timedelta(days=2)
SW_DAYS = ['Jumatatu', 'Jumanne', 'Jumatano', 'Alhamisi', 'Ijumaa', 'Jumamosi', 'Jumapili']


def _hour(name, default):
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def snapshot(now=None):
    """Hali ya kila mfanyakazi — kwa panel, API na ripoti."""
    rows = {r['worker']: r for r in Kazi.objects.values('worker').annotate(
        open=Count('pk', filter=Q(status=Kazi.OPEN)),
        awaiting=Count('pk', filter=Q(status=Kazi.AWAITING)),
        stale=Count('pk', filter=Q(status__in=Kazi.LIVE,
                                   created_at__lt=(now or _now()) - STALE)),
    )}
    out = []
    for slug in ORDER:
        info = dict(TEAM[slug], slug=slug)
        info.update({k: rows.get(slug, {}).get(k, 0) for k in ('open', 'awaiting', 'stale')})
        out.append(info)
    # William anaonyeshwa kwanza
    return [out[-1]] + out[:-1]


def _now():
    from django.utils import timezone
    return timezone.localtime()


def _remind(now):
    """Kazi zilizokwama: mkumbushe mhusika mara moja kwa siku."""
    due = Kazi.objects.filter(status__in=Kazi.LIVE, created_at__lt=now - STALE).filter(
        Q(reminded_at__isnull=True) | Q(reminded_at__lt=now - timedelta(days=1)))
    per_worker = {}
    for kazi in due:
        kazi.reminded_at = now
        kazi.reminders += 1
        kazi.save(update_fields=['reminded_at', 'reminders'])
        per_worker[kazi.worker] = per_worker.get(kazi.worker, 0) + 1
    return per_worker


def _stale_lines(now):
    rows = (Kazi.objects.filter(status__in=Kazi.LIVE, created_at__lt=now - STALE)
            .values('worker').annotate(n=Count('pk')))
    return [f"  • {member(r['worker'])['name']}: kazi {r['n']} zimekaa zaidi ya siku 2"
            for r in rows]


def _awaiting_lines(limit=8):
    lines = []
    qs = Kazi.objects.filter(status=Kazi.AWAITING).exclude(channel='social').order_by('priority', 'created_at')
    for kazi in qs[:limit]:
        code = f" — *OK {kazi.wilife_code}*" if kazi.wilife_code else ''
        lines.append(f"  • [{member(kazi.worker)['name']}] {kazi.title}{code}")
    extra = qs.count() - limit
    if extra > 0:
        lines.append(f"  • …na nyingine {extra}")
    return lines


def _count(worker, prefix=None, status=Kazi.LIVE):
    qs = Kazi.objects.filter(worker=worker, status__in=status)
    return qs.filter(key__startswith=prefix).count() if prefix else qs.count()


def morning_report(now):
    day = f"{SW_DAYS[now.weekday()]} {now:%d/%m/%Y}"
    lines = [f"👔 *William — Mpango wa leo*", f"_{day}_", ""]

    awaiting = _awaiting_lines()
    if awaiting:
        lines += [f"✍️ *Zinasubiri idhini yako ({Kazi.objects.filter(status=Kazi.AWAITING).exclude(channel='social').count()})*"]
        lines += awaiting + [""]

    try:
        n = diana.numbers(now)
        lines += ["💰 *Diana · Fedha*",
                  f"  • Invoice zilizochelewa: {n['overdue_count']} · deni lote {money(n['outstanding'])}",
                  f"  • Siku 7: Pesapal {money(n['online_week'])} · invoice zilizolipwa {money(n['invoices_paid_week'])}",
                  f"  • Malipo ya JamiiBot ya kuthibitisha: {_count('diana', 'diana:botpay:')}",
                  ""]
    except Exception:
        lines += ["💰 *Diana · Fedha*", f"  • Kazi wazi: {_count('diana')}", ""]

    lines += ["🎯 *Selvester · Mauzo*",
              f"  • Leads za kufuatilia: {_count('selvester', 'selv:lead:')}",
              f"  • Ujumbe wa fomu: {_count('selvester', 'selv:contact:')} · "
              f"wateja wa JamiiBot: {_count('selvester', 'selv:chat:')}",
              f"  • Malipo yaliyoachwa: {_count('selvester', 'selv:pay:')} · "
              f"tovuti ambazo hazijachapishwa: {_count('selvester', 'selv:site:')}",
              "",
              "💬 *Ibrahimu · Huduma kwa wateja*",
              f"  • Wanaosubiri binadamu: {_count('ibrahimu', 'ibra:handoff:')}",
              f"  • Maswali ambayo bot haikujua: {_count('ibrahimu', 'ibra:gap:')}",
              ""]

    post = (Kazi.objects.filter(worker='grace', status__in=Kazi.LIVE, key__startswith='grace:post:')
            .order_by('-created_at').first())
    if post and post.draft:
        lines += ["📣 *Grace · Post ya leo*", "────────────", post.draft, "────────────", ""]

    stale = _stale_lines(now)
    if stale:
        lines += ["⏰ *Nimewakumbusha*"] + stale + [""]

    focus = ai.write(
        ai.persona('William', 'kiongozi mkuu wa timu ya AI'),
        "Hii ni hali ya timu leo:\n" + "\n".join(lines[3:]) +
        "\n\nAndika sentensi 1-2 tu: kipaumbele kikuu cha mmiliki leo ni kipi na kwa nini.",
        max_tokens=120, temperature=0.3)
    if focus:
        lines[2:2] = [f"🎯 *Kipaumbele:* {focus}", ""]

    lines.append(f"Panel ya timu: {site('/manage/wafanyakazi/')}")
    return "\n".join(lines).strip()


def evening_report(now):
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    closed = (Kazi.objects.filter(closed_at__gte=start, status__in=[Kazi.SENT, Kazi.DONE])
              .order_by('worker', 'closed_at'))
    new = Kazi.objects.filter(created_at__gte=start).count()
    awaiting = _awaiting_lines()
    if not closed.exists() and not awaiting and not new:
        return ''

    lines = [f"👔 *William — Ripoti ya jioni*", f"_{SW_DAYS[now.weekday()]} {now:%d/%m/%Y}_", ""]
    lines.append(f"Leo timu imeona kazi mpya {new} na kukamilisha {closed.count()}.")
    lines.append("")
    if closed.exists():
        lines.append(f"✅ *Zilizokamilika leo ({closed.count()})*")
        for kazi in closed[:10]:
            lines.append(f"  • [{member(kazi.worker)['name']}] {kazi.title}")
        lines.append("")
    if awaiting:
        lines.append("✍️ *Bado zinasubiri idhini yako*")
        lines += awaiting + [""]
    stale = _stale_lines(now)
    if stale:
        lines += ["⏰ *Zilizokwama*"] + stale + [""]
    lines.append(f"Panel ya timu: {site('/manage/wafanyakazi/')}")
    return "\n".join(lines).strip()


def _send(kind, now, build, force=False):
    from .wilife import deliver_report

    existing = Ripoti.objects.filter(kind=kind, date=now.date())
    if existing.exists():
        if not force:
            return 'tayari'
        existing.delete()
    text = build(now)
    report = Ripoti.objects.create(kind=kind, date=now.date(), text=text or '(hakuna jipya)')
    if not text:
        report.delivered = 'kimya — hakuna jipya'
    else:
        report.delivered = deliver_report(text) or 'haikufika'
    report.save(update_fields=['delivered'])
    return report.delivered


def run(now, force_report=None):
    result = {'reminded': _remind(now)}
    morning, evening = _hour('WORKERS_MORNING_HOUR', 7), _hour('WORKERS_EVENING_HOUR', 18)
    if force_report == 'asubuhi' or (force_report is None and morning <= now.hour < evening):
        result['asubuhi'] = _send('asubuhi', now, morning_report, force=force_report == 'asubuhi')
    if force_report == 'jioni' or (force_report is None and now.hour >= evening):
        result['jioni'] = _send('jioni', now, evening_report, force=force_report == 'jioni')
    return result
