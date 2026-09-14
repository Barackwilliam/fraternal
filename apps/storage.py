"""
Supabase Storage — mahali image zote za JamiiTek zinakaa.

KWA NINI KUPITIA DJANGO NA SI MOJA KWA MOJA

Browser ingeweza kupakia moja kwa moja Supabase kwa signed URL, na
ingekuwa haraka zaidi. Lakini ingemaanisha funguo ikae kwenye JS, au
tuongeze hatua ya kuomba signed URL kila upload.

Kwa image za biashara ndogo (logo, picha za huduma, portfolio), file
inapita Django mara moja tu wakati wa kupakia. Baada ya hapo mteja
anasoma moja kwa moja kutoka CDN ya Supabase. Server yako haiguswi
tena.

Funguo ya `service_role` INABAKI SERVER. Kamwe isipelekwe browser —
inaweza kusoma na kufuta kila kitu kwenye storage yako.

MUUNDO WA MAJINA

    <folda>/<mwaka>/<mwezi>/<uuid>.<ext>

Mfano: services/2026/09/3f8a2b1c.jpg

UUID inazuia file mbili zenye jina moja kugongana, na inazuia mtu
kukisia URL za file za wengine. Mwaka/mwezi inarahisisha kusafisha
baadaye.
"""
import logging
import mimetypes
import os
import re
import uuid
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger('jamiitek.storage')

TIMEOUT = 30

# Aina zinazokubalika. Orodha ni fupi kwa makusudi — SVG haimo kwa
# sababu inaweza kubeba JavaScript, na image ya mteja inaonyeshwa
# kwenye tovuti ya mteja mwingine.
ALLOWED = {
    'image/jpeg': 'jpg',
    'image/png':  'png',
    'image/webp': 'webp',
    'image/gif':  'gif',
    'application/pdf': 'pdf',
}

MAX_BYTES = 10 * 1024 * 1024   # 10MB


def _base():
    return (getattr(settings, 'SUPABASE_URL', '') or '').rstrip('/')


def _key():
    return getattr(settings, 'SUPABASE_SERVICE_KEY', '') or ''


def _bucket():
    return getattr(settings, 'SUPABASE_BUCKET', 'media') or 'media'


def is_configured():
    return bool(_base() and _key())


def public_url(path):
    """URL ya kusoma. Bucket lazima iwe public."""
    if not path:
        return ''
    if path.startswith('http'):
        return path          # tayari ni URL kamili
    return f"{_base()}/storage/v1/object/public/{_bucket()}/{path.lstrip('/')}"


def _safe_ext(filename, content_type):
    """Kiendelezi kinachoaminika — kutoka content type, si jina la file."""
    ext = ALLOWED.get((content_type or '').lower().split(';')[0].strip())
    if ext:
        return ext
    guessed = mimetypes.guess_type(filename or '')[0]
    return ALLOWED.get(guessed or '', '')


def _safe_folder(folder):
    """
    Slash INARUHUSIWA — Builder inatumia `sites/<id>` ili kila tovuti
    iwe na folda yake. Lakini kila sehemu inasafishwa peke yake, kwa
    hiyo '..' haiwezi kupita na kutoka nje ya bucket.
    """
    parts = []
    for seg in (folder or 'media').lower().split('/'):
        seg = re.sub(r'[^a-z0-9_-]', '', seg)[:40]
        if seg and seg not in ('.', '..'):
            parts.append(seg)
        if len(parts) >= 3:          # kina cha kutosha; kinazuia kuzama
            break
    return '/'.join(parts) or 'media'


def build_path(folder, filename, content_type):
    ext = _safe_ext(filename, content_type)
    if not ext:
        return ''
    now = datetime.utcnow()
    return f"{_safe_folder(folder)}/{now:%Y/%m}/{uuid.uuid4().hex[:16]}.{ext}"


# ══════════════════════════════════════════════════════════════
#  KUPAKIA
# ══════════════════════════════════════════════════════════════

def upload(file_obj, folder='media', filename=None, content_type=None):
    """
    Inapakia file kwenda Supabase.

    Inarudisha dict: {'success': bool, 'url': str, 'path': str, 'error': str}
    Kamwe haitupi exception — inayeyusha kila kosa kuwa jibu.
    """
    if not is_configured():
        return {'success': False, 'error': 'SUPABASE_URL au SUPABASE_SERVICE_KEY haijawekwa'}

    filename = filename or getattr(file_obj, 'name', '') or 'file'
    content_type = content_type or getattr(file_obj, 'content_type', '') or ''

    size = getattr(file_obj, 'size', None)
    if size is not None and size > MAX_BYTES:
        return {'success': False,
                'error': f'File ni kubwa mno ({size // 1024 // 1024}MB). Kikomo ni 10MB.'}

    path = build_path(folder, filename, content_type)
    if not path:
        return {'success': False,
                'error': 'Aina ya file hairuhusiwi. Tumia JPG, PNG, WEBP, GIF au PDF.'}

    try:
        file_obj.seek(0)
    except Exception:
        pass

    url = f"{_base()}/storage/v1/object/{_bucket()}/{path}"
    try:
        resp = requests.post(
            url,
            headers={
                'Authorization': f'Bearer {_key()}',
                'Content-Type': content_type or 'application/octet-stream',
                # Bucket huundwa mara ya kwanza ikiwa haipo? Hapana —
                # Supabase inadai bucket iwepo. Angalia README.
                'x-upsert': 'false',
            },
            data=file_obj.read(),
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        logger.exception('upload imeshindwa')
        return {'success': False, 'error': str(e)}

    if resp.status_code not in (200, 201):
        detail = resp.text[:200]
        logger.error('Supabase %s: %s', resp.status_code, detail)
        if resp.status_code == 404:
            detail = f"Bucket '{_bucket()}' haipo kwenye Supabase."
        elif resp.status_code in (401, 403):
            detail = 'SUPABASE_SERVICE_KEY si sahihi au haina ruhusa.'
        return {'success': False, 'error': detail}

    return {'success': True, 'path': path, 'url': public_url(path), 'error': ''}


def delete(path):
    """Futa file. Inarudisha True/False; kamwe haitupi exception."""
    if not is_configured() or not path:
        return False
    # Ikiwa tumepewa URL kamili, toa path yake
    marker = f"/public/{_bucket()}/"
    if marker in path:
        path = path.split(marker, 1)[1]
    try:
        resp = requests.delete(
            f"{_base()}/storage/v1/object/{_bucket()}/{path.lstrip('/')}",
            headers={'Authorization': f'Bearer {_key()}'},
            timeout=TIMEOUT,
        )
        return resp.status_code in (200, 204)
    except requests.RequestException:
        logger.exception('delete imeshindwa')
        return False


def health():
    """Je, bucket ipo na funguo inafanya kazi?"""
    if not is_configured():
        return {'success': False, 'error': 'haijasanidiwa'}
    try:
        resp = requests.post(
            f"{_base()}/storage/v1/object/list/{_bucket()}",
            headers={'Authorization': f'Bearer {_key()}',
                     'Content-Type': 'application/json'},
            json={'limit': 1, 'prefix': ''},
            timeout=15,
        )
        if resp.status_code == 200:
            return {'success': True, 'bucket': _bucket()}
        if resp.status_code == 404:
            return {'success': False, 'error': f"Bucket '{_bucket()}' haipo"}
        return {'success': False, 'error': f'HTTP {resp.status_code}: {resp.text[:150]}'}
    except requests.RequestException as e:
        return {'success': False, 'error': str(e)}
