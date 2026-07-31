"""
Render — web hosting.

Docs: https://api-docs.render.com/reference/introduction
API key inatoka Render → Account Settings → API Keys.
Key moja inaona services zote za account husika.
"""
import logging

from . import base
from .base import AdapterError, BaseAdapter

logger = logging.getLogger(__name__)

API = 'https://api.render.com/v1'

# Render status → canonical
_STATUS = {
    'live': 'online',
    'deactivated': 'suspended',
    'suspended': 'suspended',
    'build_in_progress': 'building',
    'update_in_progress': 'building',
    'build_failed': 'failed',
    'update_failed': 'failed',
    'canceled': 'failed',
    'pre_deploy_in_progress': 'building',
    'pre_deploy_failed': 'failed',
}


class RenderAdapter(BaseAdapter):

    provider = 'render'
    label = 'Render (hosting)'
    client_label = 'Web hosting'

    credential_fields = [
        {'key': 'api_key', 'label': 'API key', 'secret': True,
         'help': 'Render → Account Settings → API Keys'},
    ]

    # ── ndani ──
    @staticmethod
    def _headers(key):
        return {'Authorization': f'Bearer {key}', 'Accept': 'application/json'}

    @classmethod
    def discover(cls, creds):
        key = (creds or {}).get('api_key', '').strip()
        if not key:
            raise AdapterError('API key inahitajika.')

        r = cls._request('GET', f'{API}/services',
                         headers=cls._headers(key), params={'limit': 100})
        out = []
        for row in r.json():
            svc = row.get('service', row)
            details = svc.get('serviceDetails') or {}
            out.append({
                'external_id': svc.get('id', ''),
                'name': svc.get('name', ''),
                'meta': {
                    'type': svc.get('type', ''),
                    'url': details.get('url', ''),
                    'region': details.get('region', ''),
                    'branch': svc.get('branch', ''),
                },
            })
        return out

    def _service(self):
        sid = self.integration.external_id
        r = self._request('GET', f'{API}/services/{sid}',
                          headers=self._headers(self.creds.get('api_key', '')))
        return r.json()

    def _last_deploy(self):
        sid = self.integration.external_id
        r = self._request('GET', f'{API}/services/{sid}/deploys',
                          headers=self._headers(self.creds.get('api_key', '')),
                          params={'limit': 1})
        rows = r.json()
        if not rows:
            return {}
        return rows[0].get('deploy', rows[0])

    # ── summary ──
    def summary(self):
        svc = self._service()
        details = svc.get('serviceDetails') or {}
        deploy = self._last_deploy()

        if svc.get('suspended') == 'suspended':
            status = 'suspended'
        else:
            status = _STATUS.get(deploy.get('status', ''), 'online')

        return {
            base.HOSTING_STATUS: status,
            base.LAST_DEPLOY_AT: deploy.get('finishedAt') or deploy.get('createdAt'),
            base.SERVICE_URL: details.get('url', ''),
            base.SERVER_REGION: details.get('region', ''),
            base.SERVER_PLAN: (details.get('plan')
                               or (details.get('envSpecificDetails') or {}).get('plan')
                               or ''),
        }

    # ── sections ──
    def sections(self):
        sid = self.integration.external_id
        key = self.creds.get('api_key', '')
        try:
            r = self._request('GET', f'{API}/services/{sid}/deploys',
                              headers=self._headers(key), params={'limit': 10})
            deploys = [d.get('deploy', d) for d in r.json()]
        except AdapterError:
            deploys = []

        return [{
            'key': 'deploys',
            'title': 'Deploy history',
            'rows': [{
                'id': d.get('id'),
                'status': d.get('status'),
                'commit': ((d.get('commit') or {}).get('message') or '')[:70],
                'at': d.get('finishedAt') or d.get('createdAt'),
            } for d in deploys],
        }]

    # ── actions (staff pekee) ──
    def actions(self):
        return [
            {'key': 'deploy',       'label': 'Deploy latest',        'danger': False},
            {'key': 'deploy_clear', 'label': 'Clear cache & deploy', 'danger': False},
            {'key': 'restart',      'label': 'Restart',              'danger': False},
            {'key': 'suspend',      'label': 'Suspend',              'danger': True},
            {'key': 'resume',       'label': 'Resume',               'danger': False},
        ]

    def run_action(self, key, **kwargs):
        sid = self.integration.external_id
        h = self._headers(self.creds.get('api_key', ''))

        if key in ('deploy', 'deploy_clear'):
            payload = {'clearCache': 'clear' if key == 'deploy_clear' else 'do_not_clear'}
            r = self._request('POST', f'{API}/services/{sid}/deploys',
                              headers=h, json=payload)
            return {'ok': True, 'job_id': r.json().get('id'), 'message': 'Deploy imeanza.'}

        if key == 'restart':
            self._request('POST', f'{API}/services/{sid}/restart', headers=h)
            return {'ok': True, 'message': 'Restart imeanza.'}

        if key == 'suspend':
            self._request('POST', f'{API}/services/{sid}/suspend', headers=h)
            return {'ok': True, 'message': 'Service imesimamishwa.'}

        if key == 'resume':
            self._request('POST', f'{API}/services/{sid}/resume', headers=h)
            return {'ok': True, 'message': 'Service imerudishwa.'}

        raise AdapterError(f'Kitendo hakijulikani: {key}')

    def deploy_status(self, job_id):
        sid = self.integration.external_id
        r = self._request('GET', f'{API}/services/{sid}/deploys/{job_id}',
                          headers=self._headers(self.creds.get('api_key', '')))
        d = r.json()
        return {'status': d.get('status'),
                'done': d.get('status') in ('live', 'build_failed',
                                            'update_failed', 'canceled')}
