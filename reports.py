"""
Ripoti ya mwezi kwa mteja — PDF.

Hii ndiyo bidhaa halisi ya retainer. Mteja anayeona "uptime 99.8%,
backups 30, hakuna tatizo" haulizi tena kwa nini analipa kila mwezi.

Hakuna jina la provider popote kwenye PDF.

    python manage.py monthly_report --website 3
    python manage.py monthly_report --all --month 2026-07
"""
import calendar
import io
import logging
from datetime import date, timedelta

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from .integrations import base
from .live_config import live_config
from .models import IntegrationSnapshot

logger = logging.getLogger(__name__)

INK = colors.HexColor('#1a1a1a')
MUTED = colors.HexColor('#6b6b6b')
LINE = colors.HexColor('#e0e0e0')
GOOD = colors.HexColor('#0f8a5f')
WARN = colors.HexColor('#b8860b')


def month_bounds(when=None):
    when = when or timezone.now().date()
    first = when.replace(day=1)
    last = when.replace(day=calendar.monthrange(when.year, when.month)[1])
    return first, last


def uptime_for(website, start, end):
    """Uptime ya kipindi maalum kutoka snapshots."""
    snaps = IntegrationSnapshot.objects.filter(
        integration__website=website,
        integration__provider='render',
        checked_at__date__gte=start,
        checked_at__date__lte=end,
    ).values_list('metrics', flat=True)

    total = up = 0
    incidents = 0
    prev_ok = True
    for m in snaps:
        st = (m or {}).get(base.HOSTING_STATUS)
        if not st:
            continue
        total += 1
        ok = st in ('online', 'building')
        if ok:
            up += 1
        elif prev_ok:
            incidents += 1
        prev_ok = ok

    if total < 5:
        return None, 0
    return round(up * 100.0 / total, 2), incidents


def _styles():
    ss = getSampleStyleSheet()
    return {
        'h1': ParagraphStyle('h1', parent=ss['Title'], fontSize=20,
                             textColor=INK, spaceAfter=2, alignment=0),
        'sub': ParagraphStyle('sub', parent=ss['Normal'], fontSize=10,
                              textColor=MUTED, spaceAfter=14),
        'h2': ParagraphStyle('h2', parent=ss['Heading2'], fontSize=12,
                             textColor=INK, spaceBefore=14, spaceAfter=6),
        'body': ParagraphStyle('body', parent=ss['Normal'], fontSize=9.5,
                               textColor=INK, leading=14),
        'big': ParagraphStyle('big', parent=ss['Normal'], fontSize=26,
                              textColor=GOOD, alignment=TA_CENTER, leading=30),
        'biglbl': ParagraphStyle('biglbl', parent=ss['Normal'], fontSize=8,
                                 textColor=MUTED, alignment=TA_CENTER),
        'foot': ParagraphStyle('foot', parent=ss['Normal'], fontSize=8,
                               textColor=MUTED, alignment=TA_CENTER),
    }


def build_pdf(website, when=None):
    """Rudisha bytes za PDF."""
    start, end = month_bounds(when)
    cfg = live_config(website)
    st = _styles()

    uptime, incidents = uptime_for(website, start, end)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, title=f'{website.name} — {start:%B %Y}',
        author='JamiiTek', leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=16 * mm)

    flow = [
        Paragraph('JamiiTek — Service Report', st['h1']),
        Paragraph(f'{website.name} &nbsp;·&nbsp; {website.client.name} '
                  f'&nbsp;·&nbsp; {start:%B %Y}', st['sub']),
    ]

    # ── Namba tatu kubwa ──
    cells = [
        (f'{uptime}%' if uptime is not None else '—', 'Uptime'),
        (str(incidents), 'Incidents'),
        (f'{int(cfg.monthly_visits):,}' if cfg.monthly_visits else '—', 'Visitors'),
    ]
    tbl = Table([[Paragraph(v, st['big']) for v, _ in cells],
                 [Paragraph(l, st['biglbl']) for _, l in cells]],
                colWidths=[56 * mm] * 3)
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 12),
        ('LINEBELOW', (0, 1), (-1, 1), 0.6, LINE),
    ]))
    flow += [tbl, Spacer(1, 6)]

    # ── Huduma ──
    rows = [['Service', 'Status']]
    rows.append(['Website hosting', cfg.status_label.title()])

    if cfg.ssl_expiry_date:
        rows.append(['Security certificate (SSL)',
                     f'Active · renews {cfg.ssl_expiry_date:%d %b %Y}'])
    if cfg.last_backup:
        lb = cfg.last_backup
        rows.append(['Database backup',
                     f'Last: {lb:%d %b %Y}' if hasattr(lb, 'strftime') else f'Last: {lb}'])
    if cfg.db_size_display:
        rows.append(['Database size', cfg.db_size_display])
    if cfg.media_display:
        rows.append(['Media storage', cfg.media_display])

    dom = website.domains.first()
    exp = website.resolve(base.DOMAIN_EXPIRY).value or (dom.expiry_date if dom else None)
    if dom and exp:
        exp_s = exp.strftime('%d %b %Y') if hasattr(exp, 'strftime') else str(exp)
        rows.append([f'Domain — {dom.domain_name}', f'Active until {exp_s}'])

    t = Table(rows, colWidths=[80 * mm, 88 * mm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, 0), MUTED),
        ('TEXTCOLOR', (0, 1), (-1, -1), INK),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, LINE),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    flow += [Paragraph('Services', st['h2']), t]

    # ── Muhtasari ──
    if uptime is None:
        summary = ('Monitoring for this site was set up recently. Full uptime '
                   'figures will appear in next month&rsquo;s report.')
    elif incidents == 0:
        summary = (f'Your website ran without interruption for the whole of '
                   f'{start:%B}. No action was needed on your side.')
    else:
        summary = (f'Your website recorded {incidents} brief '
                   f'{"interruption" if incidents == 1 else "interruptions"} '
                   f'during {start:%B}, each resolved by our team. Overall '
                   f'availability was {uptime}%.')

    flow += [Paragraph('Summary', st['h2']),
             Paragraph(summary, st['body']), Spacer(1, 10)]

    # ── Bili ──
    days_left = (website.hosting_end_date - timezone.now().date()).days
    bill = (f'Your service is paid until '
            f'<b>{website.hosting_end_date:%d %B %Y}</b> ({days_left} days '
            f'remaining).' if days_left > 0 else
            '<b>Your service period has ended.</b> Please contact us to renew.')
    flow += [Paragraph('Billing', st['h2']), Paragraph(bill, st['body'])]

    flow += [Spacer(1, 18),
             Paragraph('Generated by JamiiTek &nbsp;·&nbsp; '
                       'Dar es Salaam, Tanzania &nbsp;·&nbsp; '
                       f'{timezone.now():%d %B %Y}', st['foot'])]

    doc.build(flow)
    return buf.getvalue()


def filename(website, when=None):
    start, _ = month_bounds(when)
    slug = ''.join(c if c.isalnum() else '-' for c in website.name.lower())
    return f'{slug}-{start:%Y-%m}-report.pdf'
