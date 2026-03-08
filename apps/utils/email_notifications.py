# apps/utils/email_notifications.py
"""
JamiiTek Email Notification System
=====================================
Central module for all automated emails sent to clients.

USAGE:
    from apps.utils.email_notifications import (
        send_hosting_expiry_warning,
        send_website_suspended,
        send_website_restored,
        send_payment_received,
        send_domain_expiry_warning,
        send_welcome_email,
        send_bulk_expiry_warnings,
    )
"""

import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
FROM_EMAIL   = getattr(settings, 'DEFAULT_FROM_EMAIL', 'JamiiTek <noreply@jamiitek.co.tz>')
PORTAL_URL   = getattr(settings, 'PORTAL_BASE_URL', 'https://jamiitek.co.tz/portal/')


def _send(subject: str, template: str, context: dict, to_email: str) -> bool:
    """
    Core send helper. Renders HTML template, generates plain-text fallback,
    sends via Django's email backend. Returns True on success, False on failure.
    """
    if not to_email:
        logger.warning(f"[Email] No recipient for: {subject}")
        return False

    context.setdefault('subject', subject)
    context.setdefault('portal_url', PORTAL_URL)

    try:
        html_body  = render_to_string(f'emails/{template}', context)
        plain_body = strip_tags(html_body)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_body,
            from_email=FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)

        logger.info(f"[Email ✅] '{subject}' → {to_email}")
        return True

    except Exception as e:
        logger.error(f"[Email ❌] '{subject}' → {to_email} | Error: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 1. HOSTING EXPIRY WARNING
# ══════════════════════════════════════════════════════════════════════════════

def send_hosting_expiry_warning(website) -> bool:
    """
    Send hosting expiry warning to client.
    Call when days_until_expiry matches warning_days_before threshold.
    """
    client = website.client
    return _send(
        subject=f"⚠ Hosting Expiry Notice — {website.name} expires in {website.days_until_expiry} days",
        template='hosting_expiry_warning.html',
        context={
            'client_name':  client.name,
            'website_name': website.name,
            'website_url':  website.url,
            'expiry_date':  website.hosting_end_date.strftime('%d %B %Y'),
            'days_left':    website.days_until_expiry,
            'monthly_cost': website.monthly_cost,
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 2. WEBSITE SUSPENDED
# ══════════════════════════════════════════════════════════════════════════════

def send_website_suspended(website, reason: str = 'Hosting payment overdue') -> bool:
    """Send suspension notice immediately when website is suspended."""
    client = website.client
    return _send(
        subject=f"🔒 Your website '{website.name}' has been suspended",
        template='website_suspended.html',
        context={
            'client_name':          client.name,
            'website_name':         website.name,
            'website_url':          website.url,
            'reason':               reason,
            'suspended_date':       timezone.now().strftime('%d %B %Y'),
            'suspension_message':   website.suspension_message,
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 3. WEBSITE RESTORED
# ══════════════════════════════════════════════════════════════════════════════

def send_website_restored(website) -> bool:
    """Send restoration confirmation when website is brought back online."""
    client = website.client
    return _send(
        subject=f"✅ Your website '{website.name}' is back online!",
        template='website_restored.html',
        context={
            'client_name':      client.name,
            'website_name':     website.name,
            'website_url':      website.url,
            'restored_date':    timezone.now().strftime('%d %B %Y'),
            'new_expiry_date':  website.hosting_end_date.strftime('%d %B %Y'),
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4. PAYMENT RECEIVED
# ══════════════════════════════════════════════════════════════════════════════

def send_payment_received(payment) -> bool:
    """
    Send payment receipt after recording a new HostingPayment.
    Pass the HostingPayment instance.
    """
    website = payment.website
    client  = website.client
    return _send(
        subject=f"💰 Payment Received — TZS {payment.amount:,.0f} for {website.name}",
        template='payment_received.html',
        context={
            'client_name':      client.name,
            'website_name':     website.name,
            'amount':           payment.amount,
            'payment_date':     payment.payment_date.strftime('%d %B %Y'),
            'months_covered':   payment.months_covered,
            'payment_method':   payment.payment_method or 'N/A',
            'transaction_ref':  payment.transaction_ref,
            'new_expiry_date':  website.hosting_end_date.strftime('%d %B %Y'),
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 5. DOMAIN EXPIRY WARNING
# ══════════════════════════════════════════════════════════════════════════════

def send_domain_expiry_warning(domain) -> bool:
    """Send domain expiry warning. Pass DomainRecord instance."""
    client = domain.website.client
    return _send(
        subject=f"⚠ Domain Expiry Notice — {domain.domain_name} expires in {domain.days_until_expiry} days",
        template='domain_expiry_warning.html',
        context={
            'client_name':    client.name,
            'domain_name':    domain.domain_name,
            'registrar':      domain.get_registrar_display(),
            'expiry_date':    domain.expiry_date.strftime('%d %B %Y'),
            'days_left':      domain.days_until_expiry,
            'renewal_cost':   domain.renewal_cost,
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 6. WELCOME EMAIL
# ══════════════════════════════════════════════════════════════════════════════

def send_welcome_email(client) -> bool:
    """Send welcome email when a client portal account is created."""
    return _send(
        subject="Welcome to JamiiTek Client Portal 🚀",
        template='welcome.html',
        context={
            'client_name':  client.name,
            'client_email': client.email,
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 7. BULK — Run all expiry checks (call from management command or cron)
# ══════════════════════════════════════════════════════════════════════════════

def send_bulk_expiry_warnings():
    """
    Check ALL active websites and domains and send warnings where needed.
    Call this daily via a management command or Heroku scheduler.

    Returns dict with counts: { sent, skipped, errors }
    """
    from apps.models import ManagedWebsite, DomainRecord

    sent = skipped = errors = 0
    today = timezone.now().date()

    # ── Hosting warnings ──────────────────────────────────────────────────────
    active_sites = ManagedWebsite.objects.filter(
        status='active',
        send_expiry_warnings=True
    ).select_related('client')

    for site in active_sites:
        days = site.days_until_expiry
        if days == site.warning_days_before or days in [3, 1]:
            ok = send_hosting_expiry_warning(site)
            sent += 1 if ok else 0
            errors += 0 if ok else 1
        else:
            skipped += 1

    # ── Auto-suspend overdue sites ────────────────────────────────────────────
    overdue = ManagedWebsite.objects.filter(
        status='active',
        auto_suspend_on_expiry=True,
        hosting_end_date__lt=today,
    ).select_related('client')

    for site in overdue:
        site.status = 'suspended'
        site.suspension_message = 'Your hosting has expired. Please make a payment to restore your website.'
        site.save(update_fields=['status', 'suspension_message'])
        ok = send_website_suspended(site, reason='Hosting expired')
        sent += 1 if ok else 0
        errors += 0 if ok else 1
        logger.info(f"[AutoSuspend] {site.name} — expired {site.hosting_end_date}")

    # ── Domain warnings ───────────────────────────────────────────────────────
    domains = DomainRecord.objects.filter(
        status='active',
        send_renewal_warnings=True
    ).select_related('website__client')

    for domain in domains:
        days = domain.days_until_expiry
        if days == domain.warning_days_before or days in [7, 3, 1]:
            ok = send_domain_expiry_warning(domain)
            sent += 1 if ok else 0
            errors += 0 if ok else 1
        else:
            skipped += 1

    logger.info(f"[BulkEmail] Done — sent:{sent} skipped:{skipped} errors:{errors}")
    return {'sent': sent, 'skipped': skipped, 'errors': errors}
