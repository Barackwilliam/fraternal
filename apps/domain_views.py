# apps/domain_views.py
"""
Public domain search endpoint used by the homepage search bar.

GET /domain-check/?q=example.co.tz  ->  JSON
"""

import hashlib

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .domain_checker import check_domain, TLD_PRICES, normalize

# Cache successful lookups so repeat searches don't hit RDAP/DNS again
RESULT_TTL = 60 * 30          # 30 minutes
THROTTLE_LIMIT = 25           # lookups
THROTTLE_WINDOW = 60          # per minute, per IP

WHATSAPP_NUMBER = '255629712678'


def _client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _throttled(request):
    ip = _client_ip(request)
    if not ip:
        return False
    key = 'domchk:' + hashlib.sha256(ip.encode()).hexdigest()[:20]
    hits = cache.get(key, 0)
    if hits >= THROTTLE_LIMIT:
        return True
    cache.set(key, hits + 1, THROTTLE_WINDOW)
    return False


@require_GET
def domain_check(request):
    raw = request.GET.get('q', '')
    tld = request.GET.get('tld', '').strip()

    # The homepage sends the name and the extension separately.
    # Only append the extension when the user hasn't typed one already.
    if tld and '.' not in normalize(raw):
        raw = f'{normalize(raw)}{tld}'

    domain = normalize(raw)

    if not domain:
        return JsonResponse({
            'status': 'invalid',
            'message': 'Enter a domain name, for example: mybusiness.co.tz',
        }, status=400)

    if _throttled(request):
        return JsonResponse({
            'status': 'throttled',
            'message': 'Too many searches in a short time. Please try again in a minute.',
        }, status=429)

    cache_key = f'domres:{domain}'
    result = cache.get(cache_key)
    if result is None:
        result = check_domain(domain)
        if result['status'] in ('taken', 'available'):
            cache.set(cache_key, result, RESULT_TTL)

    result['messages'] = _messages(result)
    result['whatsapp'] = _whatsapp_link(result)
    return JsonResponse(result)


def _messages(result):
    """Copy for each outcome, so the template stays presentational."""
    domain = result.get('domain', '')
    status = result.get('status')

    if status == 'taken':
        return {
            'headline': f'{domain} is already registered',
            'body': 'This domain already has an owner. Try a different name, '
                    'or pick one of the available extensions below.',
        }

    if status == 'available':
        low = result.get('confidence') == 'low'
        return {
            'headline': f'{domain} is available',
            'body': (
                'Get in touch and we will register it for you before someone else does.'
                if not low else
                'This one looks free. Get in touch and we will confirm it with the '
                'registry and register it for you.'
            ),
        }

    if status == 'invalid':
        return {
            'headline': 'That name is not valid',
            'body': 'Enter a full domain name, for example: mybusiness.co.tz',
        }

    return {
        'headline': f'We could not verify {domain}',
        'body': 'Get in touch and we will check with the registry and confirm for you.',
    }


def _whatsapp_link(result):
    domain = result.get('domain', '')
    if result.get('status') == 'available':
        text = f'Hello JamiiTek, I would like to register the domain {domain}. Please help me get it.'
    else:
        text = f'Hello JamiiTek, I need help with the domain {domain}.'
    from urllib.parse import quote
    return f'https://wa.me/{WHATSAPP_NUMBER}?text={quote(text)}'


def domain_prices():
    """Helper for the homepage view context."""
    return [
        {'tld': tld, 'price': price}
        for tld, price in list(TLD_PRICES.items())[:5]
    ]