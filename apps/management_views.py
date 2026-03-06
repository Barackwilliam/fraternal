# apps/management_views.py
# Panel ya Kusimamia Websites za Wateja

import json
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def staff_required(view_func):
    """Custom decorator — inahitaji login kwenye /manage/login/ badala ya /admin/login/"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/manage/login/?next={request.path}')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'Huna ruhusa ya kufikia ukurasa huu.')
            return redirect('/manage/login/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# Alias ili isibadilishe mstari mwingi kwenye code
staff_member_required = staff_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .models import (
    ManagedWebsite, HostingPayment, WebsiteFeature,
    ScheduledAction, ClientNotification, Client
)


# ─── DASHBOARD ───────────────────────────────────────────────

@staff_member_required
def management_dashboard(request):
    websites = ManagedWebsite.objects.select_related('client').all()

    # Stats
    total = websites.count()
    active = websites.filter(status='active').count()
    suspended = websites.filter(status='suspended').count()
    maintenance = websites.filter(status='maintenance').count()

    # Expiring soon (next 14 days)
    today = date.today()
    expiring_soon = websites.filter(
        hosting_end_date__range=[today, today + timedelta(days=14)],
        status='active'
    )

    # Overdue (already expired)
    overdue = websites.filter(hosting_end_date__lt=today, status='active')

    # Pending scheduled actions
    pending_actions = ScheduledAction.objects.filter(
        status='pending'
    ).select_related('website').order_by('scheduled_at')[:10]

    # Recent notifications
    recent_notifications = ClientNotification.objects.select_related('client').order_by('-sent_at')[:10]

    context = {
        'websites': websites,
        'stats': {
            'total': total,
            'active': active,
            'suspended': suspended,
            'maintenance': maintenance,
        },
        'expiring_soon': expiring_soon,
        'overdue': overdue,
        'pending_actions': pending_actions,
        'recent_notifications': recent_notifications,
        'title': 'Dashibodi ya Usimamizi',
    }
    return render(request, 'management/dashboard.html', context)


# ─── WEBSITE LIST & DETAIL ──────────────────────────────────

@staff_member_required
def website_list(request):
    websites = ManagedWebsite.objects.select_related('client').all()

    # Filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        websites = websites.filter(status=status_filter)

    context = {
        'websites': websites,
        'status_filter': status_filter,
        'title': 'Websites Zote',
    }
    return render(request, 'management/website_list.html', context)


@staff_member_required
def website_detail(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)
    payments = website.payments.order_by('-payment_date')
    features = website.features.all()
    scheduled = website.scheduled_actions.filter(status='pending').order_by('scheduled_at')
    notifications = website.notifications.order_by('-sent_at')[:20]

    context = {
        'website': website,
        'payments': payments,
        'features': features,
        'scheduled': scheduled,
        'notifications': notifications,
        'title': f'Dhibiti: {website.name}',
    }
    return render(request, 'management/website_detail.html', context)


@staff_member_required
def website_add(request):
    clients = Client.objects.all()

    if request.method == 'POST':
        client_id = request.POST.get('client')
        client = get_object_or_404(Client, pk=client_id)

        website = ManagedWebsite.objects.create(
            client=client,
            name=request.POST.get('name'),
            url=request.POST.get('url'),
            site_type=request.POST.get('site_type', 'django'),
            hosting_start_date=request.POST.get('hosting_start_date'),
            hosting_end_date=request.POST.get('hosting_end_date'),
            monthly_cost=request.POST.get('monthly_cost', 0),
            notes=request.POST.get('notes', ''),
            auto_suspend_on_expiry=request.POST.get('auto_suspend_on_expiry') == 'on',
            send_expiry_warnings=request.POST.get('send_expiry_warnings') == 'on',
        )

        # Add default features based on site type
        default_features = []
        if website.site_type == 'django':
            default_features = [
                ('access', 'Upatikanaji wa Website'),
                ('api', 'API Endpoints'),
                ('admin', 'Admin Panel'),
                ('uploads', 'Kupakia Faili'),
                ('email', 'Huduma ya Barua Pepe'),
            ]
        else:
            default_features = [
                ('access', 'Upatikanaji wa Website'),
                ('contact_form', 'Fomu ya Mawasiliano'),
            ]

        for key, name in default_features:
            WebsiteFeature.objects.create(
                website=website,
                feature_key=key,
                feature_name=name,
                is_enabled=True
            )

        messages.success(request, f'Website "{website.name}" imeongezwa kikamilifu!')
        return redirect('website_detail', pk=website.pk)

    context = {'clients': clients, 'title': 'Ongeza Website Mpya'}
    return render(request, 'management/website_add.html', context)


# ─── STATUS ACTIONS ─────────────────────────────────────────

@staff_member_required
def suspend_website(request, pk):
    if request.method == 'POST':
        website = get_object_or_404(ManagedWebsite, pk=pk)
        reason = request.POST.get('reason', 'Malipo ya hosting hayajalipwa')
        message = request.POST.get('suspension_message', website.suspension_message)
        notify = request.POST.get('notify_client') == 'on'

        website.status = 'suspended'
        website.suspension_reason = reason
        website.suspension_message = message
        website.save()

        if notify:
            _send_notification(
                website=website,
                notification_type='suspended',
                subject=f'Huduma ya Website Yako Imesimamishwa - {website.name}',
                message=f"""Habari {website.client.name},

