// static/sw.js

// Un service worker minimale per abilitare la funzionalità PWA "installabile".
// Per ora non gestisce la cache offline, ma fa sì che il browser
// riconosca il sito come un'applicazione.

self.addEventListener('install', (event) => {
  console.log('Service Worker: Installato');
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker: Attivato');
});

self.addEventListener('fetch', (event) => {
  // Per ora, non intercettiamo le richieste, andiamo direttamente alla rete.
  // In futuro, qui si potrebbe implementare la logica offline.
  event.respondWith(fetch(event.request));
});