const CACHE_NAME = 'dictee-vocale-v1';
const urlsToCache = [
    '/dictee-vocale/',
    '/dictee-vocale/index.html',
    '/dictee-vocale/landing.html',
    '/dictee-vocale/manifest.json',
    'https://cdn.tailwindcss.com',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Installation du Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Cache ouvert');
                return cache.addAll(urlsToCache);
            })
            .catch((err) => {
                console.log('Erreur de cache:', err);
            })
    );
});

// Activation et nettoyage des anciens caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Suppression ancien cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Stratégie de fetch : Network first, fallback to cache
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Si réponse valide, on la met en cache
                if (response && response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseClone);
                        });
                }
                return response;
            })
            .catch(() => {
                // Si pas de réseau, on cherche dans le cache
                return caches.match(event.request);
            })
    );
});
