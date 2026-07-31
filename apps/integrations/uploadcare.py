"""
Uploadcare — media (picha na video).

Inatumia SIGNED requests (HMAC-SHA1), si `Uploadcare.Simple`. Tofauti:
kwa Simple, secret key inasafiri kwenye kila request. Kwa signed,
inayosafiri ni signature tu — secret haitoki kwenye server yako.

Keys ni za PROJECT, si za account. Project tano = jozi tano.
Uploadcare → Dashboard → project → API keys.

Credentials:
    {"public_key": "...", "secret_key": "..."}
"""
import hashlib
import hmac
import logging
from email.utils import formatdate

from . import base
from .base import AdapterError, BaseAdapter

logger = logging.getLogger(__name__)

API = 'https://api.uploadcare.com'
VERSION = 'application/vnd.uploadcare-v0.7+json'


class UploadcareAdapter(BaseAdapter):

    provider = 'uploadcare'
    label = 'Uploadcare (media)'
    client_label = 'Media storage'

    credential_fields = [
        {'key': 'public_key', 'label': 'Public key', 'secret': False,
         'help': 'Uploadcare → project → API keys'},
        {'key': 'secret_key', 'label': 'Secret key', 'secret': True,
         'help': 'Haitosafiri kwenye network — signature pekee ndiyo inayotumwa.'},
    ]

    # ── signing ──
    @staticmethod
    def _sign(secret, verb, uri, body=b'', content_type='application/json'):
        """
        signature = HMAC-SHA1(secret,
            verb \n md5(body) \n content_type \n date \n uri)
        """
        date = formatdate(usegmt=True)
        body_md5 = hashlib.md5(body).hexdigest()
        message = '\n'.join([verb, body_md5, content_type, date, uri])
        sig = hmac.new(secret.encode(), message.encode(), hashlib.sha1).hexdigest()
        return sig, date

    @classmethod
    def _call(cls, creds, uri, verb='GET'):
        public = (creds or {}).get('public_key', '').strip()
        secret = (creds or {}).get('secret_key', '').strip()
        if not public or not secret:
            raise AdapterError('Public key na secret key zinahitajika.')

        sig, date = cls._sign(secret, verb, uri)
        headers = {
            'Accept': VERSION,
            'Date': date,
            'Content-Type': 'application/json',
            'Authorization': f'Uploadcare {public}:{sig}',
        }
        r = cls._request(verb, f'{API}{uri}', headers=headers)
        return r.json()

    @classmethod
    def discover(cls, creds):
        data = cls._call(creds, '/project/')
        pub = (creds or {}).get('public_key', '').strip()
        return [{
            'external_id': pub,
            'name': data.get('name') or pub,
            'meta': {'collaborators': len(data.get('collaborators') or [])},
        }]

    # ── summary ──
    def summary(self):
        out = {}

        try:
            project = self._call(self.creds, '/project/')
            if project.get('name'):
                out['media_project'] = project['name']
        except AdapterError as e:
            raise AdapterError(f'Uploadcare: {e}')

        # Idadi ya files — `total` inarudi kwenye response ya /files/
        try:
            files = self._call(self.creds, '/files/?limit=1&stored=true')
            total = files.get('total')
            if total is not None:
                out[base.MEDIA_FILES] = int(total)
        except AdapterError as e:
            logger.info('Uploadcare files: %s', e)

        # Ukubwa — Uploadcare hairudishi jumla moja kwa moja.
        # Tunahesabu kutoka ukurasa wa kwanza kama sampuli tu ikiwa files
        # ni chache; vinginevyo tunaacha, ni ghali mno kuhesabu zote.
        total = out.get(base.MEDIA_FILES) or 0
        if 0 < total <= 1000:
            try:
                size = self._sum_sizes()
                if size is not None:
                    out[base.MEDIA_BYTES] = size
            except AdapterError as e:
                logger.info('Uploadcare sizes: %s', e)

        return out

    def _sum_sizes(self):
        total, uri, pages = 0, '/files/?limit=500&stored=true', 0
        while uri and pages < 4:
            data = self._call(self.creds, uri)
            for f in data.get('results') or []:
                total += int(f.get('size') or 0)
            nxt = data.get('next')
            if not nxt:
                break
            uri = nxt.replace(API, '')
            pages += 1
        return total

    def sections(self):
        try:
            data = self._call(self.creds, '/files/?limit=12&stored=true')
        except AdapterError:
            return []

        return [{
            'key': 'files',
            'title': 'Recent uploads',
            'rows': [{
                'uuid': f.get('uuid'),
                'name': f.get('original_filename', ''),
                'size': f.get('size', 0),
                'url': f.get('original_file_url', ''),
                'at': (f.get('datetime_uploaded') or '')[:10],
            } for f in data.get('results') or []],
        }]
