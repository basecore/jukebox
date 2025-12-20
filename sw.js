const CACHE_NAME = 'jukebox-v33-offline';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './manifest.json',
  './assets/img/hintergrund.jpg',
  './assets/icons/icon.png',
  './assets/icons/icon512_maskable.png',
  './assets/icons/icon512_rounded.png'
];

// 1. Install: Dateien in den Cache laden
self.addEventListener('install', (e) => {
  console.log('[Service Worker] Installiere & Cache Dateien...');
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

// 2. Fetch: Erst Cache prüfen, dann Netzwerk
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cachedResponse) => {
      // Wenn im Cache: Sofort zurückgeben
      if (cachedResponse) {
        return cachedResponse;
      }
      // Wenn nicht: Aus dem Netz holen
      return fetch(e.request);
    })
  );
});

// 3. Activate: Alte Caches löschen (Wichtig bei Updates)
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
  // Sofort die Kontrolle übernehmen
  return self.clients.claim();
});
