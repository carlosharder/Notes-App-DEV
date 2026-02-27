/**
 * Notes PWA — Service Worker
 *
 * Caching strategies:
 *   /static/*       → cache-first  (versioned by CACHE_NAME)
 *   /api/audio/*    → cache-first  (immutable once uploaded)
 *   /api/*  (GET)   → network-first, fallback to cache
 *   navigation      → network-first, fallback to cached shell
 */

const CACHE_NAME = 'notes-v2';

const STATIC_ASSETS = [
    '/static/app.js',
    '/static/style.css',
    '/static/icon.svg',
    '/static/icon-192.png',
    '/static/icon-512.png',
    '/static/manifest.json',
];

// --- Install: pre-cache static assets ---
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
    self.skipWaiting();
});

// --- Activate: clean up old caches ---
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

// --- Fetch: route requests to appropriate strategy ---
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);
    const request = event.request;

    // Only cache GET requests
    if (request.method !== 'GET') return;

    // Static assets → cache-first
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(cacheFirst(request));
        return;
    }

    // Audio files → cache-first (immutable)
    if (url.pathname.startsWith('/api/audio/')) {
        event.respondWith(cacheFirst(request));
        return;
    }

    // API GET requests → network-first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirst(request));
        return;
    }

    // Navigation (/, /login, /notes, /notes/*) → network-first
    if (request.mode === 'navigate' || url.pathname === '/' ||
        url.pathname === '/login' || url.pathname.startsWith('/notes')) {
        event.respondWith(networkFirst(request));
        return;
    }
});

// --- Cache-first: try cache, then network ---
async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        return new Response('Offline', { status: 503, statusText: 'Offline' });
    }
}

// --- Network-first: try network, then cache ---
async function networkFirst(request) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) return cached;

        // For navigation, try returning the cached /notes shell
        if (request.mode === 'navigate') {
            const shell = await caches.match('/notes');
            if (shell) return shell;
        }

        return new Response('Offline', { status: 503, statusText: 'Offline' });
    }
}
