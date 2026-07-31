"""
Supabase — database.

Vyanzo viwili:

1. Management API (https://api.supabase.com/v1) — status, region, backups.
   PAT inatoka Supabase → Account → Access Tokens.
   Rate limit: 120 req/min kwa user, cumulative kwa PATs zote.

2. psycopg moja kwa moja — ukubwa wa database na connections.
   Hii ni ya haraka, sahihi, na haigongi rate limit. Inatumia
   DATABASE_URL unayoimiliki tayari.

Credentials:
    {"pat": "sbp_...", "db_url": "postgresql://..."}

Zote mbili ni za hiari. Ukiweka `db_url` peke yake, unapata ukubwa na
connections bila PAT. Ukiweka `pat` peke yake, unapata status na backups.
"""
import logging

from . import base
from .base import AdapterError, BaseAdapter

logger = logging.getLogger(__name__)

API = 'https://api.supabase.com/v1'


class SupabaseAdapter(BaseAdapter):

    provider = 'supabase'
    label = 'Supabase (database)'
    client_label = 'Database'

    credential_fields = [
        {'key': 'pat', 'label': 'Personal access token', 'secret': True,
         'help': 'Supabase → Account → Access Tokens. Ya hiari.'},
        {'key': 'db_url', 'label': 'Database URL', 'secret': True,
         'help': 'postgresql://... — kwa ukubwa na connections. Ya hiari.'},
    ]

    @staticmethod
    def _headers(pat):
        return {'Authorization': f'Bearer {pat}', 'Accept': 'application/json'}

    @classmethod
    def discover(cls, creds):
        creds = creds or {}
        pat = (creds.get('pat') or '').strip()

        if not pat:
            # db_url peke yake — hakuna orodha, ni project moja
            if creds.get('db_url'):
                return [{'external_id': 'direct', 'name': 'Database (direct)',
                         'meta': {}}]
            raise AdapterError('Weka PAT au database URL.')

        r = cls._request('GET', f'{API}/projects', headers=cls._headers(pat))
        return [{
            'external_id': p.get('id', ''),
            'name': p.get('name', ''),
            'meta': {'region': p.get('region', ''),
                     'status': p.get('status', ''),
                     'created_at': p.get('created_at', '')},
        } for p in r.json() or []]

    # ── Management API ──
    def _project(self):
        pat = self.creds.get('pat', '')
        ref = self.integration.external_id
        if not pat or ref == 'direct':
            return {}
        try:
            r = self._request('GET', f'{API}/projects/{ref}',
                              headers=self._headers(pat))
            return r.json() or {}
        except AdapterError as e:
            logger.info('Supabase project %s: %s', ref, e)
            return {}

    def _last_backup(self):
        pat = self.creds.get('pat', '')
        ref = self.integration.external_id
        if not pat or ref == 'direct':
            return None
        try:
            r = self._request('GET', f'{API}/projects/{ref}/database/backups',
                              headers=self._headers(pat))
            data = r.json() or {}
            backups = data.get('backups') or []
            if not backups:
                return None
            latest = max(
                (b.get('inserted_at') or '') for b in backups if b.get('inserted_at'))
            return latest[:10] or None
        except AdapterError as e:
            logger.info('Supabase backups %s: %s', ref, e)
            return None

    # ── psycopg ──
    def _db_metrics(self):
        url = (self.creds.get('db_url') or '').strip()
        if not url:
            return {}

        try:
            import psycopg2
        except ImportError:
            logger.warning('psycopg2 haipo — metrics za database zimerukwa.')
            return {}

        conn = None
        try:
            conn = psycopg2.connect(url, connect_timeout=10)
            conn.set_session(readonly=True, autocommit=True)
            with conn.cursor() as cur:
                cur.execute('SELECT pg_database_size(current_database())')
                size = cur.fetchone()[0]
                cur.execute(
                    'SELECT count(*) FROM pg_stat_activity '
                    'WHERE datname = current_database()')
                conns = cur.fetchone()[0]
            return {base.DB_SIZE_BYTES: int(size),
                    base.DB_CONNECTIONS: int(conns)}
        except Exception as e:
            logger.info('Database metrics zimeshindikana: %s', type(e).__name__)
            return {}
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    # ── summary ──
    def summary(self):
        out = {}

        project = self._project()
        if project:
            status = (project.get('status') or '').upper()
            out['db_status'] = 'online' if status in (
                'ACTIVE_HEALTHY', 'ACTIVE') else status.lower()
            if project.get('region'):
                out['db_region'] = project['region']

        backup = self._last_backup()
        if backup:
            out[base.LAST_BACKUP] = backup

        out.update(self._db_metrics())

        if not out:
            raise AdapterError('Hakuna data — angalia PAT au database URL.')
        return out

    def sections(self):
        p = self._project()
        if not p:
            return []
        return [{
            'key': 'project',
            'title': 'Project',
            'rows': [{
                'ref': p.get('id', ''),
                'name': p.get('name', ''),
                'region': p.get('region', ''),
                'status': p.get('status', ''),
                'created': (p.get('created_at') or '')[:10],
            }],
        }]
