    // service-worker.js

    self.addEventListener('install', event => {
        event.waitUntil(
          caches.open('streamlit-cache').then(cache => {
            return cache.addAll([
              '/',
              '/app3.py',
              '/static/manifest.json'
            ]);
          })
        );
      });
  
      self.addEventListener('fetch', event => {
        event.respondWith(
          caches.match(event.request).then(response => {
            return response || fetch(event.request);
          })
        );
      });
      