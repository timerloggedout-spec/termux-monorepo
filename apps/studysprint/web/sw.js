/* StudySprint webApp service worker — offline after first load.
 * #4219: the cache name carries the surface version (build_data.py
 * stamps it from web/VERSION at bundle build), so a new release
 * replaces the cache instead of being pinned behind the first
 * build's. Fetch strategy: data/state.json is NETWORK-FIRST (a
 * refreshed plan reaches installed users; the cache is only the
 * offline fallback); the shell uses stale-while-revalidate. The
 * study data in localStorage is never cached here.
 *
 * App-package B (#4437): updates no longer apply silently. The
 * new worker WAITS (no skipWaiting on install); the page notices
 * via the registration and shows the update toast; only when the
 * user taps it does the page post SKIP_WAITING and reload onto
 * the new version. Navigations that fail with nothing cached
 * land on the custom offline page. */
const CACHE = "studysprint-webapp-v0.2.0";
const SHELL = [
  "./",
  "index.html",
  "offline.html",
  "styles.css",
  "app.js",
  "manifest.webmanifest",
  "data/state.json",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "icons/icon-maskable-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.endsWith("data/state.json")) {
    // network-first: fresh core state wins; cache is the fallback
    event.respondWith(
      fetch(event.request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((cache) =>
          cache.put(event.request, copy));
        return resp;
      }).catch(() => caches.match(event.request)));
    return;
  }
  if (event.request.mode === "navigate") {
    // page loads: cache (stale-while-revalidate below covers
    // refresh) or the custom offline page — never a dead end
    event.respondWith(
      caches.match(event.request).then((hit) => hit ||
        fetch(event.request).catch(() =>
          caches.match("offline.html"))));
    return;
  }
  // stale-while-revalidate for the shell
  event.respondWith(
    caches.match(event.request).then((hit) => {
      const refresh = fetch(event.request).then((resp) => {
        const copy = resp.clone();
        caches.open(CACHE).then((cache) =>
          cache.put(event.request, copy));
        return resp;
      }).catch(() => hit);
      return hit || refresh;
    }));
});
