/* Service worker — installability ∧ offline shell ONLY.
   Pages ∧ data feeds are LIVE: every fetch goes network-first, so an
   installed app never serves stale readings; the cache answers only
   when the network is unreachable (shell + icons + last-good page). */
var CACHE = "tribute-v1";
var SHELL = ["./", "./index.html", "./dashboard.css", "./manifest.webmanifest",
             "./versioning.js", "./site-nav.js", "./version-manifest.json",
             "./icon-192.png", "./icon-512.png"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(SHELL); })
    .then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.map(function (k) {
      return k === CACHE ? null : caches.delete(k);
    }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then(function (res) {
    var copy = res.clone();
    caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
    return res;
  }).catch(function () {
    return caches.match(e.request, { ignoreSearch: true });
  }));
});
