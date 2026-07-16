"""
Render API — kusajili custom domains za wateja premium AUTOMATIC,
bila kufungua Render dashboard.

Env vars zinazohitajika (Render → Environment):
    RENDER_API_KEY     — kutoka Render → Account Settings → API Keys
    RENDER_SERVICE_ID  — ID ya service yako (inaanza na 'srv-...', ipo kwenye
                         URL ya dashboard: dashboard.render.com/web/srv-XXXX)

Bila env hizi, mfumo unaendelea kufanya kazi — domain inaingia database
na routing inafanya kazi, ila utaongeza domain Render kwa mkono.
Docs: https://api-docs.render.com/reference/create-custom-domain
"""
import os
import logging

import requests

logger = logging.getLogger(__name__)

API_BASE = 'https://api.render.com/v1'
TIMEOUT = 15


def _config():
    key = os.getenv('RENDER_API_KEY')
    service = os.getenv('RENDER_SERVICE_ID')
    if not key or not service:
        return None
    return {'key': key, 'service': service}


def _headers(key):
    return {
        'Authorization': f'Bearer {key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }


def is_configured() -> bool:
    return _config() is not None


def add_custom_domain(domain: str):
    """
    Sajili domain kwenye Render service (SSL inajitengeneza yenyewe).
    Returns: (ok: bool, message: str)
    """
    cfg = _config()
    if cfg is None:
        return False, ('Auto-registration is not configured — add the domain '
                       'manually on Render (Settings → Custom Domains).')
    try:
        res = requests.post(
            f"{API_BASE}/services/{cfg['service']}/custom-domains",
            headers=_headers(cfg['key']),
            json={'name': domain},
            timeout=TIMEOUT,
        )
        if res.status_code in (200, 201):
            return True, (f'"{domain}" has been registered on our servers. '
                          'SSL activates automatically once the CNAME record is detected.')
        if res.status_code == 409:
            return True, f'"{domain}" is already registered on our servers.'
        logger.error('Render add domain failed [%s]: %s', res.status_code, res.text[:300])
        return False, ('Automatic registration failed — our team has been notified '
                       'and will activate the domain manually.')
    except requests.RequestException:
        logger.exception('Render API unreachable')
        return False, ('Could not reach the registration service — our team will '
                       'activate the domain manually.')


def remove_custom_domain(domain: str):
    """Ondoa domain kwenye Render (best-effort — haizuii chochote ikishindwa)."""
    cfg = _config()
    if cfg is None or not domain:
        return
    try:
        # Render inatambua domain kwa jina lake kwenye endpoint hii
        res = requests.delete(
            f"{API_BASE}/services/{cfg['service']}/custom-domains/{domain}",
            headers=_headers(cfg['key']),
            timeout=TIMEOUT,
        )
        if res.status_code not in (200, 204, 404):
            logger.warning('Render remove domain [%s]: %s', res.status_code, res.text[:200])
    except requests.RequestException:
        logger.exception('Render API unreachable (remove)')


def check_dns(domain: str, target: str = 'jamiitek.onrender.com') -> bool:
    """
    Ukaguzi rahisi wa DNS: je domain ya mteja ina-resolve kwenda IP zile zile
    za service yetu? (CNAME check ya takriban, bila dnspython.)
    """
    import socket
    try:
        ours = {ai[4][0] for ai in socket.getaddrinfo(target, 443)}
        theirs = {ai[4][0] for ai in socket.getaddrinfo(domain, 443)}
        return bool(ours & theirs)
    except OSError:
        return False
