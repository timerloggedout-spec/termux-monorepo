/* StudySprint webApp service worker — offline after first load.
 * Cache-first for the app shell + baked core state; the study data
 * in localStorage (SR review state) is never cached here. */
const CACHE = "studysprint-webapp-v1";
const SHELL = [
  "./",
  "index.html",
  "styles.css",
  "app.js",
  "manifest.webmanifest",
  "data/state.json",
  "icons/icon-192.png",
  "icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((hit) =>
      hit || fetch(event.request)));
});
