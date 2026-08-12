# apps/turnstile_middleware.py
"""
Cloudflare Turnstile middleware — OPT-IN MODEL.

MUHIMU: Middleware hii inakagua TU njia zilizoorodheshwa kwenye PROTECTED_PATHS.
Kila kitu kingine kinapita bila kuguswa.

Sababu: mtindo wa "zuia kila kitu, ondoa vichache" ulikuwa unavunja /manage/,
/portal/, /proposals/, na forms za websites za wateja kwenye subdomains —
kwa sababu forms hizo hazina widget, hivyo hazitumi token, hivyo kila POST
inarudi 403 "missing-input-response".

KANUNI: Ongeza path hapa TU baada ya kuhakikisha template yake ina widget:
    <div class="cf-turnstile" data-sitekey="{{ TURNSTILE_SITEKEY }}"></div>

Kama form inatumia TurnstileFormMixin, USIIWEKE hapa. Token ni single-use —
ikikaguliwa mara mbili, ya pili inashindwa.
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from apps.turnstile import verify_token, get_client_ip

logger = logging.getLogger(__name__)


# ── Njia zinazolindwa ─────────────────────────────────────────────
# Public forms TU. Kila moja LAZIMA iwe na widget kwenye template yake.
# Ni exact match kwenye request.path (si prefix) ili /manage/ isiingie kwa bahati mbaya.
PROTECTED_PATHS = {
    # "/contact/",
    # "/domain-check/",
}


def _wants_json(request):
    """
    Browsers hutuma Accept: text/html,...,*/*;q=0.8 — hivyo request.accepts('application/json')
    inarudi True KILA MARA. Tumia XHR header badala yake.
    """
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.content_type == "application/json"
    )


class TurnstileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == "POST"
            and settings.TURNSTILE_ENABLED
            and request.path in PROTECTED_PATHS
        ):
            token = request.POST.get("cf-turnstile-response")
            ok, codes = verify_token(token, get_client_ip(request))

            if not ok:
                logger.warning(
                    "Turnstile rejected POST %s from %s: %s",
                    request.path, get_client_ip(request), codes,
                )

                if _wants_json(request):
                    return JsonResponse(
                        {"error": "Uthibitisho umeshindikana. Tafadhali jaribu tena."},
                        status=403,
                    )

                # Browser: rudisha mtumiaji kwenye form na ujumbe, si JSON tupu
                messages.error(
                    request,
                    "Uthibitisho umeshindikana. Tafadhali jaribu tena.",
                )
                return redirect(request.path)

        return self.get_response(request)