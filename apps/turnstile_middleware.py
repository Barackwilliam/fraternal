# apps/turnstile_middleware.py
"""
Optional middleware kwa forms zisizotumia Django Forms (raw HTML)
Hadithi: Token ni single-use. Kama form uses TurnstileFormMixin, middleware itakataa request
(token iliyothibitishwa tayari ni invalid).

SOLUTION: Chagua moja tu kwa form:
  - TurnstileFormMixin (kwa Django forms) — Recommended
  - Middleware (kwa raw HTML forms) — Kwa edges only

Mara nyingi TurnstileFormMixin ni decision sahihi.
"""

from django.conf import settings
from django.http import JsonResponse
from apps.turnstile import verify_token, get_client_ip


# Routes zisizohitaji bot check — webhooks, admin, API, n.k.
EXEMPT_PREFIXES = (
    "/admin/",
    "/api/",
    "/webhooks/",              # Green API, Pesapal IPN, n.k.
    "/payments/callback",      # Pesapal return URL
    "/api/",                   # REST API endpoints
)


class TurnstileMiddleware:
    """
    POST requests lazima zina cf-turnstile-response token, kwa sehemu zisizoinunguza.
    
    MATUKIO:
    - Entry point: /contact/ (POST) — middleware itacheck
    - Entry point: /select-website/ (POST) — middleware itacheck
    - Entry point: /webhooks/pesapal/ (POST) — EXEMPT (webhook ni server-to-server, si user bot)
    - Entry point: /admin/login/ (POST) — EXEMPT (admin wana session na other protections)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Chuja — POST tu, kama Turnstile ni enabled, kama route sio exempt
        if (
            request.method == "POST"
            and settings.TURNSTILE_ENABLED
            and not any(request.path.startswith(prefix) for prefix in EXEMPT_PREFIXES)
        ):
            # Verify token
            ok, codes = verify_token(
                request.POST.get("cf-turnstile-response"),
                get_client_ip(request)
            )
            
            if not ok:
                # Reject kwa 403 Forbidden
                if request.accepts("application/json"):
                    return JsonResponse(
                        {
                            "error": "Uthibitisho umeshindikana. Tafadhali jaribu tena." 
                                    if settings.LANGUAGE_CODE.startswith('sw')
                                    else "Verification failed. Please try again.",
                            "codes": codes
                        },
                        status=403
                    )
                else:
                    # Fallback: Return HTML error
                    from django.http import HttpResponse
                    return HttpResponse(
                        f"<h1>Verification Failed</h1><p>Codes: {codes}</p>",
                        status=403
                    )
        
        return self.get_response(request)