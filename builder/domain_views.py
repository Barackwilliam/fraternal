"""/manage/site-domains/ — wewe unaunganisha website ya builder na domain ya mteja."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.management_views import staff_member_required
from builder import domains
from builder.models import ClientWebsite


@staff_member_required
def domain_list(request):
    connected = (ClientWebsite.objects.exclude(custom_domain__isnull=True)
                 .exclude(custom_domain='').select_related('owner')
                 .order_by('domain_status', '-domain_added_at'))
    q = (request.GET.get('q') or '').strip()
    sites = ClientWebsite.objects.select_related('owner').order_by('site_name')
    if q:
        sites = sites.filter(Q(site_name__icontains=q) | Q(subdomain__icontains=q)
                             | Q(owner__username__icontains=q) | Q(owner__email__icontains=q))

    rows = [{'site': s, 'records': domains.dns_records(s.custom_domain)} for s in connected]
    counts = {k: sum(1 for r in rows if r['site'].domain_status == k)
              for k in ('active', 'dns_ok', 'pending', 'error')}
    return render(request, 'management/site_domains.html', {
        'title': 'Site Domains',
        'nav': 'site_domains',
        'rows': rows,
        'counts': counts,
        'sites': sites[:200],
        'q': q,
        'render_ip': domains.RENDER_APEX_IP,
        'render_host': domains.RENDER_HOST,
    })


@staff_member_required
@require_POST
def domain_connect(request):
    site = get_object_or_404(ClientWebsite, pk=request.POST.get('site'))
    ok, msg = domains.connect(site, request.POST.get('domain', ''))
    (messages.success if ok else messages.error)(request, msg)
    if ok:
        domains.check(site)          # onyesha hali halisi mara moja
    return redirect('site_domain_list')


@staff_member_required
@require_POST
def domain_check(request, pk):
    site = get_object_or_404(ClientWebsite, pk=pk)
    status, msg = domains.check(site)
    level = messages.success if status == 'active' else (
        messages.error if status == 'error' else messages.info)
    level(request, f'{site.custom_domain}: {msg}')
    return redirect('site_domain_list')


@staff_member_required
@require_POST
def domain_reregister(request, pk):
    """Sajili tena kwenye Render — kama usajili wa kwanza ulishindwa."""
    from builder import render_api
    site = get_object_or_404(ClientWebsite, pk=pk)
    ok, msg = render_api.add_custom_domain(site.custom_domain)
    (messages.success if ok else messages.error)(request, msg)
    return redirect('site_domain_list')


@staff_member_required
@require_POST
def domain_disconnect(request, pk):
    site = get_object_or_404(ClientWebsite, pk=pk)
    old = site.custom_domain
    domains.disconnect(site)
    messages.success(request, f'{old} imeondolewa. Website inaendelea kwenye {site.subdomain}.jamiitek.com.')
    return redirect('site_domain_list')
