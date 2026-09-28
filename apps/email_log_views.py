"""Ukurasa wa /manage/emails/ — kufuatilia kila barua inayotoka.

Swali lililozaa ukurasa huu: "nitajuaje barua imetumwa kwa mteja na
imemfikia?"

Kabla ya hapa, jibu lilikuwa logs za Render — ambazo zinafutwa, na
huwezi kuzitafuta kwa jina la mteja. Na hata hizo zilikuambia tu kwamba
Brevo ameipokea barua, si kwamba imefika kwa mteja.

Sasa: kila barua inahifadhiwa inapotumwa, na Brevo anaturudishia hatima
yake kwa webhook. Hapa unaiona yote mahali pamoja.
"""
import logging
import os
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import EmailLog
from .management_views import staff_member_required


@staff_member_required
def email_log_list(request):
    qs = EmailLog.objects.select_related('client', 'website')

    # ── Kuchuja ────────────────────────────────────────────────
    status = (request.GET.get('status') or '').strip()
    category = (request.GET.get('category') or '').strip()
    days = (request.GET.get('days') or '30').strip()
    q = (request.GET.get('q') or '').strip()

    if status == 'problem':
        qs = qs.filter(status__in=['bounced', 'spam', 'blocked', 'error'])
    elif status:
        qs = qs.filter(status=status)

    if category:
        qs = qs.filter(category=category)

    if days.isdigit() and int(days) > 0:
        qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=int(days)))

    if q:
        qs = qs.filter(
            Q(to_email__icontains=q) |
            Q(subject__icontains=q) |
            Q(client__name__icontains=q) |
            Q(website__name__icontains=q)
        )

    # ── Takwimu (swali MOJA, si moja kwa kila hali) ────────────
    window = timezone.now() - timedelta(days=int(days) if days.isdigit() else 30)
    base = EmailLog.objects.filter(created_at__gte=window)
    stats = base.aggregate(
        total=Count('pk'),
        delivered=Count('pk', filter=Q(status__in=['delivered', 'opened', 'clicked'])),
        opened=Count('pk', filter=Q(status__in=['opened', 'clicked'])),
        problem=Count('pk', filter=Q(status__in=['bounced', 'spam', 'blocked', 'error'])),
        pending=Count('pk', filter=Q(status__in=['sent', 'deferred'])),
    )
    total = stats['total'] or 0
    stats['delivered_pct'] = round(stats['delivered'] * 100 / total) if total else 0
    stats['opened_pct'] = round(stats['opened'] * 100 / total) if total else 0

    # Anwani zenye matatizo — hizi ndizo zinazohitaji hatua yako
    problem_addresses = (base
                         .filter(status__in=['bounced', 'blocked', 'error'])
                         .values('to_email')
                         .annotate(n=Count('pk'))
                         .order_by('-n')[:8])

    page = Paginator(qs, 50).get_page(request.GET.get('page'))

    return render(request, 'management/email_logs.html', {
        'title': 'Email Delivery',
        'nav': 'emails',
        'page_obj': page,
        'logs': page.object_list,
        'stats': stats,
        'problem_addresses': problem_addresses,
        'categories': (EmailLog.objects.exclude(category='')
                       .values_list('category', flat=True).distinct().order_by('category')),
        'f': {'status': status, 'category': category, 'days': days, 'q': q},
        'webhook_ready': EmailLog.objects.exclude(message_id='').exists(),
        'diag': _diagnostics(),
    })


def _mask(value):
    """Onyesha herufi 4 za mwanzo na 4 za mwisho — kulinganisha bila kufichua."""
    v = (value or '').strip()
    if not v:
        return ''
    return v if len(v) <= 10 else f'{v[:4]}…{v[-4:]}'


def _diagnostics():
    """Hali ya usanidi wa barua, bila kuhitaji Render Shell.

    Kila tatizo tulilokutana nalo hapa lilikuwa la usanidi, si la code:
    token ya webhook isiyolingana, ALERT_EMAIL yenye typo. Zote
    zinaonekana hapa kwa mtazamo mmoja.
    """
    backend = getattr(settings, 'EMAIL_BACKEND', '')
    token = os.getenv('BREVO_WEBHOOK_TOKEN', '')
    alert = (os.getenv('ALERT_EMAIL', '') or os.getenv('EMAIL_HOST_USER', '')).strip()
    return {
        'backend': backend.rsplit('.', 1)[-1],
        'is_brevo': 'Brevo' in backend,
        'api_key': bool(getattr(settings, 'BREVO_API_KEY', '')),
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
        'webhook_token': _mask(token),
        'token_len': len(token.strip()),
        'token_has_space': token != token.strip() or ' ' in token,
        'alert_email': alert,
        # Sifuri badala ya herufi O ni typo inayoonekana kama sahihi
        'alert_suspicious': bool(alert) and ('0@' in alert or alert.split('@')[0].endswith('0')),
    }


@staff_member_required
@require_POST
def email_send_test(request):
    """Tuma barua ya majaribio kutoka production — mbadala wa Render Shell."""
    to = (request.POST.get('to') or '').strip()
    if '@' not in to:
        messages.error(request, 'Weka anwani sahihi ya email.')
        return redirect('email_log_list')
    try:
        n = send_mail(
            subject='Jaribio la JamiiTek — ufuatiliaji wa barua',
            message=(
                'Hii ni barua ya majaribio kutoka /manage/emails/.\n\n'
                'Ukiipokea, kutuma kunafanya kazi. Ndani ya dakika moja, '
                'hali yake kwenye ukurasa inapaswa kubadilika kutoka '
                '"Imetumwa" kwenda "Imefika" — hiyo inathibitisha webhook.'
            ),
            from_email=None,
            recipient_list=[to],
            fail_silently=False,
        )
        if n:
            messages.success(request, f'Barua imetumwa kwa {to}. Angalia hali yake kwenye orodha hapa chini.')
        else:
            messages.error(request, 'Backend imerudisha 0 — hakuna barua iliyotumwa. Angalia usanidi hapo juu.')
    except Exception as exc:
        logging.getLogger(__name__).exception('Barua ya majaribio imeshindwa')
        # Ni ukurasa wa staff pekee: kosa kamili linasaidia, halifichui kitu kwa umma
        messages.error(request, f'Imeshindwa: {type(exc).__name__}: {exc}')
    return redirect('email_log_list')
