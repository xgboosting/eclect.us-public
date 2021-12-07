const cacheName = 'eclectus-v1';
const staticAssets = [
  './',
  './static',
  './static/symbols.js',
  './static/autocomplete.min.js',
  './static/bootstrap/js/bootstrap.min.js',
  './static/bootstrap/css/bootstrap-grid.min.css',
  './static/autocomplete.css',
  './static/bootstrap/css/bootstrap.min.css',
  './index.html',
  './index.js',
  './empty-filing.js',
  './filing-loading.js',
  './filing-static.js',
  './filings.js',
  './nav-bar.js',
  './recents.js',
  './search.js'
];

self.addEventListener('install', async e => {
  const cache = await caches.open(cacheName);
  await cache.addAll(staticAssets);
  return self.skipWaiting();
});

self.addEventListener('activate', e => {
  self.clients.claim();
});

self.addEventListener('fetch', async e => {
  const req = e.request;
  const url = new URL(req.url);

  if (url.origin === location.origin) {
    e.respondWith(cacheFirst(req));
  } else {
    e.respondWith(networkAndCache(req));
  }
});

async function cacheFirst(req) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  return cached || fetch(req);
}

async function networkAndCache(req) {
  const cache = await caches.open(cacheName);
  try {
    const fresh = await fetch(req);
    await cache.put(req, fresh.clone());
    return fresh;
  } catch (e) {
    const cached = await cache.match(req);
    return cached;
  }
}