Tunakutaarifu kuwa huduma ya website yako ({website.name}) imesimamishwa kwa sababu ifuatayo:

{reason}

Ili kurudisha huduma, tafadhali wasiliana nasi au lipa ankara yako iliyobaki.

Kwa msaada, wasiliana nasi.

Asante,
JamiiTek Team""",
                sent_by=request.user
            )

        messages.success(request, f'Website "{website.name}" imesimamishwa.')
    return redirect('website_detail', pk=pk)


@staff_member_required
def restore_website(request, pk):
    if request.method == 'POST':
        website = get_object_or_404(ManagedWebsite, pk=pk)
        notify = request.POST.get('notify_client') == 'on'

        website.status = 'active'
        website.suspension_reason = ''
        website.save()

        if notify:
            _send_notification(
                website=website,
                notification_type='restored',
                subject=f'Huduma ya Website Yako Imerudishwa - {website.name}',
                message=f"""Habari {website.client.name},

Tunafurahi kukutaarifu kuwa huduma ya website yako ({website.name}) imerudishwa na sasa inafanya kazi vizuri.

URL: {website.url}

Asante kwa kuendelea kutumia huduma zetu.

JamiiTek Team""",
                sent_by=request.user
            )

        messages.success(request, f'Website "{website.name}" imerudishwa kikamilifu!')
    return redirect('website_detail', pk=pk)


@staff_member_required
def set_maintenance(request, pk):
    if request.method == 'POST':
        website = get_object_or_404(ManagedWebsite, pk=pk)
        message = request.POST.get('maintenance_message', 'Website iko katika matengenezo. Tutarudi hivi karibuni.')
        website.status = 'maintenance'
        website.suspension_message = message
        website.save()
        messages.success(request, f'"{website.name}" imewekwa katika hali ya matengenezo.')
    return redirect('website_detail', pk=pk)


# ─── FEATURES MANAGEMENT ────────────────────────────────────

@staff_member_required
def toggle_feature(request, pk, feature_pk):
    if request.method == 'POST':
        feature = get_object_or_404(WebsiteFeature, pk=feature_pk, website_id=pk)
        feature.is_enabled = not feature.is_enabled
        if not feature.is_enabled:
            feature.disabled_reason = request.POST.get('reason', '')
        else:
            feature.disabled_reason = ''
        feature.save()

        status = "imewashwa" if feature.is_enabled else "imezimwa"
        messages.success(request, f'Huduma "{feature.feature_name}" {status}.')
    return redirect('website_detail', pk=pk)


@staff_member_required
def add_feature(request, pk):
    if request.method == 'POST':
        website = get_object_or_404(ManagedWebsite, pk=pk)
        WebsiteFeature.objects.get_or_create(
            website=website,
            feature_key=request.POST.get('feature_key'),
            defaults={
                'feature_name': request.POST.get('feature_name'),
                'is_enabled': True,
            }
        )
        messages.success(request, 'Huduma mpya imeongezwa.')
    return redirect('website_detail', pk=pk)


# ─── PAYMENTS ───────────────────────────────────────────────

@staff_member_required
def add_payment(request, pk):
    if request.method == 'POST':
        website = get_object_or_404(ManagedWebsite, pk=pk)
        months = int(request.POST.get('months_covered', 1))

        payment = HostingPayment.objects.create(
            website=website,
            amount=request.POST.get('amount'),
            payment_date=request.POST.get('payment_date'),
            months_covered=months,
            payment_method=request.POST.get('payment_method', ''),
            transaction_ref=request.POST.get('transaction_ref', ''),
            notes=request.POST.get('notes', ''),
            recorded_by=request.user
        )

        # Extend hosting end date
        if request.POST.get('extend_hosting') == 'on':
            from dateutil.relativedelta import relativedelta
            website.hosting_end_date = website.hosting_end_date + relativedelta(months=months)
            website.save()

        # Auto restore if was suspended for non-payment
        if website.status == 'suspended' and request.POST.get('auto_restore') == 'on':
            website.status = 'active'
            website.suspension_reason = ''
            website.save()
            messages.info(request, f'Website imerudishwa kiotomatiki baada ya malipo.')

        messages.success(request, f'Malipo ya TZS {payment.amount} yameandikwa kikamilifu.')
    return redirect('website_detail', pk=pk)


# ─── SEND NOTIFICATION ──────────────────────────────────────

@staff_member_required
def send_notification(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_body = request.POST.get('message')
        notification_type = request.POST.get('notification_type', 'custom')

        _send_notification(
            website=website,
            notification_type=notification_type,
            subject=subject,
            message=message_body,
            sent_by=request.user
        )
        messages.success(request, f'Ujumbe umetumwa kwa {website.client.name}.')
        return redirect('website_detail', pk=pk)

    context = {
        'website': website,
        'notification_types': ClientNotification.NOTIFICATION_TYPES,
        'title': f'Tuma Ujumbe - {website.name}',
    }
    return render(request, 'management/send_notification.html', context)


# ─── SCHEDULED ACTIONS ──────────────────────────────────────

@staff_member_required
def schedule_action(request, pk):
    website = get_object_or_404(ManagedWebsite, pk=pk)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        scheduled_at_str = request.POST.get('scheduled_at')
        
        from datetime import datetime
        scheduled_at = datetime.fromisoformat(scheduled_at_str)
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at)

        action_data = {
            'reason': request.POST.get('reason', ''),
            'message': request.POST.get('message', ''),
            'notify_client': request.POST.get('notify_client') == 'on',
            'feature_key': request.POST.get('feature_key', ''),
            'email_subject': request.POST.get('email_subject', ''),
            'email_body': request.POST.get('email_body', ''),
        }

        ScheduledAction.objects.create(
            website=website,
            action_type=action_type,
            scheduled_at=scheduled_at,
            action_data=action_data,
            created_by=request.user
        )

        messages.success(request, f'Kitendo kimepangwa: {action_type} @ {scheduled_at.strftime("%d/%m/%Y %H:%M")}')
        return redirect('website_detail', pk=pk)

    context = {
        'website': website,
        'action_types': ScheduledAction.ACTION_TYPES,
        'features': website.features.all(),
        'title': f'Panga Kitendo - {website.name}',
    }
    return render(request, 'management/schedule_action.html', context)


@staff_member_required
def cancel_scheduled_action(request, action_pk):
    action = get_object_or_404(ScheduledAction, pk=action_pk)
    pk = action.website.pk
    action.status = 'cancelled'
    action.save()
    messages.success(request, 'Kitendo kimesimamishwa.')
    return redirect('website_detail', pk=pk)


# ─── API ENDPOINT (Client websites ping this) ───────────────

@require_GET
@csrf_exempt
def site_status_api(request, api_key):
    """
    API endpoint ambayo client websites zinapiga ping.
    Inarudisha JSON na hali ya website na features.
    """
    try:
        website = ManagedWebsite.objects.get(api_key=api_key)
        features = {
            f.feature_key: f.is_enabled
            for f in website.features.all()
        }
        
        data = {
            'status': website.status,
            'is_active': website.is_active,
            'suspension_message': website.suspension_message if not website.is_active else '',
            'features': features,
            'site_name': website.name,
        }
        return JsonResponse(data)

    except ManagedWebsite.DoesNotExist:
        return JsonResponse({'status': 'active', 'is_active': True, 'features': {}}, status=200)


@require_GET
def get_js_snippet(request, api_key):
    """Returns JS snippet for static websites"""
    try:
        website = ManagedWebsite.objects.get(api_key=api_key)
    except ManagedWebsite.DoesNotExist:
        return HttpResponse("// Invalid API key", content_type='application/javascript')

    api_url = request.build_absolute_uri(f'/api/site-status/{api_key}/')
    
    js_code = f"""
