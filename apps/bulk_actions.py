# apps/bulk_actions.py
"""
Suspend or activate several websites at once.

Each website is still written individually — this is a convenience wrapper
around the same per-site status field, not a shared one. That is what keeps
"suspend one" and "suspend all" behaving consistently.

Add to apps/urls.py:

    from . import bulk_actions

    path('manage/websites/bulk/', bulk_actions.bulk_website_action, name='bulk_website_action'),
    path('manage/clients/<int:pk>/suspend-all/', bulk_actions.suspend_client_websites, name='suspend_client_websites'),
    path('manage/clients/<int:pk>/activate-all/', bulk_actions.activate_client_websites, name='activate_client_websites'),
"""

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Client, ManagedWebsite
from .management_views import staff_required, _send_notification

DEFAULT_SUSPENSION_MESSAGE = (
    'This website has been suspended. Please contact us for more information.'
)


def _is_paid_up(website):
    """Still inside the period the client has already paid for."""
    return website.hosting_end_date > timezone.now().date()


def _apply(websites, action, reason, message, notify, user, include_paid=True):
    """
    Returns (changed, skipped, protected).

    `protected` counts sites left alone because the client has already paid
    for the current period. Suspending those would punish a client who is up
    to date on that site because of a debt on a different one.
    """
    changed = skipped = protected = 0

    for website in websites:
        if action == 'suspend':
            if website.status == 'suspended':
                skipped += 1
                continue
            if not include_paid and _is_paid_up(website):
                protected += 1
                continue
            website.status = 'suspended'
            website.suspension_reason = reason
            website.suspension_message = message or DEFAULT_SUSPENSION_MESSAGE
            website.save(update_fields=[
                'status', 'suspension_reason', 'suspension_message', 'updated_at'])
            if notify:
                _send_notification(
                    website, 'suspension',
                    f'Website Suspended — {website.name}',
                    f'Dear {website.client.name},\n\n'
                    f'Your website ({website.name}) has been suspended.\n\n'
                    f'Reason: {reason}\n\n{website.suspension_message}\n\n'
                    f'Contact us to resolve this.\n\nJamiiTek Team',
                    user)
        else:
            if website.status == 'active':
                skipped += 1
                continue
            website.status = 'active'
            website.suspension_reason = ''
            website.save(update_fields=['status', 'suspension_reason', 'updated_at'])
            if notify:
                _send_notification(
                    website, 'restoration',
                    f'Website Restored — {website.name}',
                    f'Dear {website.client.name},\n\n'
                    f'Your website ({website.name}) is active again.\n\n'
                    f'Thank you.\n\nJamiiTek Team',
                    user)
        changed += 1

    return changed, skipped, protected


def _report(request, action, changed, skipped, protected=0):
    verb = 'suspended' if action == 'suspend' else 'activated'
    if changed:
        messages.success(request, f'{changed} website{"" if changed == 1 else "s"} {verb}.')
    if skipped:
        messages.info(request, f'{skipped} already {verb} — left untouched.')
    if protected:
        messages.warning(
            request,
            f'{protected} website{"" if protected == 1 else "s"} left running — '
            'still inside a paid period. Tick "Include paid-up websites" to '
            'suspend those too.')
    if not any((changed, skipped, protected)):
        messages.error(request, 'No websites were selected.')


# ══════════════════════════════════════════════════════════════
@staff_required
@require_POST
def bulk_website_action(request):
    """Checkbox selection on the websites list."""
    action = request.POST.get('action')
    if action not in ('suspend', 'activate'):
        messages.error(request, 'Unknown action.')
        return redirect('website_list')

    pks = request.POST.getlist('selected')
    reason = request.POST.get('reason', '').strip()
    message = request.POST.get('suspension_message', '').strip()
    notify = request.POST.get('notify_client') == 'on'

    if action == 'suspend' and not reason:
        messages.error(request, 'A suspension reason is required.')
        return redirect('website_list')

    websites = ManagedWebsite.objects.filter(pk__in=pks).select_related('client')
    # Explicit tick-box selection — you already saw exactly which sites these are.
    changed, skipped, protected = _apply(
        websites, action, reason, message, notify, request.user, include_paid=True)
    _report(request, action, changed, skipped, protected)
    return redirect('website_list')


@staff_required
@require_POST
def suspend_client_websites(request, pk):
    """Every website belonging to one client."""
    client = get_object_or_404(Client, pk=pk)
    reason = request.POST.get('reason', '').strip()
    if not reason:
        messages.error(request, 'A suspension reason is required.')
        return redirect('client_detail_admin', pk=pk)

    # Default is to protect sites the client has already paid for.
    include_paid = request.POST.get('include_paid') == 'on'

    websites = client.managed_websites.select_related('client')
    changed, skipped, protected = _apply(
        websites, 'suspend', reason,
        request.POST.get('suspension_message', '').strip(),
        request.POST.get('notify_client') == 'on', request.user,
        include_paid=include_paid)
    _report(request, 'suspend', changed, skipped, protected)
    return redirect('client_detail_admin', pk=pk)


@staff_required
@require_POST
def activate_client_websites(request, pk):
    client = get_object_or_404(Client, pk=pk)
    websites = client.managed_websites.select_related('client')
    changed, skipped, protected = _apply(
        websites, 'activate', '', '',
        request.POST.get('notify_client') == 'on', request.user)
    _report(request, 'activate', changed, skipped, protected)
    return redirect('client_detail_admin', pk=pk)