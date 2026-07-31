"""
Cloudflare — DNS, SSL na analytics.

MUHIMU: hii inafanya kazi kwa domain YOYOTE inayotumia nameservers za
Cloudflare, bila kujali imesajiliwa wapi (Namecheap, WazoHost, tzNIC).

Haitoi tarehe ya kuisha kwa domain — hiyo iko kwa registrar. Tumia
rdap.py kwa hiyo.

Token: dash.cloudflare.com → My Profile → API Tokens → Create Token
Ruhusa zinazotosha (usiongeze zaidi):
    Zone         → Zone      → Read
    Zone         → DNS       → Read
    Zone         → Analytics → Read
Weka pia expiry date kwenye token.
"""
import logging
from datetime import datetime, timedelta, timezone as dt_timezone

from . import base
from .base import AdapterError, BaseAdapter

logger = logging.getLogger(__name__)

API = 'https://api.cloudflare.com/client/v4'


class CloudflareAdapter(BaseAdapter):

    provider = 'cloudflare'
    label = 'Cloudflare (DNS / CDN)'
    client_label = 'Domain & security'

    credential_fields = [
        {'key': 'api_token', 'label': 'API token', 'secret': True,
         'help': 'Zone:Read, DNS:Read, Analytics:Read'},
    ]

    @staticmethod
    def _headers(token):
        return {'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'}

    @classmethod
    def _get(cls, token, path, **kw):
        r = cls._request('GET', f'{API}{path}', headers=cls._headers(token), **kw)
        data = r.json()
        if not data.get('success', False):
            errs = data.get('errors') or [{}]
            raise AdapterError(errs[0].get('message', 'Cloudflare imekataa ombi.'))
        return data.get('result')

    @classmethod
    def discover(cls, creds):
        token = (creds or {}).get('api_token', '').strip()
        if not token:
            raise AdapterError('API token inahitajika.')

        zones = cls._get(token, '/zones', params={'per_page': 50})
        return [{
            'external_id': z['id'],
            'name': z['name'],
            'meta': {'status': z.get('status'),
                     'plan': (z.get('plan') or {}).get('name', '')},
        } for z in zones or []]

    # ── summary ──
    def summary(self):
        token = self.creds.get('api_token', '')
        zid = self.integration.external_id
        out = {}

        zone = self._get(token, f'/zones/{zid}')
        out[base.DNS_OK] = zone.get('status') == 'active'

        # SSL — cheti cha Universal SSL
        try:
            certs = self._get(token, f'/zones/{zid}/ssl/certificate_packs',
                              params={'status': 'all'})
            expiry, issuer = None, ''
            for pack in certs or []:
                for cert in pack.get('certificates') or []:
                    exp = cert.get('expires_on')
                    if exp and (expiry is None or exp < expiry):
                        expiry, issuer = exp, cert.get('issuer', '')
            if expiry:
                out[base.SSL_EXPIRY] = expiry[:10]
                out[base.SSL_ISSUER] = issuer or 'Cloudflare Universal SSL'
        except AdapterError as e:
            logger.info('SSL haipatikani kwa %s: %s', zid, e)

        # Wageni wa siku 30 — GraphQL analytics
        visits = self._visits_30d(token, zid)
        if visits is not None:
            out[base.MONTHLY_VISITS] = visits

        return out

    def _visits_30d(self, token, zid):
        since = (datetime.now(dt_timezone.utc) - timedelta(days=30)).date().isoformat()
        query = """
        query($zone: String!, $since: Date!) {
          viewer { zones(filter: {zoneTag: $zone}) {
            httpRequests1dGroups(limit: 31, filter: {date_geq: $since}) {
              uniq { uniques }
            }
          }}
        }"""
        try:
            r = self._request(
                'POST', 'https://api.cloudflare.com/client/v4/graphql',
                headers=self._headers(token),
                json={'query': query, 'variables': {'zone': zid, 'since': since}},
            )
            data = r.json()
            zones = (data.get('data') or {}).get('viewer', {}).get('zones') or []
            if not zones:
                return None
            groups = zones[0].get('httpRequests1dGroups') or []
            return sum((g.get('uniq') or {}).get('uniques', 0) for g in groups)
        except Exception as e:
            logger.info('Analytics haipatikani kwa %s: %s', zid, type(e).__name__)
            return None

    # ── sections ──
    def sections(self):
        token = self.creds.get('api_token', '')
        zid = self.integration.external_id
        try:
            records = self._get(token, f'/zones/{zid}/dns_records',
                                params={'per_page': 100})
        except AdapterError:
            records = []

        return [{
            'key': 'dns',
            'title': 'DNS records',
            'rows': [{
                'type': r.get('type'),
                'name': r.get('name'),
                'value': (r.get('content') or '')[:60],
                'proxied': r.get('proxied', False),
                'ttl': r.get('ttl'),
            } for r in records or []],
        }]
