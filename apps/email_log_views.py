"""Ukurasa wa /manage/emails/ — kufuatilia kila barua inayotoka.

Swali lililozaa ukurasa huu: "nitajuaje barua imetumwa kwa mteja na
imemfikia?"

Kabla ya hapa, jibu lilikuwa logs za Render — ambazo zinafutwa, na
huwezi kuzitafuta kwa jina la mteja. Na hata hizo zilikuambia tu kwamba
Brevo ameipokea barua, si kwamba imefika kwa mteja.

Sasa: kila barua inahifadhiwa inapotumwa, na Brevo anaturudishia hatima
yake kwa webhook. Hapa unaiona yote mahali pamoja.
"""
from datetime import timedelta

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone

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
    })
