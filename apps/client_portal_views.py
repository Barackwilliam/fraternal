# apps/client_portal_views.py
# JamiiTek Client Portal — Website owners can log in and manage their account

import secrets
from decimal import Decimal
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings

from apps.utils.email_notifications import send_welcome_email
from django.core.mail import send_mail

from .models import (
    Client, ManagedWebsite, HostingPayment, ClientNotification, WebsiteFeature,
    DomainRecord, EmailHostingPlan, EmailHostingPayment,
    HostingConfiguration, DomainDNSRecord,
)


# ── HELPER ─────────────────────────────────────────────────────────

def client_required(view_func):
    """Require login as a client (non-staff user with Client profile)."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/portal/login/?next={request.path}')
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/manage/')
        try:
            request.client_profile = Client.objects.get(user=request.user)
        except Client.DoesNotExist:
            messages.error(request, 'Your account is not linked to a client profile. Please contact JamiiTek.')
            return redirect('/portal/login/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ── REGISTER ───────────────────────────────────────────────────────

def portal_register(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('portal_dashboard')

    if request.method == 'POST':
        username    = request.POST.get('username', '').strip()
        email       = request.POST.get('email', '').strip()
        phone       = request.POST.get('phone', '').strip()
        full_name   = request.POST.get('full_name', '').strip()
        website_name = request.POST.get('website_name', '').strip()
        website_url  = request.POST.get('website_url', '').strip()
        password    = request.POST.get('password', '')
        password2   = request.POST.get('password2', '')

        errors = []
        if not all([username, email, full_name, password]):
            errors.append('All fields except phone are required.')
        if password != password2:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if User.objects.filter(username=username).exists():
            errors.append('That username is already taken.')
        if User.objects.filter(email=email).exists():
            errors.append('That email is already registered.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            user = User.objects.create_user(
                username=username, email=email, password=password,
                first_name=full_name.split()[0],
                last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else '',
            )
            client = Client.objects.create(
                user=user, name=full_name,
                email=email, phone=phone,
                company=website_name,
            )
            # Send branded welcome email
            send_welcome_email(client)
            # Store website URL as a pending managed website note
            if website_url:
                from .models import ClientNotification
                ClientNotification.objects.create(
                    website=None, client=client,
                    notification_type='general',
                    subject=f'New Registration — Website URL: {website_url}',
                    # ✅ Use \n instead
message=f'Client {full_name} registered and provided website URL: {website_url}\nPhone: {phone}\nPlease add their website in the management panel.',
                    email_sent=False,
                )
            # Notify JamiiTek staff
            try:
                send_mail(
                    subject=f'New Portal Registration — {full_name}',
                    message=f'New client registered on JamiiTek portal.\n\nName: {full_name}\nEmail: {email}\nPhone: {phone}\nWebsite interest: {website_name}\nUsername: {username}\n\nLog in to the management panel to review.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
                    recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'info@jamiitek.com')],
                    fail_silently=True,
                )
            except Exception:
                pass

            login(request, user)
            messages.success(request, f'Welcome, {full_name}! Your account has been created.')
            return redirect('portal_dashboard')

    return render(request, 'portal/register.html', {'title': 'Create Account'})


# ── LOGIN ──────────────────────────────────────────────────────────

def portal_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('portal_dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_staff or user.is_superuser:
                error = 'Staff accounts use the management panel.'
            elif Client.objects.filter(user=user).exists():
                login(request, user)
                return redirect(request.POST.get('next') or '/portal/')
            else:
                error = 'Your account is not linked to a client profile. Please contact JamiiTek.'
        else:
            error = 'Invalid username or password.'

    return render(request, 'portal/login.html', {
        'error': error, 'next': request.GET.get('next', ''),
    })


def portal_logout(request):
    logout(request)
    return redirect('portal_login')


# ── DASHBOARD ──────────────────────────────────────────────────────

@client_required
def portal_dashboard(request):
    client   = request.client_profile
    websites = ManagedWebsite.objects.filter(client=client)
    domains  = DomainRecord.objects.filter(website__client=client)
    email_plans = EmailHostingPlan.objects.filter(client=client)
    today    = date.today()

    total_paid = HostingPayment.objects.filter(website__client=client).aggregate(
        total=Sum('amount'))['total'] or 0
    notifications = ClientNotification.objects.filter(
        client=client).order_by('-sent_at')[:5]

    alerts = []
    for w in websites:
        if w.is_overdue:
            alerts.append({'type': 'danger', 'msg': f'<strong>{w.name}</strong> — hosting expired! Please make a payment.'})
        elif w.days_until_expiry is not None and w.days_until_expiry <= 7:
            alerts.append({'type': 'warning', 'msg': f'<strong>{w.name}</strong> — hosting expires in {w.days_until_expiry} day(s).'})
        if w.status == 'suspended':
            alerts.append({'type': 'danger', 'msg': f'<strong>{w.name}</strong> is suspended. Contact JamiiTek.'})

    for d in domains:
        if d.is_expired:
            alerts.append({'type': 'danger', 'msg': f'Domain <strong>{d.domain_name}</strong> has expired!'})
        elif d.days_until_expiry <= 30:
            alerts.append({'type': 'warning', 'msg': f'Domain <strong>{d.domain_name}</strong> expires in {d.days_until_expiry} day(s).'})

    for ep in email_plans:
        if ep.is_overdue:
            alerts.append({'type': 'danger', 'msg': f'Email hosting <strong>{ep.email_domain}</strong> has expired!'})
        elif ep.days_until_expiry <= 7:
            alerts.append({'type': 'warning', 'msg': f'Email hosting <strong>{ep.email_domain}</strong> expires in {ep.days_until_expiry} day(s).'})

    return render(request, 'portal/dashboard.html', {
        'title': 'My Dashboard',
        'client': client,
        'websites': websites,
        'domains': domains,
        'email_plans': email_plans,
        'total_paid': total_paid,
        'notifications': notifications,
        'alerts': alerts,
        'today': today,
    })


# ── MY WEBSITES ────────────────────────────────────────────────────

@client_required
def portal_website_list(request):
    client = request.client_profile
    websites = ManagedWebsite.objects.filter(client=client).order_by('name')
    return render(request, 'portal/website_list.html', {
        'title': 'My Websites',
        'client': client,
        'websites': websites,
    })


@client_required
def portal_website_detail(request, pk):
    client = request.client_profile
    website = get_object_or_404(ManagedWebsite, pk=pk, client=client)
    payments = HostingPayment.objects.filter(website=website).order_by('-payment_date')
    notifications = ClientNotification.objects.filter(website=website).order_by('-sent_at')[:20]
    features = WebsiteFeature.objects.filter(website=website)

    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    months_paid = payments.aggregate(total=Sum('months_covered'))['total'] or 0

    return render(request, 'portal/website_detail.html', {
        'title': website.name,
        'client': client,
        'website': website,
        'payments': payments,
        'notifications': notifications,
        'features': features,
        'total_paid': total_paid,
        'months_paid': months_paid,
    })


# ── BILLING & PAYMENTS ─────────────────────────────────────────────

@client_required
def portal_billing(request):
    client = request.client_profile
    websites = ManagedWebsite.objects.filter(client=client)
    payments = HostingPayment.objects.filter(
        website__client=client).order_by('-payment_date').select_related('website')

    total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_due = sum([
        w.monthly_cost for w in websites
        if w.is_overdue or (w.days_until_expiry is not None and w.days_until_expiry <= 14)
    ])

    # NMB payment details from settings or hardcoded
    payment_info = {
        'bank': 'NMB Bank',
        'account_name': 'JamiiTek Technologies',
        'account_number': getattr(settings, 'NMB_ACCOUNT', '21410034200'),
        'branch': 'Dar es Salaam',
        'reference_format': 'WEBSITE NAME + PHONE',
    }

    return render(request, 'portal/billing.html', {
        'title': 'Billing & Payments',
        'client': client,
        'websites': websites,
        'payments': payments,
        'total_paid': total_paid,
        'total_due': total_due,
        'payment_info': payment_info,
    })


# ── SUBMIT PAYMENT PROOF ───────────────────────────────────────────

@client_required
@require_POST
def portal_submit_payment(request):
    client = request.client_profile
    website_pk = request.POST.get('website')
    amount = request.POST.get('amount', '').strip()
    transaction_ref = request.POST.get('transaction_ref', '').strip()
    payment_method = request.POST.get('payment_method', 'NMB Bank Transfer')
    months = request.POST.get('months_covered', '1')
    notes = request.POST.get('notes', '').strip()

    if not all([website_pk, amount, transaction_ref]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('portal_billing')

    try:
        website = ManagedWebsite.objects.get(pk=website_pk, client=client)
    except ManagedWebsite.DoesNotExist:
        messages.error(request, 'Website not found.')
        return redirect('portal_billing')

    # Create pending payment record (staff will confirm)
    # We note it as pending in the notes field
    from .models import ClientNotification
    ClientNotification.objects.create(
        website=website, client=client,
        notification_type='payment_received',
        subject=f'Payment Submission — {website.name}',
        message=f'Client {client.name} submitted payment proof.\n\nAmount: TZS {amount}\nMethod: {payment_method}\nRef: {transaction_ref}\nMonths: {months}\nNotes: {notes}\n\nPlease verify and record the payment in the management panel.',
        email_sent=False,
    )

    # Email JamiiTek staff
    try:
        send_mail(
            subject=f'Payment Proof Submitted — {website.name} — {client.name}',
            message=f'Client has submitted payment proof.\n\nWebsite: {website.name}\nClient: {client.name}\nAmount: TZS {amount}\nMethod: {payment_method}\nRef: {transaction_ref}\nMonths: {months}\n\nPlease verify and record it in the management panel.',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
            recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'info@jamiitek.com')],
            fail_silently=True,
        )
    except Exception:
        pass

    messages.success(request, 'Payment proof submitted! JamiiTek will verify and confirm within 24 hours.')
    return redirect('portal_billing')


# ── NOTIFICATIONS ──────────────────────────────────────────────────

@client_required
def portal_notifications(request):
    client = request.client_profile
    notifications = ClientNotification.objects.filter(
        client=client).order_by('-sent_at')
    return render(request, 'portal/notifications.html', {
        'title': 'Messages & Notifications',
        'client': client,
        'notifications': notifications,
    })


# ── PROFILE ────────────────────────────────────────────────────────

@client_required
def portal_profile(request):
    client = request.client_profile
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            client.name = request.POST.get('name', client.name).strip()
            client.phone = request.POST.get('phone', client.phone).strip()
            client.company = request.POST.get('company', client.company).strip()
            client.save()
            # Update email on user too
            new_email = request.POST.get('email', '').strip()
            if new_email and new_email != client.user.email:
                if User.objects.filter(email=new_email).exclude(pk=client.user.pk).exists():
                    messages.error(request, 'That email is already in use.')
                else:
                    client.user.email = new_email
                    client.email = new_email
                    client.user.save()
                    client.save()
            messages.success(request, 'Profile updated successfully.')

        elif action == 'change_password':
            current = request.POST.get('current_password', '')
            new_pw = request.POST.get('new_password', '')
            confirm = request.POST.get('confirm_password', '')
            if not client.user.check_password(current):
                messages.error(request, 'Current password is incorrect.')
            elif new_pw != confirm:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pw) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                client.user.set_password(new_pw)
                client.user.save()
                messages.success(request, 'Password changed. Please log in again.')
                return redirect('portal_login')

        return redirect('portal_profile')

    return render(request, 'portal/profile.html', {
        'title': 'My Profile',
        'client': client,
    })


# ── SUPPORT REQUEST ────────────────────────────────────────────────

@client_required
def portal_support(request):
    client = request.client_profile
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message_body = request.POST.get('message', '').strip()
        website_pk = request.POST.get('website', '')
        priority = request.POST.get('priority', 'normal')
        if not subject or not message_body:
            messages.error(request, 'Subject and message are required.')
        else:
            website = None
            if website_pk:
                try:
                    website = ManagedWebsite.objects.get(pk=website_pk, client=client)
                except ManagedWebsite.DoesNotExist:
                    pass

            ClientNotification.objects.create(
                website=website, client=client,
                notification_type='support',
                subject=f'[{priority.upper()}] Support: {subject}',
                message=f'From: {client.name} ({client.email})\nPriority: {priority}\n\n{message_body}',
                email_sent=False,
            )
            try:
                send_mail(
                    subject=f'[Support/{priority.upper()}] {subject} — {client.name}',
                    message=f'Client: {client.name}\nEmail: {client.email}\nPhone: {client.phone}\nWebsite: {website.name if website else "N/A"}\nPriority: {priority}\n\n{message_body}',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.com'),
                    recipient_list=[getattr(settings, 'ADMIN_EMAIL', 'info@jamiitek.com')],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Support request submitted! We will respond within 24 hours.')
            return redirect('portal_support')

    faqs = [
        {'q': 'How do I renew my hosting?', 'a': 'Transfer payment to NMB Bank Account 21410034200 (JamiiTek Technologies), then submit your proof in the Billing section. We verify within 24 hours.'},
        {'q': 'My website is suspended — why?', 'a': 'This usually means your hosting payment has expired. Go to Billing, renew your hosting, and submit payment proof.'},
        {'q': 'How long does payment verification take?', 'a': 'We verify payments within 24 hours on business days (Monday to Saturday). You will receive a confirmation message once verified.'},
        {'q': 'How do I update content on my website?', 'a': 'Contact JamiiTek support via this form or WhatsApp. Describe the changes you need and we will handle them for you.'},
        {'q': 'What is the NMB reference I should use?', 'a': 'Use your full name as the payment reference when transferring. This helps us identify your payment quickly.'},
    ]
    return render(request, 'portal/support.html', {
        'title': 'Support',
        'client': client,
        'websites': ManagedWebsite.objects.filter(client=client),
        'faqs': faqs,
    })


# ── PORTAL: MY DOMAINS ──────────────────────────────────────────────

@client_required
def portal_domains(request):
    client  = request.client_profile
    domains = DomainRecord.objects.filter(website__client=client).select_related('website')
    return render(request, 'portal/domains.html', {
        'title': 'My Domains',
        'client': client,
        'domains': domains,
    })


# ── PORTAL: EMAIL HOSTING ────────────────────────────────────────────

@client_required
def portal_email_hosting(request):
    client      = request.client_profile
    email_plans = EmailHostingPlan.objects.filter(client=client).select_related('website')
    payments    = EmailHostingPayment.objects.filter(
        plan__client=client).select_related('plan').order_by('-payment_date')
    total_paid  = sum(p.amount for p in payments)
    payment_info = {
        'bank':           'NMB Bank',
        'account_name':   'JamiiTek Technologies',
        'account_number': getattr(settings, 'NMB_ACCOUNT', '21410034200'),
    }
    return render(request, 'portal/email_hosting.html', {
        'title': 'Email Hosting',
        'client': client,
        'email_plans': email_plans,
        'payments': payments,
        'total_paid': total_paid,
        'payment_info': payment_info,
    })


# ══════════════════════════════════════════════════════════════
# HOSTING CONTROL PANEL
# ══════════════════════════════════════════════════════════════

@client_required
def portal_hosting_config(request, pk):
    client  = request.client_profile
    website = get_object_or_404(ManagedWebsite, pk=pk, client=client)
    try:
        cfg = website.hosting_config
    except HostingConfiguration.DoesNotExist:
        cfg = None
    return render(request, 'portal/hosting_config.html', {
        'title':   f'Hosting Panel — {website.name}',
        'client':  client,
        'website': website,
        'cfg':     cfg,
    })


# ══════════════════════════════════════════════════════════════
# DNS MANAGER
# ══════════════════════════════════════════════════════════════

@client_required
def portal_dns_manager(request, pk):
    client = request.client_profile
    domain = get_object_or_404(DomainRecord, pk=pk, website__client=client)
    records = domain.dns_records.all().order_by('record_type', 'name')
    return render(request, 'portal/dns_manager.html', {
        'title':   f'DNS Manager — {domain.domain_name}',
        'client':  client,
        'domain':  domain,
        'records': records,
    })
