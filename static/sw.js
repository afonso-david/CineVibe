// Service Worker para cachear a logo e evitar flickering
const CACHE_NAME = 'cinevibe-logo-v1';
const LOGO_URL = '/static/imgs/Logo/logo8 sem fundo.png';

// Instalar e cachear a logo imediatamente
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.add(LOGO_URL);
        })
    );
    self.skipWaiting();
});

// Ativar e limpar caches antigos
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Interceptar requisições da logo e servir do cache
self.addEventListener('fetch', (event) => {
    if (event.request.url.includes('logo8 sem fundo.png')) {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request).then((fetchResponse) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, fetchResponse.clone());
                        return fetchResponse;
                    });
                });
            })
        );
    }
});
