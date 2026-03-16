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
FROM_EMAIL   = getattr(settings, 'DEFAULT_FROM_EMAIL', 'JamiiTek <noreply@jamiitek.com>')
PORTAL_URL   = getattr(settings, 'PORTAL_BASE_URL', 'https://jamiitek.com/portal/')


def _send(subject: str, template: str, context: dict, to_email: str) -> bool:
    """
    Core send helper. Renders HTML template, generates plain-text fallback,
    sends via Django's email backend. Returns True on success, False on failure.
    NEVER raises — all exceptions are caught and logged.
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
        msg.send(fail_silently=True)

        logger.info(f"[Email ✅] '{subject}' → {to_email}")
        return True

    except Exception as e:
        logger.error(f"[Email ❌] '{subject}' → {to_email} | Error: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# 1. HOSTING EXPIRY WARNING
# ══════════════════════════════════════════════════════════════════════════════

def send_hosting_expiry_warning(website, days: int = None) -> bool:
    """
    Send the correct expiry warning email based on days remaining.
      - 7 days  → hosting_7days_warning.html  (friendly reminder)
      - 3 days  → hosting_3days_warning.html  (urgent notice)
      - other   → hosting_7days_warning.html  (fallback)
    """
    client = website.client
    raw_days = (website.hosting_end_date - timezone.now().date()).days
    if days is None:
        days = raw_days

    if days <= 3:
        template  = 'hosting_3days_warning.html'
        subject   = f"🚨 URGENT — {website.name} suspends in 3 days! Renew now"
    else:
        template  = 'hosting_7days_warning.html'
        subject   = f"⏰ Hosting Expiry Notice — {website.name} expires in 7 days"

    return _send(
        subject=subject,
        template=template,
        context={
            'client_name':  client.name,
            'website_name': website.name,
            'website_url':  website.url,
            'expiry_date':  website.hosting_end_date.strftime('%d %B %Y'),
            'days_left':    max(days, 0),
            'monthly_cost': website.monthly_cost,
        },
        to_email=client.email,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 2. WEBSITE SUSPENDED
# ══════════════════════════════════════════════════════════════════════════════

def send_website_suspended(website, reason: str = 'Hosting payment overdue') -> bool:
    """Send suspension notice with full restore instructions."""
    client = website.client
    return _send(
        subject=f"🔒 SUSPENDED — {website.name} is now offline | Pay to restore",
        template='website_suspended.html',
        context={
            'client_name':        client.name,
            'website_name':       website.name,
            'website_url':        website.url,
            'reason':             reason,
            'suspended_date':     timezone.now().strftime('%d %B %Y'),
            'suspension_message': getattr(website, 'suspension_message', ''),
            'monthly_cost':       website.monthly_cost,
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
    Check ALL active websites and email plans and send warnings / auto-suspend.
    Call this daily via management command or cron-job.org.

    Auto-suspend triggers when days_until_expiry <= 0 (today OR past).
    Warning emails sent at: warning_days_before, 3, 1 days.

    Returns dict with counts: { sent, skipped, errors, suspended }
    """
    from apps.models import ManagedWebsite, DomainRecord, EmailHostingPlan

    sent = skipped = errors = suspended = 0
    today = timezone.now().date()

    # ══════════════════════════════════════════════════════════════
    # WEBSITE HOSTING
    # ══════════════════════════════════════════════════════════════

    active_sites = ManagedWebsite.objects.filter(
        status='active',
    ).select_related('client')

    for site in active_sites:
        raw_days = (site.hosting_end_date - today).days  # real delta, can be negative

        # ── Auto-suspend: day 0 or past ───────────────────────────
        if raw_days <= 0 and site.auto_suspend_on_expiry:
            site.status = 'suspended'
            site.suspension_message = (
                'Your hosting has expired. Please make a payment to restore your website.'
            )
            site.save(update_fields=['status', 'suspension_message'])
            ok = send_website_suspended(site, reason='Hosting expired')
            suspended += 1
            sent += 1 if ok else 0
            errors += 0 if ok else 1
            logger.info(f"[AutoSuspend] {site.name} — expired {site.hosting_end_date}")
            continue

        # ── Expiry warnings for still-active sites ─────────────────
        # 7 days: friendly reminder | 3 days: urgent | 1 day: final
        if site.send_expiry_warnings:
            if raw_days == 7:
                ok = send_hosting_expiry_warning(site, days=7)
                sent += 1 if ok else 0
                errors += 0 if ok else 1
            elif raw_days == 3:
                ok = send_hosting_expiry_warning(site, days=3)
                sent += 1 if ok else 0
                errors += 0 if ok else 1
            elif raw_days == 1:
                ok = send_hosting_expiry_warning(site, days=1)
                sent += 1 if ok else 0
                errors += 0 if ok else 1
            else:
                skipped += 1

    # ══════════════════════════════════════════════════════════════
    # EMAIL HOSTING
    # ══════════════════════════════════════════════════════════════

    active_email = EmailHostingPlan.objects.filter(
        status='active',
    ).select_related('client')

    for plan in active_email:
        raw_days = (plan.end_date - today).days

        # ── Auto-suspend: day 0 or past ───────────────────────────
        if raw_days <= 0 and plan.auto_suspend_on_expiry:
            plan.status = 'suspended'
            plan.suspension_message = (
                'Your email hosting has expired. Please make a payment to restore your service.'
            )
            plan.save(update_fields=['status', 'suspension_message'])
            # Send suspension notification
            try:
                from django.core.mail import send_mail
                from django.conf import settings as djsettings
                send_mail(
                    subject=f'🔒 Email Hosting Suspended — {plan.email_domain}',
                    message=(
                        f'Dear {plan.client.name},\n\n'
                        f'Your email hosting for {plan.email_domain} has been suspended '
                        f'due to non-payment.\n\n'
                        f'Please contact JamiiTek to restore your service.\n\n'
                        f'— JamiiTek Team'
                    ),
                    from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.co.tz'),
                    recipient_list=[plan.client.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"[EmailSuspend] {plan.email_domain} — {e}")
            suspended += 1
            logger.info(f"[AutoSuspend-Email] {plan.email_domain} — expired {plan.end_date}")
            continue

        # ── Expiry warnings ───────────────────────────────────────
        if plan.send_expiry_warnings:
            if raw_days in [plan.warning_days_before, 7, 3, 1]:
                # Basic expiry warning email for email hosting
                try:
                    from django.core.mail import send_mail
                    from django.conf import settings as djsettings
                    send_mail(
                        subject=f'⚠ Email Hosting Expiry — {plan.email_domain} expires in {raw_days} days',
                        message=(
                            f'Dear {plan.client.name},\n\n'
                            f'Your email hosting for {plan.email_domain} expires in {raw_days} day(s) '
                            f'on {plan.end_date.strftime("%d %B %Y")}.\n\n'
                            f'Please make a payment to avoid service interruption.\n\n'
                            f'— JamiiTek Team'
                        ),
                        from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', 'noreply@jamiitek.co.tz'),
                        recipient_list=[plan.client.email],
                        fail_silently=True,
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"[EmailWarning] {plan.email_domain} — {e}")
                    errors += 1
            else:
                skipped += 1

    # ══════════════════════════════════════════════════════════════
    # DOMAIN warnings
    # ══════════════════════════════════════════════════════════════

    domains = DomainRecord.objects.filter(
        status='active',
        send_renewal_warnings=True
    ).select_related('website__client')

    for domain in domains:
        raw_days = (domain.expiry_date - today).days
        if raw_days in [domain.warning_days_before, 14, 7, 3, 1]:
            ok = send_domain_expiry_warning(domain)
            sent += 1 if ok else 0
            errors += 0 if ok else 1
        else:
            skipped += 1

    logger.info(f"[BulkEmail] Done — sent:{sent} suspended:{suspended} skipped:{skipped} errors:{errors}")
    return {'sent': sent, 'skipped': skipped, 'errors': errors, 'suspended': suspended}