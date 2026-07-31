"""
Kiungo kimoja kwa providers wote.

Kila adapter inarudisha summary yenye MAJINA YALEYALE (canonical keys)
bila kujali provider. Hii ndiyo inayofanya UI iwe moja na `resolve()`
isijali data inatoka wapi.
"""
import logging

logger = logging.getLogger(__name__)

TIMEOUT = 15


# ── Canonical keys ────────────────────────────────────────────────
# Kila adapter inatoa baadhi ya hizi. Hakuna adapter inayotoa zote.

HOSTING_STATUS   = 'hosting_status'      # online | building | failed | suspended
LAST_DEPLOY_AT   = 'last_deploy_at'
SERVICE_URL      = 'service_url'
SERVER_REGION    = 'server_region'
SERVER_PLAN      = 'server_plan'

DB_SIZE_BYTES    = 'db_size_bytes'
DB_CONNECTIONS   = 'db_connections'
LAST_BACKUP      = 'last_backup'

MEDIA_FILES      = 'media_files'
MEDIA_BYTES      = 'media_bytes'

SSL_EXPIRY       = 'ssl_expiry_date'
SSL_ISSUER       = 'ssl_issuer'
MONTHLY_VISITS   = 'monthly_visits'
DNS_OK           = 'dns_ok'

DOMAIN_EXPIRY    = 'domain_expiry'
DOMAIN_REGISTRAR = 'domain_registrar'
DOMAIN_AUTORENEW = 'domain_auto_renew'


class AdapterError(Exception):
    """Kosa lolote la provider. Halipaswi kuvuja kwa mteja."""


class BaseAdapter:
    """
    Kila provider inarithi hii.

    provider  — ufunguo kwenye ADAPTERS registry
    label     — jina la ndani (staff wanaona)
    client_label — jina la mteja (hakuna jina la provider hapa)
    """

    provider = ''
    label = ''
    client_label = ''
    credential_fields = []   # [{'key','label','secret','help'}]

    def __init__(self, integration):
        self.integration = integration
        self.creds = integration.credentials or {}

    # ── lazima ziandikwe ──
    def summary(self) -> dict:
        """Rudisha dict yenye canonical keys. Hakuna kitu kingine."""
        raise NotImplementedError

    # ── za hiari ──
    def sections(self) -> list:
        return []

    def actions(self) -> list:
        return []

    def run_action(self, key, **kwargs) -> dict:
        raise AdapterError(f'Kitendo hakijulikani: {key}')

    # ── discovery (kabla ya kuhifadhi) ──
    @classmethod
    def validate(cls, creds) -> tuple:
        """(ok, ujumbe)"""
        try:
            cls.discover(creds)
            return True, 'Imeunganishwa.'
        except AdapterError as e:
            return False, str(e)
        except Exception as e:
            return False, f'Imeshindikana: {type(e).__name__}'

    @classmethod
    def discover(cls, creds) -> list:
        """[{'external_id','name','meta'}] — resources zilizopo."""
        raise NotImplementedError

    # ── msaada ──
    @staticmethod
    def _request(method, url, **kw):
        import requests
        kw.setdefault('timeout', TIMEOUT)
        try:
            r = requests.request(method, url, **kw)
        except Exception as e:
            raise AdapterError(f'Mtandao umeshindikana: {type(e).__name__}')

        if r.status_code in (401, 403):
            raise AdapterError('Credentials hazikubaliki.')
        if r.status_code == 404:
            raise AdapterError('Haipatikani.')
        if r.status_code == 429:
            raise AdapterError('Rate limit imefikiwa — jaribu baadaye.')
        if r.status_code >= 400:
            raise AdapterError(f'Provider amerudisha {r.status_code}.')
        return r
