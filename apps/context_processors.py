# apps/context_processors.py
"""
Context processors — kuweka variables zote za template kwenye context
"""

from django.conf import settings


def turnstile_context(request):
    """
    Sitekey ndiyo public, inaeleweka kwenye browser
    Secret hairuhusu kuonekana kwa frontend — stay kwenye backend tu
    """
    return {
        "TURNSTILE_ENABLED": settings.TURNSTILE_ENABLED,
        "TURNSTILE_SITEKEY": settings.TURNSTILE_SITEKEY if settings.TURNSTILE_ENABLED else "",
        "PESAPAL_ENABLED": getattr(settings, "PESAPAL_ENABLED", False),
    }

# ── Sidebar: ni kipengele kipi kimewashwa ────────────────────────────────
# Awali sidebar ilitumia `{% if 'website' in request.resolver_match.url_name %}`.
# Hiyo ni mechi ya sehemu ya jina, kwa hiyo url_name kama 'websitetemplate_edit'
# au 'client_portal_home' zilikuwa zinawasha kipengele kisicho sahihi. Ramani
# hii ni wazi: url_name -> kipengele.
_NAV_EXACT = {
    'management_dashboard': 'dashboard',
    'manage_builder': 'builder',
    'manage_chatbot': 'chatbot',
    'manage_bot_clients': 'bot_clients',
    'manage_bot_payments': 'bot_payments',
    'infra_overview': 'infra',
    'infra_audit': 'infra_audit',
    'lead_list': 'leads',
    'profile_builder': 'profile',
}

_NAV_PREFIX = (
    ('website',            'websites'),
    ('client',             'clients'),
    ('domain',             'domains'),
    ('email_hosting',      'email'),
    ('invoice',            'invoices'),
    ('receipt',            'receipts'),
    ('proposal_builder',   'proposals'),
    ('contract_builder',   'contracts'),
    ('infra',              'infra'),
)


def sidebar_nav(request):
    match = getattr(request, 'resolver_match', None)
    name = getattr(match, 'url_name', '') or ''

    if name in _NAV_EXACT:
        return {'nav': _NAV_EXACT[name]}

    for prefix, key in _NAV_PREFIX:
        if name.startswith(prefix):
            return {'nav': key}

    return {'nav': ''}
