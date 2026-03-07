# apps/management_views.py — JamiiTek Management Panel

import json, secrets
from datetime import date, timedelta
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Sum, Count, Q


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/manage/login/?next={request.path}')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Access denied. Staff accounts only.')
            return redirect('/manage/login/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper

staff_member_required = staff_required

from .models import (
    ManagedWebsite, HostingPayment, WebsiteFeature,
    ScheduledAction, ClientNotification, Client,
    DomainRecord, DomainRenewalPayment,
    EmailHostingPlan, EmailHostingPayment,
)


# ── DASHBOARD ─────────────────────────────────────────────────────

@staff_required
def management_dashboard(request):
    websites = ManagedWebsite.objects.select_related('client').all()
    today = date.today()

    stats = {
        'total': websites.count(),
        'active': websites.filter(status='active').count(),
        'suspended': websites.filter(status='suspended').count(),
        'maintenance': websites.filter(status='maintenance').count(),
        'terminated': websites.filter(status='terminated').count(),
        'revenue_month': HostingPayment.objects.filter(
            payment_date__month=today.month, payment_date__year=today.year
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'revenue_total': HostingPayment.objects.aggregate(total=Sum('amount'))['total'] or 0,
    }

    overdue = [w for w in websites if w.is_overdue and w.status == 'active']
    expiring_soon = [w for w in websites
                     if w.days_until_expiry is not None
                     and 0 <= w.days_until_expiry <= 14 and not w.is_overdue]

    pending_actions = ScheduledAction.objects.filter(
        status='pending').select_related('website').order_by('scheduled_at')[:10]
    recent_notifications = ClientNotification.objects.select_related(
        'client', 'website').order_by('-sent_at')[:8]
    recent_payments = HostingPayment.objects.select_related(
        'website__client').order_by('-payment_date')[:6]

    return render(request, 'management/dashboard.html', {
        'title': 'Dashboard',
        'websites': websites.order_by('-created_at')[:10],
        'stats': stats,
        'overdue': overdue,
        'expiring_soon': expiring_soon,
        'pending_actions': pending_actions,
        'recent_notifications': recent_notifications,
        'recent_payments': recent_payments,
    })


# ── WEBSITE LIST ───────────────────────────────────────────────────

@staff_required
def website_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('q', '')
    websites = ManagedWebsite.objects.select_related('client').all()
    if status_filter:
        websites = websites.filter(status=status_filter)
    if search:
        websites = websites.filter(
            Q(name__icontains=search) | Q(client__name__icontains=search) | Q(url__icontains=search))
    return render(request, 'management/website_list.html', {
        'title': 'All Websites',
        'websites': websites.order_by('name'),
        'status_filter': status_filter,
        'search': search,
        'status_choices': [('', 'All'), ('active', 'Active'), ('suspended', 'Suspended'), ('maintenance', 'Maintenance'), ('terminated', 'Terminated')],
    })


# ── WEBSITE DETAIL ─────────────────────────────────────────────────

@staff_required
def website_detail(request, pk):
    website = get_object_or_404(ManagedWebsite.objects.select_related('client'), pk=pk)
    return render(request, 'management/website_detail.html', {
        'title': website.name,
        'website': website,
        'features': WebsiteFeature.objects.filter(website=website),
        'scheduled': ScheduledAction.objects.filter(website=website, status='pending').order_by('scheduled_at'),
        'payments': HostingPayment.objects.filter(website=website).order_by('-payment_date'),
        'notifications': ClientNotification.objects.filter(website=website).order_by('-sent_at')[:30],
        'action_types': ScheduledAction.ACTION_TYPES,
        'notification_types': ClientNotification.NOTIFICATION_TYPES,
    })


# ── ADD WEBSITE ────────────────────────────────────────────────────

@staff_required
def website_add(request):
    if request.method == 'POST':
        client_id = request.POST.get('client')
        name = request.POST.get('name', '').strip()
        url = request.POST.get('url', '').strip()
        if not all([client_id, name, url,
                    request.POST.get('hosting_start_date'),
                    request.POST.get('hosting_end_date')]):
            messages.error(request, 'Please fill in all required fields.')
        else:
            try:
                website = ManagedWebsite.objects.create(
                    client=Client.objects.get(pk=client_id),
                    name=name, url=url,
                    site_type=request.POST.get('site_type', 'static'),
                    hosting_start_date=request.POST.get('hosting_start_date'),
                    hosting_end_date=request.POST.get('hosting_end_date'),
                    monthly_cost=Decimal(request.POST.get('monthly_cost', 0)),
                    notes=request.POST.get('notes', ''),
                    auto_suspend_on_expiry=request.POST.get('auto_suspend_on_expiry') == 'on',
                    send_expiry_warnings=request.POST.get('send_expiry_warnings') == 'on',
                    status='active',
                )
                messages.success(request, f'Website "{name}" added successfully.')
                return redirect('website_detail', pk=website.pk)
            except Exception as e:
                messages.error(request, f'Error: {e}')
    return render(request, 'management/website_add.html', {
        'title': 'Add Website',
        'clients': Client.objects.all().order_by('name'),
    })


# ── EDIT WEBSITE ───────────────────────────────────────────────────

@staff_required
def website_edit(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    if request.method == 'POST':
        from datetime import datetime
        website.name = request.POST.get('name', website.name).strip()
        website.url = request.POST.get('url', website.url).strip()
        website.site_type = request.POST.get('site_type', website.site_type)
        website.monthly_cost = Decimal(request.POST.get('monthly_cost', website.monthly_cost))
        website.notes = request.POST.get('notes', '')
        website.auto_suspend_on_expiry = request.POST.get('auto_suspend_on_expiry') == 'on'
        website.send_expiry_warnings = request.POST.get('send_expiry_warnings') == 'on'
        end = request.POST.get('hosting_end_date')
        if end:
            website.hosting_end_date = datetime.strptime(end, '%Y-%m-%d').date()
        website.save()
        messages.success(request, 'Website updated.')
        return redirect('website_detail', pk=pk)
    return render(request, 'management/website_edit.html', {
        'title': f'Edit — {website.name}', 'website': website,
        'clients': Client.objects.all().order_by('name'),
    })


# ── SUSPEND ────────────────────────────────────────────────────────

@staff_required
@require_POST
def suspend_website(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    reason = request.POST.get('reason', '').strip()
    msg = request.POST.get('suspension_message', '').strip() or \
        'This website has been suspended. Please contact us for more information.'
    if not reason:
        messages.error(request, 'Suspension reason is required.')
        return redirect('website_detail', pk=pk)
    website.status = 'suspended'
    website.suspension_reason = reason
    website.suspension_message = msg
    website.save()
    if request.POST.get('notify_client') == 'on':
        _send_notification(website, 'suspension',
            f'Website Suspended — {website.name}',
            f'Dear {website.client.name},\n\nYour website ({website.name}) has been suspended.\n\nReason: {reason}\n\n{msg}\n\nContact us to resolve this.\n\nJamiiTek Team',
            request.user)
    messages.success(request, f'"{website.name}" has been suspended.')
    return redirect('website_detail', pk=pk)


# ── RESTORE ────────────────────────────────────────────────────────

@staff_required
@require_POST
def restore_website(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    website.status = 'active'
    website.suspension_reason = ''
    website.suspension_message = ''
    website.save()
    if request.POST.get('notify_client') == 'on':
        _send_notification(website, 'restoration',
            f'Website Restored — {website.name}',
            f'Dear {website.client.name},\n\nYour website ({website.name}) is now live again.\n\nURL: {website.url}\n\nThank you!\n\nJamiiTek Team',
            request.user)
    messages.success(request, f'"{website.name}" restored successfully.')
    return redirect('website_detail', pk=pk)


# ── MAINTENANCE ────────────────────────────────────────────────────

@staff_required
@require_POST
def set_maintenance(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    msg = request.POST.get('maintenance_message', '').strip() or \
        'We are performing scheduled maintenance. We will be back shortly. Thank you for your patience.'
    website.status = 'maintenance'
    website.suspension_message = msg
    website.save()
    if request.POST.get('notify_client') == 'on':
        _send_notification(website, 'maintenance',
            f'Scheduled Maintenance — {website.name}',
            f'Dear {website.client.name},\n\nYour website ({website.name}) is in maintenance mode.\n\nVisitors will see: {msg}\n\nWe will notify you when done.\n\nJamiiTek Team',
            request.user)
    messages.success(request, f'"{website.name}" is in maintenance mode.')
    return redirect('website_detail', pk=pk)


# ── FEATURES ───────────────────────────────────────────────────────

@staff_required
@require_POST
def toggle_feature(request, pk, feature_pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    feature = get_object_or_404(WebsiteFeature, pk=feature_pk, website=website)
    feature.is_enabled = not feature.is_enabled
    feature.save()
    messages.success(request, f'Feature "{feature.feature_name}" {"enabled" if feature.is_enabled else "disabled"}.')
    return redirect('website_detail', pk=pk)


@staff_required
@require_POST
def add_feature(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    feature_key = request.POST.get('feature_key', '').strip().lower().replace(' ', '_')
    feature_name = request.POST.get('feature_name', '').strip()
    if not feature_key or not feature_name:
        messages.error(request, 'Feature key and name are required.')
        return redirect('website_detail', pk=pk)
    _, created = WebsiteFeature.objects.get_or_create(
        website=website, feature_key=feature_key,
        defaults={'feature_name': feature_name, 'is_enabled': True})
    messages.success(request, f'Feature "{feature_name}" {"added" if created else "already exists"}.')
    return redirect('website_detail', pk=pk)


# ── PAYMENTS ───────────────────────────────────────────────────────

@staff_required
@require_POST
def add_payment(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    try:
        from datetime import datetime
        amount = Decimal(request.POST.get('amount', 0))
        payment_date = datetime.strptime(request.POST.get('payment_date'), '%Y-%m-%d').date()
        months_covered = int(request.POST.get('months_covered', 1))
        payment_method = request.POST.get('payment_method', '')
        transaction_ref = request.POST.get('transaction_ref', '').strip()
        extend_hosting = request.POST.get('extend_hosting') == 'on'
        auto_restore = request.POST.get('auto_restore') == 'on'
        notify_client = request.POST.get('notify_client') == 'on'

        HostingPayment.objects.create(
            website=website, amount=amount, payment_date=payment_date,
            months_covered=months_covered, payment_method=payment_method,
            transaction_ref=transaction_ref,
            notes=request.POST.get('notes', ''),
            recorded_by=request.user)

        if extend_hosting and months_covered > 0:
            try:
                from dateutil.relativedelta import relativedelta
                base = website.hosting_end_date if (website.hosting_end_date and website.hosting_end_date >= date.today()) else date.today()
                website.hosting_end_date = base + relativedelta(months=months_covered)
            except ImportError:
                website.hosting_end_date = (website.hosting_end_date or date.today()) + timedelta(days=30 * months_covered)
            website.save()

        if auto_restore and website.status == 'suspended':
            website.status = 'active'
            website.suspension_reason = ''
            website.suspension_message = ''
            website.save()

        if notify_client:
            new_expiry = website.hosting_end_date.strftime('%d %B %Y') if website.hosting_end_date else 'N/A'
            _send_notification(website, 'payment_received',
                f'Payment Received — {website.name}',
                f'Dear {website.client.name},\n\nPayment received!\n\nAmount: TZS {amount:,.0f}\nMethod: {payment_method}\nMonths: {months_covered}\nRef: {transaction_ref or "N/A"}\nValid until: {new_expiry}\n\nThank you!\n\nJamiiTek Team',
                request.user)

        messages.success(request, f'Payment of TZS {amount:,.0f} recorded.')
    except Exception as e:
        messages.error(request, f'Error recording payment: {e}')
    return redirect('website_detail', pk=pk)


# ── SEND NOTIFICATION ──────────────────────────────────────────────

@staff_required
def send_notification(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()
        notification_type = request.POST.get('notification_type', 'general')
        if not subject or not message_body:
            messages.error(request, 'Subject and message are required.')
        else:
            _send_notification(website, notification_type, subject, message_body, request.user)
            messages.success(request, f'Message sent to {website.client.name} successfully.')
        return redirect('website_detail', pk=pk)
    # GET: show dedicated page too (for backwards compat)
    return render(request, 'management/send_notification.html', {
        'title': f'Send Message — {website.name}',
        'website': website,
        'notification_types': ClientNotification.NOTIFICATION_TYPES,
    })


# ── SCHEDULE ACTION ────────────────────────────────────────────────

@staff_required
@require_POST
def schedule_action(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    try:
        from datetime import datetime
        action_type = request.POST.get('action_type')
        scheduled_at = timezone.make_aware(
            datetime.strptime(request.POST.get('scheduled_at'), '%Y-%m-%dT%H:%M'))
        action_data = {
            'reason': request.POST.get('reason', ''),
            'message': request.POST.get('message', ''),
            'notify_client': request.POST.get('notify_client') == 'on',
            'email_subject': request.POST.get('email_subject', ''),
            'email_body': request.POST.get('email_body', ''),
            'feature_key': request.POST.get('feature_key', ''),
        }
        ScheduledAction.objects.create(
            website=website, action_type=action_type,
            scheduled_at=scheduled_at, action_data=action_data,
            created_by=request.user)
        messages.success(request, f'Action scheduled for {scheduled_at.strftime("%d %b %Y %H:%M")}.')
    except Exception as e:
        messages.error(request, f'Error scheduling: {e}')
    return redirect('website_detail', pk=pk)


@staff_required
def cancel_scheduled_action(request, action_pk):
    action = get_object_or_404(ScheduledAction, pk=action_pk)
    wpk = action.website.pk
    action.status = 'cancelled'
    action.save()
    messages.success(request, 'Action cancelled.')
    return redirect('website_detail', pk=wpk)


# ── REGENERATE API KEY ─────────────────────────────────────────────

@staff_required
@require_POST
def regenerate_api_key(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    website.api_key = secrets.token_urlsafe(48)
    website.save()
    messages.success(request, 'API key regenerated. Update the script on the client website.')
    return redirect('website_detail', pk=pk)


# ── CLIENT LIST ────────────────────────────────────────────────────

@staff_required
def client_list(request):
    clients = Client.objects.annotate(
        website_count=Count('managed_websites')).order_by('name')
    return render(request, 'management/client_list.html', {
        'title': 'Clients', 'clients': clients,
    })


@staff_required
def client_detail_admin(request, pk):
    client = get_object_or_404(Client, pk=pk)
    payments = HostingPayment.objects.filter(website__client=client).order_by('-payment_date')
    return render(request, 'management/client_detail.html', {
        'title': client.name, 'client': client,
        'websites': ManagedWebsite.objects.filter(client=client),
        'payments': payments,
        'notifications': ClientNotification.objects.filter(client=client).order_by('-sent_at')[:20],
        'total_revenue': payments.aggregate(total=Sum('amount'))['total'] or 0,
    })


# ── PUBLIC API ─────────────────────────────────────────────────────

@require_GET
def site_status_api(request, api_key):
    try:
        website = ManagedWebsite.objects.get(api_key=api_key)
        data = {
            'status': website.status,
            'is_active': website.is_active,
            'suspension_message': website.suspension_message if not website.is_active else '',
            'features': {f.feature_key: f.is_enabled for f in website.features.all()},
            'site_name': website.name,
        }
        resp = JsonResponse(data)
    except ManagedWebsite.DoesNotExist:
        resp = JsonResponse({'status': 'active', 'is_active': True, 'features': {}})

    resp['Access-Control-Allow-Origin'] = '*'
    resp['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    resp['Cache-Control'] = 'no-store, no-cache'
    return resp


@require_GET
def get_js_snippet(request, api_key):
    try:
        website = ManagedWebsite.objects.get(api_key=api_key)
    except ManagedWebsite.DoesNotExist:
        return HttpResponse("// JamiiTek: Invalid API key", content_type='application/javascript')

    api_url = request.build_absolute_uri(f'/api/site-status/{api_key}/')

    js_code = f"""/* JamiiTek Status Guard v2 — {website.name} */
(function(){{
  'use strict';
  var API='{api_url}';
  var RETRY=3,TIMEOUT=8000;
  var hideStyle=document.createElement('style');
  hideStyle.id='_jt_guard';
  hideStyle.textContent='html{{opacity:0!important;pointer-events:none!important}}';
  (document.head||document.documentElement).appendChild(hideStyle);
  function reveal(){{var s=document.getElementById('_jt_guard');if(s)s.parentNode.removeChild(s);}}
  function showBlock(status,msg){{
    reveal();
    var isMaint=status==='maintenance';
    var icon=isMaint?'🔧':'🔒';
    var title=isMaint?'Under Maintenance':'Service Suspended';
    var accent=isMaint?'#f59e0b':'#ef4444';
    document.documentElement.style.cssText='height:100%;margin:0';
    document.body.style.cssText='margin:0;padding:0;min-height:100vh;background:#0b0f1a;font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;display:flex;align-items:center;justify-content:center';
    document.body.innerHTML='<div style="text-align:center;padding:32px;max-width:520px;width:100%"><div style="display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);padding:7px 16px;border-radius:100px;font-size:12px;color:rgba(255,255,255,0.4);font-weight:600;letter-spacing:0.5px;margin-bottom:32px"><span style="width:7px;height:7px;border-radius:50%;background:'+accent+';display:inline-block"></span>'+(isMaint?'Maintenance Mode':'Suspended')+'</div><div style="font-size:72px;margin-bottom:24px;line-height:1">'+icon+'</div><h1 style="font-size:clamp(22px,4vw,32px);font-weight:800;color:#fff;margin:0 0 16px;letter-spacing:-0.5px">'+title+'</h1><p style="font-size:16px;color:rgba(255,255,255,0.5);line-height:1.7;margin:0 0 32px;max-width:400px;margin-inline:auto">'+((msg&&msg.trim())||'This website is temporarily unavailable. Please contact the administrator.')+'</p><div style="display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border-radius:10px;border:1px solid rgba(255,255,255,0.08);color:rgba(255,255,255,0.25);font-size:13px">Managed by JamiiTek</div></div>';
    document.title=title+' — '+document.title;
  }}
  function check(attempt){{
    var controller=typeof AbortController!=='undefined'?new AbortController():null;
    var timer=controller?setTimeout(function(){{controller.abort();}},TIMEOUT):null;
    var opts={{cache:'no-store'}};
    if(controller)opts.signal=controller.signal;
    fetch(API,opts)
      .then(function(r){{if(timer)clearTimeout(timer);return r.json();}})
      .then(function(data){{
        window.JAMIITEK=data;
        document.dispatchEvent(new CustomEvent('jamiitek:ready',{{detail:data}}));
        if(!data.is_active){{showBlock(data.status,data.suspension_message);}}
        else{{reveal();}}
      }})
      .catch(function(){{
        if(timer)clearTimeout(timer);
        if(attempt<RETRY){{setTimeout(function(){{check(attempt+1);}},1500*attempt);}}
        else{{console.warn('[JamiiTek] Could not reach status API. Showing page.');reveal();}}
      }});
  }}
  if(document.readyState==='loading'){{document.addEventListener('DOMContentLoaded',function(){{check(1);}});}}
  else{{check(1);}}
}})();""".strip()

    resp = HttpResponse(js_code, content_type='application/javascript; charset=utf-8')
    resp['Access-Control-Allow-Origin'] = '*'
    resp['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp['Pragma'] = 'no-cache'
    return resp


# ── AUTH ───────────────────────────────────────────────────────────

def management_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('management_dashboard')
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect(request.POST.get('next') or '/manage/')
        error = 'Invalid credentials or insufficient permissions.'
    return render(request, 'management/login.html', {
        'error': error, 'next': request.GET.get('next', ''),
    })


def management_logout(request):
    logout(request)
    return redirect('management_login')


# ── HELPER ─────────────────────────────────────────────────────────

def _send_notification(website, notification_type, subject, message, sent_by=None):
    n = ClientNotification.objects.create(
        website=website, client=website.client,
        notification_type=notification_type,
        subject=subject, message=message,
        sent_by=sent_by, email_sent=False)
    if website.client.email:
        try:
            send_mail(subject=subject, message=message,
                      from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
                      recipient_list=[website.client.email], fail_silently=False)
            n.email_sent = True
            n.save()
        except Exception as e:
            print(f'[JamiiTek] Email failed: {e}')
    return n


# ══════════════════════════════════════════════════════════════════════════════
# DOMAIN MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@staff_required
def domain_list(request):
    from datetime import timedelta
    today = date.today()
    domains = DomainRecord.objects.select_related('website', 'website__client').all()
    expiring = [d for d in domains if not d.is_expired and d.days_until_expiry <= 30]
    expired  = [d for d in domains if d.is_expired]
    return render(request, 'management/domain_list.html', {
        'title': 'Domain Management',
        'domains': domains,
        'expiring': expiring,
        'expired': expired,
    })


@staff_required
def domain_add(request):
    websites = ManagedWebsite.objects.select_related('client').all()
    if request.method == 'POST':
        website = get_object_or_404(ManagedWebsite, pk=request.POST['website'])
        d = DomainRecord.objects.create(
            website=website,
            domain_name=request.POST.get('domain_name', '').strip(),
            registrar=request.POST.get('registrar', 'other'),
            registrar_other=request.POST.get('registrar_other', '').strip(),
            registration_date=request.POST['registration_date'],
            expiry_date=request.POST['expiry_date'],
            renewal_cost=Decimal(request.POST.get('renewal_cost') or 0),
            auto_renew=bool(request.POST.get('auto_renew')),
            send_renewal_warnings=bool(request.POST.get('send_renewal_warnings')),
            warning_days_before=int(request.POST.get('warning_days_before') or 30),
            dns_nameservers=request.POST.get('dns_nameservers', '').strip(),
            notes=request.POST.get('notes', '').strip(),
        )
        messages.success(request, f'Domain {d.domain_name} added successfully.')
        return redirect('domain_detail', pk=d.pk)
    return render(request, 'management/domain_add.html', {
        'title': 'Add Domain',
        'websites': websites,
        'registrar_choices': DomainRecord.REGISTRAR_CHOICES,
    })


@staff_required
def domain_detail(request, pk):
    domain   = get_object_or_404(DomainRecord, pk=pk)
    payments = domain.renewal_payments.all()
    return render(request, 'management/domain_detail.html', {
        'title': domain.domain_name,
        'domain': domain,
        'payments': payments,
        'status_choices': DomainRecord.STATUS_CHOICES,
    })


@staff_required
@require_POST
def domain_renew(request, pk):
    domain = get_object_or_404(DomainRecord, pk=pk)
    renewed_until = request.POST['renewed_until']
    DomainRenewalPayment.objects.create(
        domain=domain,
        amount=Decimal(request.POST.get('amount') or domain.renewal_cost),
        paid_date=request.POST.get('paid_date') or date.today(),
        renewed_until=renewed_until,
        payment_method=request.POST.get('payment_method', ''),
        transaction_ref=request.POST.get('transaction_ref', ''),
        notes=request.POST.get('notes', ''),
        recorded_by=request.user,
    )
    domain.expiry_date = renewed_until
    domain.status = 'active'
    domain.save()
    if request.POST.get('notify_client'):
        _send_domain_notification(domain, renewed_until)
    messages.success(request, f'Domain {domain.domain_name} renewed until {renewed_until}.')
    return redirect('domain_detail', pk=domain.pk)


@staff_required
@require_POST
def domain_update_status(request, pk):
    domain = get_object_or_404(DomainRecord, pk=pk)
    domain.status = request.POST.get('status', domain.status)
    domain.notes  = request.POST.get('notes', domain.notes)
    domain.save()
    messages.success(request, 'Domain status updated.')
    return redirect('domain_detail', pk=domain.pk)


def _send_domain_notification(domain, renewed_until):
    client = domain.website.client
    if not client.email:
        return
    try:
        send_mail(
            subject=f'Domain Renewal Confirmed — {domain.domain_name}',
            message=(
                f'Dear {client.name},\n\n'
                f'Your domain {domain.domain_name} has been renewed.\n\n'
                f'Valid Until: {renewed_until}\n'
                f'Registrar: {domain.get_registrar_display()}\n\n'
                f'JamiiTek Team\ninfo@jamiitek.com'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
            recipient_list=[client.email],
            fail_silently=True,
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# EMAIL HOSTING MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

@staff_required
def email_hosting_list(request):
    today = date.today()
    plans    = EmailHostingPlan.objects.select_related('client', 'website').all()
    expiring = [p for p in plans if not p.is_overdue and p.days_until_expiry <= 14]
    expired  = [p for p in plans if p.is_overdue]
    return render(request, 'management/email_hosting_list.html', {
        'title': 'Email Hosting',
        'plans': plans,
        'expiring': expiring,
        'expired': expired,
        'stats': {
            'total':     plans.count(),
            'active':    plans.filter(status='active').count(),
            'suspended': plans.filter(status='suspended').count(),
            'exp_count': len(expired),
        },
    })


@staff_required
def email_hosting_add(request):
    clients  = Client.objects.all()
    websites = ManagedWebsite.objects.select_related('client').all()
    if request.method == 'POST':
        client  = get_object_or_404(Client, pk=request.POST['client'])
        website = None
        if request.POST.get('website'):
            website = ManagedWebsite.objects.filter(pk=request.POST['website']).first()
        plan = EmailHostingPlan.objects.create(
            client=client,
            website=website,
            plan_name=request.POST.get('plan_name', '').strip(),
            email_domain=request.POST.get('email_domain', '').strip(),
            accounts_count=int(request.POST.get('accounts_count') or 1),
            storage_gb=Decimal(request.POST.get('storage_gb') or 5),
            monthly_cost=Decimal(request.POST.get('monthly_cost') or 0),
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            auto_suspend_on_expiry=bool(request.POST.get('auto_suspend_on_expiry')),
            send_expiry_warnings=bool(request.POST.get('send_expiry_warnings')),
            warning_days_before=int(request.POST.get('warning_days_before') or 7),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, f'Email plan "{plan.plan_name}" created.')
        return redirect('email_hosting_detail', pk=plan.pk)
    return render(request, 'management/email_hosting_add.html', {
        'title': 'Add Email Hosting Plan',
        'clients': clients,
        'websites': websites,
    })


@staff_required
def email_hosting_detail(request, pk):
    plan     = get_object_or_404(EmailHostingPlan, pk=pk)
    payments = plan.email_payments.all()
    return render(request, 'management/email_hosting_detail.html', {
        'title': plan.plan_name,
        'plan': plan,
        'payments': payments,
        'notification_types': ClientNotification.NOTIFICATION_TYPES,
    })


@staff_required
@require_POST
def email_hosting_payment(request, pk):
    plan   = get_object_or_404(EmailHostingPlan, pk=pk)
    amount = Decimal(request.POST.get('amount') or plan.monthly_cost)
    months = int(request.POST.get('months_covered') or 1)
    EmailHostingPayment.objects.create(
        plan=plan,
        amount=amount,
        payment_date=request.POST.get('payment_date') or date.today(),
        months_covered=months,
        payment_method=request.POST.get('payment_method', ''),
        transaction_ref=request.POST.get('transaction_ref', ''),
        notes=request.POST.get('notes', ''),
        recorded_by=request.user,
    )
    if request.POST.get('extend_plan'):
        from dateutil.relativedelta import relativedelta
        plan.end_date = plan.end_date + relativedelta(months=months)
        if plan.status in ('suspended', 'expired'):
            plan.status = 'active'
        plan.save()
    if request.POST.get('notify_client') and plan.client.email:
        try:
            send_mail(
                subject=f'Email Hosting Payment Received — {plan.email_domain}',
                message=(
                    f'Dear {plan.client.name},\n\n'
                    f'We have received your email hosting payment.\n\n'
                    f'Plan: {plan.plan_name}\n'
                    f'Domain: {plan.email_domain}\n'
                    f'Amount: TZS {amount}\n'
                    f'Valid Until: {plan.end_date}\n\n'
                    f'JamiiTek Team'
                ),
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
                recipient_list=[plan.client.email],
                fail_silently=True,
            )
        except Exception:
            pass
    messages.success(request, f'Payment recorded. Plan valid until {plan.end_date}.')
    return redirect('email_hosting_detail', pk=plan.pk)


@staff_required
@require_POST
def email_hosting_suspend(request, pk):
    plan = get_object_or_404(EmailHostingPlan, pk=pk)
    plan.status = 'suspended'
    plan.suspension_message = request.POST.get('suspension_message', plan.suspension_message)
    plan.save()
    if request.POST.get('notify_client') and plan.client.email:
        send_mail(
            subject=f'Email Hosting Suspended — {plan.email_domain}',
            message=f'Dear {plan.client.name},\n\nYour email hosting for {plan.email_domain} has been suspended.\n\n{plan.suspension_message}\n\nJamiiTek Team',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
            recipient_list=[plan.client.email], fail_silently=True)
    messages.success(request, 'Email plan suspended.')
    return redirect('email_hosting_detail', pk=plan.pk)


@staff_required
@require_POST
def email_hosting_restore(request, pk):
    plan = get_object_or_404(EmailHostingPlan, pk=pk)
    plan.status = 'active'
    plan.save()
    if request.POST.get('notify_client') and plan.client.email:
        send_mail(
            subject=f'Email Hosting Restored — {plan.email_domain}',
            message=f'Dear {plan.client.name},\n\nYour email hosting for {plan.email_domain} has been restored.\n\nJamiiTek Team',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
            recipient_list=[plan.client.email], fail_silently=True)
    messages.success(request, 'Email plan restored.')
    return redirect('email_hosting_detail', pk=plan.pk)
