"""
Ulinzi wa jumla wa mfumo (apps/security.py).

1. Kuzuia kubahatisha nywila (brute force) — kwa logins ZOTE:
   Client Portal, JamiiBot, Web Builder, /manage/ na /admin/. Zote zinapitia
   `django.contrib.auth.authenticate(request, ...)`, kwa hiyo ulinzi uko
   kwenye authentication backend moja badala ya kila view.
     • Akaunti moja: makosa 5 ndani ya dakika 15 → imefungwa dakika 15
     • IP moja:      makosa 30 ndani ya dakika 15 → imefungwa dakika 15
   Hata nywila sahihi inakataliwa wakati imefungwa, kwa hiyo mshambulizi
   hawezi kujua kama amepata nywila.

2. Security headers za ziada (SecurityHeadersMiddleware): Permissions-Policy,
   CSP ya msingi isiyovunja inline styles,
   na `Cache-Control: no-store` kwa kurasa za mtu aliyeingia (ili kitufe cha
   "Back" kwenye kompyuta ya pamoja kisionyeshe data baada ya logout).
"""
import hashlib
import logging

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver

from apps.turnstile import get_client_ip

log = logging.getLogger('apps.security')

WINDOW_SECONDS = 15 * 60
MAX_PER_ACCOUNT = 5
MAX_PER_IP = 30


def _key(kind, value):
    digest = hashlib.sha256(str(value or '').strip().lower().encode()).hexdigest()[:32]
    return f'sec:login:{kind}:{digest}'


def _keys(request, username):
    keys = []
    if username:
        keys.append((_key('user', username), MAX_PER_ACCOUNT))
    ip = get_client_ip(request) if request is not None else None
    if ip:
        keys.append((_key('ip', ip), MAX_PER_IP))
    return keys


def login_locked(request, username):
    """True kama akaunti au IP hii imefungwa kwa muda kwa makosa mengi."""
    for key, limit in _keys(request, username):
        if (cache.get(key) or 0) >= limit:
            return True
    return False


def lockout_message():
    return ('Too many failed sign-in attempts. For your security this account '
            'is locked for 15 minutes. Try again later or reset your password.')


class ThrottledModelBackend(ModelBackend):
    """ModelBackend ya kawaida + kufunga baada ya makosa mengi."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('username')
        if login_locked(request, username):
            if request is not None:
                request.login_locked = True
            log.warning('Login blocked (locked out): user=%r ip=%s',
                        username, get_client_ip(request))
            # PermissionDenied inasimamisha backends zote — hata nywila sahihi
            raise PermissionDenied
        return super().authenticate(request, username=username, password=password, **kwargs)


@receiver(user_login_failed)
def _count_failure(sender, credentials, request=None, **kwargs):
    if request is not None and getattr(request, 'login_locked', False):
        return
    username = (credentials or {}).get('username')
    for key, limit in _keys(request, username):
        # add() haiandiki juu ya kilichopo, kwa hiyo dirisha halirefushwi
        cache.add(key, 0, WINDOW_SECONDS)
        try:
            count = cache.incr(key)
        except ValueError:
            cache.set(key, 1, WINDOW_SECONDS)
            count = 1
        if count == limit:
            log.warning('Login lockout started: %s (user=%r ip=%s)',
                        key.split(':')[2], username, get_client_ip(request))


@receiver(user_logged_in)
def _reset_on_success(sender, request=None, user=None, **kwargs):
    if user is not None:
        cache.delete(_key('user', user.get_username()))


# ── Security headers ─────────────────────────────────────────────
PERMISSIONS_POLICY = ', '.join([
    'accelerometer=()', 'autoplay=()', 'camera=()', 'display-capture=()',
    'geolocation=()', 'gyroscope=()', 'magnetometer=()', 'microphone=()',
    'midi=()', 'payment=(self)', 'usb=()', 'interest-cohort=()',
])

# CSP ya msingi: haizuii inline <style>/<script> (kurasa nyingi zinazitumia),
# lakini inazuia mbinu hatari zaidi za XSS: <base> ya kigeni, plugins
# (<object>/<embed>), na kutuma form kwenda http au javascript:.
CONTENT_SECURITY_POLICY = '; '.join([
    "base-uri 'self'",
    "object-src 'none'",
    "form-action 'self' https:",
    'upgrade-insecure-requests',
])

_PRIVATE_PREFIXES = ('/portal/', '/chatbot/', '/builder/', '/manage/', '/admin/')


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault('Permissions-Policy', PERMISSIONS_POLICY)
        response.headers.setdefault('X-Permitted-Cross-Domain-Policies', 'none')
        response.headers.setdefault('Content-Security-Policy', CONTENT_SECURITY_POLICY)

        user = getattr(request, 'user', None)
        ctype = response.headers.get('Content-Type', '')
        if (user is not None and user.is_authenticated
                and request.path.startswith(_PRIVATE_PREFIXES)
                and ctype.startswith('text/html')):
            response.headers['Cache-Control'] = 'no-store, private'
        return response


def password_problems(password, username='', email='', full_name=''):
    """
    Makosa ya nywila kwa mujibu wa AUTH_PASSWORD_VALIDATORS (urefu, nywila
    za kawaida kama 'password123', namba tupu, kufanana na jina/email).
    Fomu za usajili za portal na JamiiBot hazikuyatumia — '12345678' ilikubaliwa.
    """
    from django.contrib.auth.models import User
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    parts = (full_name or '').split()
    probe = User(username=username or '', email=email or '',
                 first_name=parts[0] if parts else '',
                 last_name=' '.join(parts[1:]))
    try:
        validate_password(password or '', user=probe)
    except ValidationError as e:
        return list(e.messages)
    return []


def same_site_logout(view):
    """
    Logout kwa link (GET) inabaki kwa urahisi wa sidebar, lakini tovuti ya
    nje haiwezi tena kumtoa mtu kwa <img src=".../logout/"> (login-CSRF /
    phishing). Browsers zote za kisasa zinatuma `Sec-Fetch-Site`.
    """
    from functools import wraps
    from django.shortcuts import redirect

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST' and request.headers.get('Sec-Fetch-Site') == 'cross-site':
            return redirect('/')
        return view(request, *args, **kwargs)
    return wrapper
