/* JamiiTek service worker — offline fallback only.
 *
 * Deliberately narrow: it caches one page and answers failed navigations
 * with it. It does not cache HTML pages or API responses, so a client can
 * never be shown a stale invoice, receipt or balance.
 *
 * Bump CACHE when offline.html changes.
 */
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

  // Only page loads. Everything else is left to the browser.
  if (req.mode !== 'navigate' || req.method !== 'GET') return;

  event.respondWith(
    fetch(req).catch(() => caches.match(OFFLINE, { ignoreSearch: true }))
  );
});
