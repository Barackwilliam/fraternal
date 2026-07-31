"""
RDAP — tarehe ya kuisha kwa domain, bila kujali registrar.

Hii ni bure kabisa: hakuna API key, hakuna IP whitelist, hakuna kikomo
cha account. Inafanya kazi kwa Namecheap, GoDaddy, Cloudflare — yeyote.

KIKOMO: ccTLD nyingi hazina RDAP. `.co.tz` (tzNIC) karibu hakika haina.
Kwa hizo, summary inarudi tupu na `resolve()` inarudi kwenye tarehe ya
mkono kwenye DomainRecord.expiry_date. Hiyo ndiyo tabia sahihi.
"""
import logging

from . import base
from .base import AdapterError, BaseAdapter

logger = logging.getLogger(__name__)

RDAP = 'https://rdap.org/domain/'


class DomainAdapter(BaseAdapter):

    provider = 'rdap'
    label = 'Domain registry (RDAP)'
    client_label = 'Domain'

    credential_fields = [
        {'key': 'domain', 'label': 'Domain name', 'secret': False,
         'help': 'mfano: mudandaza.co.tz — hakuna key inayohitajika'},
    ]

    @classmethod
    def _lookup(cls, domain):
        domain = (domain or '').strip().lower().lstrip('.')
        if not domain or '.' not in domain:
            raise AdapterError('Domain si sahihi.')

        r = cls._request('GET', f'{RDAP}{domain}',
                         headers={'Accept': 'application/rdap+json'})
        return r.json()

    @classmethod
    def discover(cls, creds):
        domain = (creds or {}).get('domain', '')
        data = cls._lookup(domain)
        return [{
            'external_id': domain.strip().lower(),
            'name': data.get('ldhName', domain),
            'meta': {'status': data.get('status', [])},
        }]

    def summary(self):
        domain = self.creds.get('domain') or self.integration.external_id
        try:
            data = self._lookup(domain)
        except AdapterError as e:
            # ccTLD isiyo na RDAP — si kosa, ni ukweli tu
            logger.info('RDAP haipatikani kwa %s: %s', domain, e)
            return {}

        events = {e.get('eventAction'): e.get('eventDate')
                  for e in data.get('events') or []}

        registrar = ''
        for ent in data.get('entities') or []:
            if 'registrar' not in (ent.get('roles') or []):
                continue
            for item in (ent.get('vcardArray') or [None, []])[1]:
                if item and item[0] == 'fn':
                    registrar = item[3]
                    break

        statuses = [s.lower() for s in data.get('status') or []]
        auto_renew = 'auto renew period' in statuses

        out = {}
        if events.get('expiration'):
            out[base.DOMAIN_EXPIRY] = events['expiration'][:10]
        if registrar:
            out[base.DOMAIN_REGISTRAR] = registrar
        out[base.DOMAIN_AUTORENEW] = auto_renew
        return out
