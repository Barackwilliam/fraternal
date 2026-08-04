"""
Encryption ya credentials zinazokaa database.

FERNET_KEY LAZIMA iwe kwenye environment, si kwenye code wala database.
Tengeneza mara moja:

    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Kisha iweke Render → Environment → FERNET_KEY.

Bila key, mfumo hauvunjiki — credentials tu haziwezi kusomwa, na sync
inarukwa kwa taarifa kwenye log. Hii ni bora kuliko app kushindwa kuanza.
"""
import json
import logging
import os

from django.core.exceptions import ImproperlyConfigured
from django.db import models

logger = logging.getLogger(__name__)

_FERNET = None


def _raw_key():
    """
    Tafuta key mahali pawili:
      1. environment (au .env kupitia load_dotenv)
      2. settings.FERNET_KEY

    Hii inakupa uhuru: unaweza kuiweka .env kwa local na Render
    Environment kwa production, bila kubadilisha code.
    """
    key = (os.getenv('FERNET_KEY') or '').strip()
    if key:
        return key
    try:
        from django.conf import settings
        return (getattr(settings, 'FERNET_KEY', '') or '').strip()
    except Exception:
        return ''


def _fernet():
    """
    Kushindwa HAKUKUMBUKWI. Ukiweka key na kuanzisha upya, inafanya kazi
    mara moja — hakuna cache ya kosa inayokusumbua.
    """
    global _FERNET
    if _FERNET is not None:
        return _FERNET

    key = _raw_key()
    if not key:
        return None

    try:
        from cryptography.fernet import Fernet
        _FERNET = Fernet(key.encode())
    except Exception as e:
        logger.error(
            'FERNET_KEY si sahihi (%s). Inatakiwa iwe base64 ya bytes 32 — '
            'tengeneza kwa: python -c "from cryptography.fernet import Fernet; '
            'print(Fernet.generate_key().decode())"', type(e).__name__)
        return None
    return _FERNET


def diagnose():
    """Ujumbe wa kueleweka kwa command na admin."""
    key = _raw_key()
    if not key:
        return False, ('FERNET_KEY haipatikani. Iweke kwenye .env (local) '
                       'au Render Environment, kisha anzisha upya server.')
    if _fernet() is None:
        return False, (f'FERNET_KEY ipo (herufi {len(key)}) lakini si sahihi. '
                       'Inatakiwa iwe base64 ya bytes 32.')
    return True, 'FERNET_KEY iko sawa.'

def encryption_available() -> bool:
    return _fernet() is not None


class EncryptedJSONField(models.TextField):
    """
    Inahifadhi dict kama JSON iliyo-encrypt kwa Fernet.

    Database ikiibiwa peke yake bila FERNET_KEY, yaliyomo hayana maana.
    """

    description = 'Fernet-encrypted JSON'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', dict)
        kwargs.setdefault('blank', True)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('default', None)
        kwargs.pop('blank', None)
        return name, path, args, kwargs

    # ── kusoma ──
    def from_db_value(self, value, expression, connection):
        return self._decrypt(value)

    def to_python(self, value):
        if isinstance(value, dict):
            return value
        return self._decrypt(value)

    def _decrypt(self, value):
        if value in (None, ''):
            return {}
        if isinstance(value, dict):
            return value

        f = _fernet()
        if f is None:
            return {}
        try:
            return json.loads(f.decrypt(value.encode()).decode())
        except Exception:
            logger.warning('Imeshindwa ku-decrypt credentials — key imebadilika?')
            return {}

    # ── kuandika ──
    def get_prep_value(self, value):
        if value in (None, '', {}):
            return ''
        if not isinstance(value, (dict, list)):
            raise ValueError('EncryptedJSONField inakubali dict au list pekee.')

        f = _fernet()
        if f is None:
            ok, msg = diagnose()
            raise ImproperlyConfigured(msg)
        return f.encrypt(json.dumps(value).encode()).decode()


def mask(value: str, keep: int = 4) -> str:
    """Kwa kuonyesha secret kwenye admin bila kuifichua yote."""
    if not value:
        return ''
    value = str(value)
    if len(value) <= keep * 2:
        return '•' * len(value)
    return f'{value[:keep]}{"•" * 8}{value[-keep:]}'