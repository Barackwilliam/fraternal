"""
Pesapal API 3.0 client (JSON).

Inashughulikia:
  • RequestToken  — pata Bearer token (imecache ~4 dakika)
  • RegisterIPN   — sajili URL ya taarifa (mara moja; ipn_id imecache/env)
  • SubmitOrderRequest — anzisha malipo, pata redirect_url + order_tracking_id
  • GetTransactionStatus — angalia hali halisi ya malipo

Sandbox:  https://cybqa.pesapal.com/pesapalv3
Live:     https://pay.pesapal.com/v3

Weka env: PESAPAL_CONSUMER_KEY, PESAPAL_CONSUMER_SECRET, PESAPAL_ENV (sandbox|live),
          PESAPAL_IPN_ID (hiari — ikikosekana tunasajili moja kwa moja)
"""
import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

_TIMEOUT = 30
_TOKEN_CACHE_KEY = 'pesapal_token_v3'
_IPN_CACHE_KEY = 'pesapal_ipn_id_v3'


class PesapalError(Exception):
    """Hitilafu yoyote kutoka Pesapal au mtandao."""


class PesapalClient:
    def __init__(self):
        self.key = getattr(settings, 'PESAPAL_CONSUMER_KEY', '')
        self.secret = getattr(settings, 'PESAPAL_CONSUMER_SECRET', '')
        env = (getattr(settings, 'PESAPAL_ENV', 'sandbox') or 'sandbox').lower()
        self.env = env
        if env == 'live':
            self.base = 'https://pay.pesapal.com/v3'
        else:
            self.base = 'https://cybqa.pesapal.com/pesapalv3'

    # ── ndani ─────────────────────────────────────────────
    @property
    def configured(self):
        return bool(self.key and self.secret)

    def _headers(self, token=None):
        h = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if token:
            h['Authorization'] = f'Bearer {token}'
        return h

    def _post(self, path, json_body, token=None):
        url = f'{self.base}{path}'
        try:
            r = requests.post(url, json=json_body, headers=self._headers(token), timeout=_TIMEOUT)
        except requests.RequestException as e:
            raise PesapalError(f'Mtandao umeshindikana: {e}') from e
        return self._parse(r, url)

    def _get(self, path, params=None, token=None):
        url = f'{self.base}{path}'
        try:
            r = requests.get(url, params=params or {}, headers=self._headers(token), timeout=_TIMEOUT)
        except requests.RequestException as e:
            raise PesapalError(f'Mtandao umeshindikana: {e}') from e
        return self._parse(r, url)

    def _parse(self, r, url):
        try:
            data = r.json()
        except ValueError:
            raise PesapalError(f'Jibu si JSON kutoka {url}: HTTP {r.status_code}')
        # Pesapal huweka hitilafu ndani ya `error` hata kwa HTTP 200
        err = data.get('error') if isinstance(data, dict) else None
        if err and (err.get('code') or err.get('message')):
            msg = err.get('message') or err.get('code')
            raise PesapalError(f'Pesapal: {msg}')
        if r.status_code >= 400:
            raise PesapalError(f'Pesapal HTTP {r.status_code}: {data}')
        return data

    # ── Auth ──────────────────────────────────────────────
    def get_token(self, force=False):
        if not self.configured:
            raise PesapalError('PESAPAL_CONSUMER_KEY / PESAPAL_CONSUMER_SECRET hazijawekwa.')
        if not force:
            cached = cache.get(_TOKEN_CACHE_KEY)
            if cached:
                return cached
        data = self._post('/api/Auth/RequestToken', {
            'consumer_key': self.key,
            'consumer_secret': self.secret,
        })
        token = data.get('token')
        if not token:
            raise PesapalError(f'Hakuna token kwenye jibu: {data}')
        # Token huisha baada ya dakika 5 — tunacache dakika 4
        cache.set(_TOKEN_CACHE_KEY, token, 240)
        return token

    # ── IPN ───────────────────────────────────────────────
    def get_ipn_id(self, ipn_url):
        """
        Rudisha notification_id. Kipaumbele:
          1) settings.PESAPAL_IPN_ID (env — imesajiliwa mara moja)
          2) cache
          3) sajili sasa hivi na uweke kwenye cache
        """
        env_id = getattr(settings, 'PESAPAL_IPN_ID', '')
        if env_id:
            return env_id
        cached = cache.get(_IPN_CACHE_KEY)
        if cached:
            return cached
        token = self.get_token()
        data = self._post('/api/URLSetup/RegisterIPN', {
            'url': ipn_url,
            'ipn_notification_type': 'POST',
        }, token=token)
        ipn_id = data.get('ipn_id')
        if not ipn_id:
            raise PesapalError(f'Kusajili IPN kumeshindikana: {data}')
        cache.set(_IPN_CACHE_KEY, ipn_id, 60 * 60 * 24 * 30)
        return ipn_id

    def register_ipn(self, ipn_url, notification_type='POST'):
        """Kwa matumizi ya moja kwa moja (mfano management command)."""
        token = self.get_token()
        return self._post('/api/URLSetup/RegisterIPN', {
            'url': ipn_url,
            'ipn_notification_type': notification_type,
        }, token=token)

    # ── Order ─────────────────────────────────────────────
    def submit_order(self, *, merchant_reference, amount, currency, description,
                     callback_url, ipn_id, email='', phone='', first_name='', last_name=''):
        token = self.get_token()
        billing = {}
        if email:
            billing['email_address'] = email
        if phone:
            billing['phone_number'] = phone
        if first_name:
            billing['first_name'] = first_name
        if last_name:
            billing['last_name'] = last_name
        # Pesapal inahitaji angalau email au phone
        if 'email_address' not in billing and 'phone_number' not in billing:
            billing['email_address'] = 'info@jamiitek.com'

        body = {
            'id': merchant_reference,
            'currency': currency,
            'amount': float(amount),
            'description': (description or 'JamiiTek Payment')[:100],
            'callback_url': callback_url,
            'notification_id': ipn_id,
            'billing_address': billing,
        }
        data = self._post('/api/Transactions/SubmitOrderRequest', body, token=token)
        if not data.get('redirect_url') or not data.get('order_tracking_id'):
            raise PesapalError(f'SubmitOrderRequest jibu pungufu: {data}')
        return data  # {order_tracking_id, merchant_reference, redirect_url, ...}

    # ── Status ────────────────────────────────────────────
    def get_status(self, order_tracking_id):
        token = self.get_token()
        return self._get('/api/Transactions/GetTransactionStatus',
                         params={'orderTrackingId': order_tracking_id}, token=token)


# Ramani ya status_code ya Pesapal → hali yetu
STATUS_MAP = {
    0: 'invalid',
    1: 'completed',
    2: 'failed',
    3: 'reversed',
}
