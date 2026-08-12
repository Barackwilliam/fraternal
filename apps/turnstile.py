# apps/turnstile.py
"""
Cloudflare Turnstile integration — CSRF na bot protection kwa forms zote
Turnstile is single-use, expires ~5 min, supports invisible + interactive modes
"""

import requests
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def get_client_ip(request):
    """Extract client IP from request (respects CloudFlare CF-Connecting-IP)"""
    if not request:
        return None
    # CloudFlare sets this header kama request inakuja kupitia CF
    xff = request.META.get("HTTP_CF_CONNECTING_IP") or request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def verify_token(token, ip=None):
    """
    Verify token with Cloudflare — token ni single-use, ina-expire baada ya ~5 min
    
    Returns: (ok: bool, codes: list)
    
    Kama TURNSTILE_ENABLED = False, kurudi True (pass watumiaji halali)
    Kama Cloudflare hapatikani, kurudi True (nusitunze watumiaji)
    """
    if not settings.TURNSTILE_ENABLED:
        return True, []
    if not token:
        return False, ["missing-input-response"]

    data = {
        "secret": settings.TURNSTILE_SECRET,
        "response": token
    }
    if ip:
        data["remoteip"] = ip

    try:
        r = requests.post(VERIFY_URL, data=data, timeout=6)
        result = r.json()
    except Exception:
        # Cloudflare ikishindikana, usifungie watumiaji halali nje — ni server error, si bot
        return True, ["verify-unreachable"]

    return bool(result.get("success")), result.get("error-codes", [])


class TurnstileWidget(forms.Widget):
    """
    Renders <div class="cf-turnstile"> — Cloudflare script inabadilisha hii kwenye iframe
    Invisible mode inayoonyesha checkbox tu kama shuku
    """
    is_hidden = False

    def render(self, name, value, attrs=None, renderer=None):
        if not settings.TURNSTILE_ENABLED:
            return mark_safe("")
        
        sitekey = settings.TURNSTILE_SITEKEY
        return mark_safe(
            f'<div class="cf-turnstile" '
            f'data-sitekey="{sitekey}" '
            f'data-theme="auto" '
            f'data-language="auto" '
            f'style="margin-bottom:1rem"></div>'
        )

    def value_from_datadict(self, data, files, name):
        # Cloudflare hutuma hii constant field name, si jina la form field
        return data.get("cf-turnstile-response")


class TurnstileField(forms.Field):
    """
    Custom field inayorender widget na kuvalidate token
    required=True tu kama TURNSTILE_ENABLED
    """
    widget = TurnstileWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("label", "")
        kwargs.setdefault("required", settings.TURNSTILE_ENABLED)
        kwargs.setdefault("initial", None)
        super().__init__(*args, **kwargs)


class TurnstileFormMixin:
    """
    Ongeza kwenye form yoyote: class MyForm(TurnstileFormMixin, forms.Form)
    
    Lazima upitishe `request=request` kwenye form initialization:
        form = MyForm(request.POST or None, request=request)
    
    Turnstile token ni single-use:
    - Kama inathibitishwa na mixin, middleware HAIRUHUSU kutest tena
    - Chagua njia moja kwa form: mixin AU middleware, sio zote
    """

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        
        # Ongeza field kama TURNSTILE ni enabled
        if settings.TURNSTILE_ENABLED:
            self.fields["turnstile"] = TurnstileField()

    def clean(self):
        cleaned = super().clean()
        
        if not settings.TURNSTILE_ENABLED:
            return cleaned
        
        token = cleaned.get("turnstile")
        ok, codes = verify_token(token, get_client_ip(self.request))
        
        if not ok:
            self.add_error(
                "turnstile",
                _("Uthibitisho umeshindikana. Tafadhali jaribu tena.") if settings.LANGUAGE_CODE.startswith('sw') 
                else _("Verification failed. Please try again.")
            )
        
        return cleaned