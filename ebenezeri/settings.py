import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
WEBSITE_TYPES_DIR = BASE_DIR / 'apps' / 'website_types'

# ── Security ──────────────────────────────────────────
SECRET_KEY   = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-production')
DEBUG        = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'jamiitek.com,www.jamiitek.com,127.0.0.1,localhost').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
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
        'NAME':     os.getenv('DB_NAME', 'postgres'),
        'USER':     os.getenv('DB_USER', 'postgres.frapnewfadymevdkznrq'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST':     os.getenv('DB_HOST', 'aws-1-eu-north-1.pooler.supabase.com'),
        'PORT':     os.getenv('DB_PORT', '5432'),
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
STATIC_URL        = '/static/'
STATICFILES_DIRS  = [BASE_DIR / 'apps' / 'static']
STATIC_ROOT       = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME', '')}/"
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
    "theme":         "darkly",
    "navbar_fixed":  True,
    "sidebar_fixed": True,
    "footer_fixed":  False,
    "show_ui_builder": True,
}

# ── Uploadcare & Cloudinary ────────────────────────────
UPLOADCARE = {
    'pub_key':    os.getenv('UPLOADCARE_PUB_KEY', '96c9f49ee7fe6afeb1fc'),
    'secret':     os.getenv('UPLOADCARE_SECRET', '7c2ec708937b40ea415c'),
    'use_secure': True,
}

WEASPRINT_BASEURL = BASE_DIR

# ── Email ──────────────────────────────────────────────
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv('EMAIL_HOST_USER', 'info@jamiitek.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL  = f"JamiiTek <{os.getenv('EMAIL_HOST_USER', 'info@jamiitek.com')}>"
PORTAL_BASE_URL     = os.getenv('PORTAL_BASE_URL', 'https://jamiitek.com/portal/')

# ── Chatbot / WhatsApp ─────────────────────────────────
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
SITE_URL       = os.getenv('SITE_URL', 'https://jamiitek.com')

WHATSAPP_MASTER_TOKEN         = os.getenv('WHATSAPP_MASTER_TOKEN', '')
WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', '')
WILLIAM_WHATSAPP              = os.getenv('WILLIAM_WHATSAPP', '')
WILLIAM_PHONE_NUMBER_ID       = os.getenv('WILLIAM_PHONE_NUMBER_ID', '')

CHATBOT_PAYMENT_INFO = {
    'bank':           'NMB Bank',
    'account_number': os.getenv('NMB_ACCOUNT', '21410034200'),
    'account_name':   os.getenv('NMB_NAME', 'WILLIAM CHIPINDI'),
    'branch':         'Dar es Salaam',
}