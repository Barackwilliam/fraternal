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
    }