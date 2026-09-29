"""Domain za wateja — kuunganisha, kukagua, na kuondoa.

Mtiririko ni wa hatua tatu, na kila moja inaweza kukwama kwa sababu tofauti:

    1. DNS      — mteja ameelekeza domain yake kwetu?
    2. SSL      — Render amethibitisha na kutengeneza cheti?
    3. Website  — https://domain inaonyesha website SAHIHI?

Ukaguzi wa zamani (`render_api.check_dns`) uliangalia hatua ya 1 tu, kwa
kulinganisha IP. Hapa tunaangalia zote tatu na kutoa sababu ya wazi
kila inapokwama — kwa sababu "haifanyi kazi" haimsaidii mteja wala wewe.

Maelekezo ya DNS (kutoka docs za Render):
    domain kuu  (biashara.co.tz)      A      216.24.57.1
                                      au ALIAS/ANAME -> jamiitek.onrender.com
    www         (www.biashara.co.tz)  CNAME  jamiitek.onrender.com
    Rekodi zote za AAAA LAZIMA ziondolewe — Render ni IPv4 pekee, na AAAA
    inazuia cheti cha SSL kutengenezwa.
"""
import logging
import re
import socket

import requests
from django.utils import timezone

logger = logging.getLogger(__name__)

RENDER_HOST = 'jamiitek.onrender.com'
RENDER_APEX_IP = '216.24.57.1'

_DOMAIN_RE = re.compile(
    r'^(?=.{4,120}$)(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*\.[a-z]{2,24}$')


def normalize(raw):
    """'https://WWW.Biashara.co.tz/about' -> 'www.biashara.co.tz'"""
    d = (raw or '').strip().lower()
    d = re.sub(r'^[a-z]+://', '', d)
    d = d.split('/', 1)[0].split('?', 1)[0].split(':', 1)[0].rstrip('.')
    return d


def is_valid(domain):
    if not _DOMAIN_RE.match(domain or ''):
        return False
    # Domain zetu wenyewe si za mteja
    return not (domain == 'jamiitek.com' or domain.endswith('.jamiitek.com')
                or domain.endswith('.onrender.com'))


def is_apex(domain):
    """biashara.co.tz / biashara.com ni kuu; www.biashara.co.tz si kuu."""
    parts = domain.split('.')
    # .co.tz, .or.tz, .ac.tz, .go.tz, .co.ke, .co.uk … zina sehemu mbili za mwisho
    second_level = {'co', 'or', 'ac', 'go', 'ne', 'com', 'org', 'net', 'sc', 'me'}
    if len(parts) >= 3 and parts[-2] in second_level and len(parts[-1]) == 2:
        return len(parts) == 3
    return len(parts) == 2


def dns_records(domain):
    """Rekodi ambazo mteja anatakiwa kuweka — tayari kwa kunakili."""
    if is_apex(domain):
        return [
            {'type': 'A', 'name': '@', 'value': RENDER_APEX_IP,
             'note': 'Au ALIAS/ANAME kwenda ' + RENDER_HOST + ' kama mtoa huduma anaiunga mkono'},
            {'type': 'CNAME', 'name': 'www', 'value': RENDER_HOST, 'note': 'Ili www pia ifanye kazi'},
        ]
    sub = domain.split('.', 1)[0]
    return [{'type': 'CNAME', 'name': sub, 'value': RENDER_HOST, 'note': ''}]


def _ipv4(host):
    try:
        return {ai[4][0] for ai in socket.getaddrinfo(host, 443, socket.AF_INET)}
    except OSError:
        return set()


def _has_ipv6(host):
    try:
        return bool(socket.getaddrinfo(host, 443, socket.AF_INET6))
    except OSError:
        return False


def check(site):
    """Kagua hatua zote tatu na uhifadhi matokeo kwenye site.

    Inarudisha (status, message).
    """
    domain = site.custom_domain
    if not domain:
        return '', ''

    status, message = _check(domain, site)
    site.domain_status = status
    site.domain_message = message[:300]
    site.domain_checked_at = timezone.now()
    site.save(update_fields=['domain_status', 'domain_message', 'domain_checked_at'])
    return status, message


