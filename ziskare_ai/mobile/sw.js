// Ziskare AI Mobile PWA Service Worker
const CACHE_NAME = 'ziskare-mobile-v1';
const ASSETS_TO_CACHE = [
  '/mobile',
  '/mobile/index.html',
  '/mobile/manifest.json'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k !== CACHE_NAME ? caches.delete(k) : null)))
    )
  );
});

self.addEventListener('fetch', (e) => {
  // Only cache static web UI files; bypass cache for API calls
  if (e.request.url.includes('/api/') || e.request.method !== 'GET') {
    return;
  }
  e.respondWith(
    caches.match(e.request).then((res) => res || fetch(e.request))
  );
});
