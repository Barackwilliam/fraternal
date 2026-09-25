"""
IndexNow — kujulisha Bing, Yandex, Seznam, Naver (na ChatGPT search / DuckDuckGo
zinazotumia Bing) PAPO HAPO makala inapochapishwa, badala ya kusubiri crawl.

Hakuna usajili wala env variable inayohitajika: funguo (key) inatokana na
SECRET_KEY, na inaonyeshwa kwenye /indexnow.txt ili injini zithibitishe umiliki.

Google haitumii IndexNow — kwa Google tunategemea sitemap.xml + news-sitemap.xml
(zimeorodheshwa kwenye robots.txt) na Search Console.
"""
import hashlib
import json
import logging
import threading
import urllib.request
from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)

ENDPOINT = 'https://api.indexnow.org/indexnow'


def get_key():
    raw = (getattr(settings, 'INDEXNOW_KEY', '') or '').strip()
    if raw:
        return raw
    return hashlib.sha256((settings.SECRET_KEY + ':indexnow').encode()).hexdigest()[:32]


def key_file(request):
    """/indexnow.txt — injini zinasoma funguo hapa kuthibitisha umiliki."""
    return HttpResponse(get_key(), content_type='text/plain')


def _site_base():
    # Lazima ilingane na canonical za blog (apps/blog_views.CANONICAL_BASE)
    return (getattr(settings, 'CANONICAL_BASE_URL', '') or 'https://jamiitek.com').rstrip('/')


def ping(paths):
    """Tuma URL (au paths kama '/blog/slug/') kwa IndexNow, nyuma (haizuii request)."""
    if getattr(settings, 'DEBUG', False) or not paths:
        return
    base = _site_base()
    urls = [p if p.startswith('http') else base + p for p in paths]
    host = urlparse(base).netloc
    payload = json.dumps({
        'host': host,
        'key': get_key(),
        'keyLocation': f'{base}/indexnow.txt',
        'urlList': urls[:1000],
    }).encode()

    def _send():
        try:
            req = urllib.request.Request(ENDPOINT, data=payload, method='POST',
                                         headers={'Content-Type': 'application/json; charset=utf-8'})
            with urllib.request.urlopen(req, timeout=10) as r:
                logger.info('IndexNow %s → %s', len(urls), r.status)
        except Exception as e:           # 202/200 ni sawa; kosa lolote lisivunje kitu
            logger.warning('IndexNow ping failed: %s', e)

    threading.Thread(target=_send, daemon=True).start()