/* JamiiTek Website Status Checker - {website.name} */
(function() {{
    var JAMIITEK_API = '{api_url}';
    
    function checkStatus() {{
        fetch(JAMIITEK_API)
            .then(function(r) {{ return r.json(); }})
            .then(function(data) {{
                if (!data.is_active) {{
                    showSuspensionPage(data.suspension_message || 'Huduma imesimamishwa kwa muda.');
                }}
                // Store features globally for app use
                window.JAMIITEK_FEATURES = data.features || {{}};
                
                // Trigger custom event
                document.dispatchEvent(new CustomEvent('jamiitek:status', {{ detail: data }}));
            }})
            .catch(function(err) {{
                console.warn('JamiiTek: Status check failed', err);
            }});
    }}
    
    function showSuspensionPage(msg) {{
        document.body.innerHTML = `
        <div style="
            display:flex; flex-direction:column; align-items:center; justify-content:center;
            min-height:100vh; background:#f8f9fa; font-family:Arial,sans-serif; text-align:center; padding:20px;">
            <div style="background:white; padding:50px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.1); max-width:500px;">
                <div style="font-size:64px; margin-bottom:20px;">🔒</div>
                <h1 style="color:#dc3545; margin-bottom:15px;">Huduma Imesimamishwa</h1>
                <p style="color:#6c757d; font-size:16px; line-height:1.6;">${{msg}}</p>
                <p style="color:#adb5bd; font-size:13px; margin-top:30px;">Powered by JamiiTek</p>
            </div>
        </div>`;
    }}
    
    // Check on page load
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', checkStatus);
    }} else {{
        checkStatus();
    }}
}})();
""".strip()

    return HttpResponse(js_code, content_type='application/javascript')


# ─── HELPER ─────────────────────────────────────────────────

def _send_notification(website, notification_type, subject, message, sent_by=None):
    """Internal helper to save and optionally email notification"""
    notification = ClientNotification.objects.create(
        website=website,
        client=website.client,
        notification_type=notification_type,
        subject=subject,
        message=message,
        sent_by=sent_by,
        email_sent=False
    )

    # Send email if client has email
    if website.client.email:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
                recipient_list=[website.client.email],
                fail_silently=False,
            )
            notification.email_sent = True
            notification.save(update_fields=['email_sent'])
        except Exception as e:
            pass  # Log silently — notification saved even if email fails

    return notification


# ─── MANAGEMENT LOGIN / LOGOUT ──────────────────────────────

def management_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('management_dashboard')

    next_url = request.GET.get('next', '/manage/')
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '/manage/')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect(next_url)
            else:
                error = 'Account yako haina ruhusa ya kufikia panel hii.'
        else:
            error = 'Username au password si sahihi. Jaribu tena.'

    return render(request, 'management/login.html', {
        'error': error,
        'next': next_url,
        'title': 'Ingia - JamiiTek Panel'
    })


def management_logout(request):
    logout(request)
    return redirect('/manage/login/')
