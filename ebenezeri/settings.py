import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
WEBSITE_TYPES_DIR = BASE_DIR / 'apps' / 'website_types'

# ── Security ──────────────────────────────────────────
SECRET_KEY    = os.getenv('SECRET_KEY',    'django-insecure-@&r$)$xpb)f6pm=_73pupatv2#n-%0%d=(cky=kab5ww6&*tzs')
DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'jamiitek.com,www.jamiitek.com,jamiitek.onrender.com,127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sitemaps',   
    'django.contrib.sites',     
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps',
    'apps.chatbot',
    'uploadcare',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'ebenezeri.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'apps' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ebenezeri.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.getenv('DB_NAME',     'postgres'),
        'USER':     os.getenv('DB_USER',     'postgres.frapnewfadymevdkznrq'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'NyumbaChap'),
        'HOST':     os.getenv('DB_HOST',     'aws-1-eu-north-1.pooler.supabase.com'),
        'PORT':     os.getenv('DB_PORT',     '5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': 'require',
            'connect_timeout': 10,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalization ───────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Africa/Dar_es_Salaam'
USE_I18N      = True
USE_TZ        = True

# ── Static & Media ─────────────────────────────────────
STATIC_URL          = '/static/'
STATICFILES_DIRS    = [BASE_DIR / 'apps' / 'static']
STATIC_ROOT         = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME', 'drc3xiipg')}/"
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Jazzmin ────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title":   "JamiiTek Admin",
    "site_header":  "JamiiTek Dashboard",
    "site_brand":   "JamiiTek",
    "welcome_sign": "Welcome to JamiiTek Dashboard",
    "copyright":    "JamiiTek © 2025",
    "search_model": "auth.User",
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "auth.User"},
        {"app":   "JamiiTek System"},
    ],
}

JAZZMIN_UI_TWEAKS = {
    "theme":           "darkly",
    "navbar_fixed":    True,
    "sidebar_fixed":   True,
    "footer_fixed":    False,
    "show_ui_builder": True,
}

# ── Uploadcare & Cloudinary ────────────────────────────
UPLOADCARE = {
    'pub_key':    os.getenv('UPLOADCARE_PUB_KEY', '4c3ba9de492e0e0eaddc'),
    'secret':     os.getenv('UPLOADCARE_SECRET',  '28410d13b3cb1098451e'),
    'use_secure': True,
}

WEASPRINT_BASEURL = BASE_DIR
 
# ── Email ──────────────────────────────────────────────
_email_user = os.getenv('EMAIL_HOST_USER', 'info@jamiitek.com')
_email_pass = os.getenv('EMAIL_HOST_PASSWORD', 'tbgh swtl zple dhiv')
 
if _email_user and _email_pass:
    EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST          = 'smtp.gmail.com'
    EMAIL_PORT          = 587
    EMAIL_USE_TLS       = True
    EMAIL_HOST_USER     = _email_user
    EMAIL_HOST_PASSWORD = _email_pass
    DEFAULT_FROM_EMAIL  = f"JamiiTek <{_email_user}>"
else:
    # Fallback: log emails to console instead of crashing
    EMAIL_BACKEND   = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST_USER = 'info@jamiitek.com'
    DEFAULT_FROM_EMAIL = 'JamiiTek <info@jamiitek.com>'
 
PORTAL_BASE_URL = os.getenv('PORTAL_BASE_URL', 'https://jamiitek.com/portal/')
 
# ── Cloudinary ─────────────────────────────────────────
CLOUDINARY_API_KEY    = os.getenv('CLOUDINARY_API_KEY',    '321181265585861')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', 'KA2L_qJUCyBBZFcyeQDGzH1kfUo')

# ── Chatbot / WhatsApp ─────────────────────────────────
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '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')
SITE_URL     = os.getenv('SITE_URL',     'https://jamiitek.com')

WHATSAPP_MASTER_TOKEN         = os.getenv('WHATSAPP_MASTER_TOKEN',         'EAARTZCRXCM9sBRCw5ratThW8zsfNp3h8TdFqoKmh6crYm7a4OZBe0u1y5jZBHu3LkEARBFCZAZCVwF6NsqKWsi1n460VWl1IjOO1UsZC3hmjmGMfBkeHUG7ZA5ie1iVvZB9m0hQy8OLpmiMKn8JMgbhlJM7hFNwBHDvXmlC3uatpVADEZA0wLmWbzyUZBwtFTCdhHnj6je4y1gRFk5mdZARtgB5uuE7lQ7juhUAQSlaEt8m4SZBZAkQkmj6KclZAHoiKHFaKPZCfHptOy4J9ZCvmfErOFLCS')
WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'jamiitek_wh_2025')
WILLIAM_WHATSAPP              = os.getenv('WILLIAM_WHATSAPP',              '15551681112')
WILLIAM_PHONE_NUMBER_ID       = os.getenv('WILLIAM_PHONE_NUMBER_ID',       '1001845693020330')

CHATBOT_PAYMENT_INFO = {
    'bank':           'NMB Bank',
    'account_number': os.getenv('NMB_ACCOUNT', '21410034200'),
    'account_name':   os.getenv('NMB_NAME',    'WILLIAM CHIPINDI'),
    'branch':         'Dar es Salaam',
}