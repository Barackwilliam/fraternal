"""
Offline test settings — sqlite, locmem cache/email, DEBUG.
Kwa uhakiki wa haraka bila Postgres/Redis/env halisi.
    python manage.py check --settings=jamiitek.test_settings
"""
import os
os.environ.setdefault('SECRET_KEY', 'test-only-key')
os.environ.setdefault('DEBUG', 'True')

from jamiitek.settings import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*', 'testserver', 'localhost', '127.0.0.1']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
