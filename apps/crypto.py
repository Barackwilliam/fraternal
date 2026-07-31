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
_CHECKED = False


def _fernet():
    global _FERNET, _CHECKED
    if _CHECKED:
        return _FERNET
    _CHECKED = True

    key = os.getenv('FERNET_KEY', '').strip()
    if not key:
        logger.error('FERNET_KEY haijawekwa — credentials hazitasomeka.')
        return None
    try:
        from cryptography.fernet import Fernet
        _FERNET = Fernet(key.encode())
    except Exception as e:
        logger.error('FERNET_KEY si sahihi: %s', type(e).__name__)
        _FERNET = None
    return _FERNET


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
            raise ImproperlyConfigured(
                'FERNET_KEY haijawekwa — huwezi kuhifadhi credentials.'
            )
        return f.encrypt(json.dumps(value).encode()).decode()


def mask(value: str, keep: int = 4) -> str:
    """Kwa kuonyesha secret kwenye admin bila kuifichua yote."""
    if not value:
        return ''
    value = str(value)
    if len(value) <= keep * 2:
        return '•' * len(value)
    return f'{value[:keep]}{"•" * 8}{value[-keep:]}'
