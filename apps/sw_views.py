# apps/sw_views.py
"""
Serves /sw.js straight from Python.

Earlier this was a TemplateView, which meant the file had to sit in the
templates directory and pass through the Django template engine — two ways
to get a 500 on a file whose only job is to keep the site working when
things go wrong. A plain HttpResponse has neither problem.

A service worker can only control paths at or below its own URL, so this
must be served from the site root (/sw.js), not from /static/.
"""

from django.http import HttpResponse
from django.views.decorators.cache import cache_control

# Bump the version whenever offline.html changes, or browsers keep the old copy.
SW_JS = """/* JamiiTek service worker - offline fallback only. */
const CACHE = 'jamiitek-offline-v1';
const OFFLINE = '/offline.html';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.add(new Request(OFFLINE, { cache: 'reload' })))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Page loads only. Never cache HTML, API responses, invoices or receipts:
  // showing a client a stale balance would be worse than showing them nothing.
  if (req.mode !== 'navigate' || req.method !== 'GET') return;

  event.respondWith(
    fetch(req).catch(() => caches.match(OFFLINE, { ignoreSearch: true }))
  );
});
"""


@cache_control(max_age=0, no_cache=True, must_revalidate=True)
def service_worker(request):
    return HttpResponse(SW_JS, content_type='application/javascript')