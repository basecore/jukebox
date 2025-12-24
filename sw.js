const CACHE_NAME = 'jukebox-v60-scrollfix'; // <--- Version 60
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './assets/limit.mp3',
  './assets/img/hintergrund.jpg',
  './assets/icons/icon.png',
  './assets/icons/icon512_maskable.png',
  './assets/icons/icon512_rounded.png'
];

// ... (Rest der Datei bleibt gleich) ...
// 1. Install ...
self.addEventListener('install', (e) => {
  console.log('[Service Worker] Installiere & Cache Dateien...');
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

// 2. Fetch ...
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      return cachedResponse || fetch(e.request);
    })
  );
});

// 3. Activate ...
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(keyList.map((key) => {
        if (key !== CACHE_NAME) {
          console.log('[Service Worker] Entferne alten Cache:', key);
          return caches.delete(key);
        }
      }));
    })
  );
  return self.clients.claim();
});