def _check(domain, site):
    # ── 1. DNS ──
    theirs = _ipv4(domain)
    if not theirs:
        return 'pending', ('Domain haijaelekezwa popote bado. Mteja aweke rekodi za DNS '
                           'zilizoonyeshwa hapa. Mabadiliko ya DNS yanaweza kuchukua hadi saa 24.')

    ours = _ipv4(RENDER_HOST) | {RENDER_APEX_IP}
    if not (theirs & ours):
        return 'pending', (f'Domain inaelekeza kwenye {", ".join(sorted(theirs))} — si kwetu. '
                           'Huenda bado inaelekeza kwenye hosting ya zamani. Rekebisha rekodi za DNS.')

    if _has_ipv6(domain):
        return 'error', ('Domain ina rekodi ya AAAA (IPv6). Render haitumii IPv6, na rekodi hii '
                         'inazuia cheti cha SSL kutengenezwa. Mteja aifute kwenye DNS yake.')

    # ── 2 & 3. SSL na website yenyewe ──
    try:
        r = requests.get(f'https://{domain}/', timeout=10, allow_redirects=True,
                         headers={'User-Agent': 'JamiiTek-DomainCheck/1.0'})
    except requests.exceptions.SSLError:
        return 'dns_ok', ('DNS iko sawa. Render bado anatengeneza cheti cha SSL — kwa kawaida '
                          'dakika chache hadi saa moja baada ya DNS kuwa sahihi.')
    except requests.RequestException as e:
        return 'dns_ok', f'DNS iko sawa, lakini website haijajibu bado ({type(e).__name__}).'

    if r.status_code >= 400:
        return 'error', (f'Website imejibu {r.status_code}. Hakikisha domain imeongezwa kwenye '
                         'Render (kitufe cha "Sajili tena Render").')

    # Je, ni website SAHIHI? (domain iliyoelekezwa kwetu lakini ikaonyesha
    # website nyingine ingekuwa hatari kuliko isiyofanya kazi kabisa)
    name = (site.site_name or '').strip()
    if name and name.lower() not in r.text.lower():
        return 'error', ('Domain inafunguka, lakini haionyeshi website ya ' + name + '. '
                         'Angalia kama website imechapishwa (published).')

    return 'active', 'Website iko live kwenye domain yake, pamoja na SSL.'


def connect(site, raw_domain):
    """Unganisha domain na website. Inarudisha (ok, message)."""
    from builder import render_api
    from builder.models import ClientWebsite

    domain = normalize(raw_domain)
    if not is_valid(domain):
        return False, f'"{raw_domain}" si domain sahihi. Mfano: biashara.co.tz au www.biashara.co.tz'

    alt = domain[4:] if domain.startswith('www.') else f'www.{domain}'
    clash = (ClientWebsite.objects.filter(custom_domain__in=[domain, alt])
             .exclude(pk=site.pk).first())
    if clash:
        return False, f'{domain} tayari imeunganishwa na website "{clash.site_name}".'

    old = site.custom_domain
    site.custom_domain = domain
    # Middleware inaelekeza custom domain kwa website za premium pekee
    site.is_premium = True
    site.domain_status = 'pending'
    site.domain_message = 'Imeunganishwa. Inasubiri mteja kuweka rekodi za DNS.'
    site.domain_added_at = timezone.now()
    site.domain_checked_at = None
    site.save()

    if old and old != domain:
        render_api.remove_custom_domain(old)

    ok, msg = render_api.add_custom_domain(domain)
    if not ok:
        site.domain_message = msg[:300]
        site.save(update_fields=['domain_message'])
        return True, f'{domain} imeunganishwa kwenye mfumo. ' + msg
    return True, f'{domain} imeunganishwa na kusajiliwa Render. Mpe mteja rekodi za DNS.'


def disconnect(site):
    from builder import render_api
    domain = site.custom_domain
    if not domain:
        return
    render_api.remove_custom_domain(domain)
    site.custom_domain = None
    site.domain_status = ''
    site.domain_message = ''
    site.domain_checked_at = None
    site.save(update_fields=['custom_domain', 'domain_status', 'domain_message', 'domain_checked_at'])
