/* PWA install (owner order 2026-10-31): the surface REQUESTS installation
   where the platform allows. Chromium: capture beforeinstallprompt ∧ show
   an Install pill; acceptance ∨ dismissal ⇒ pill gone (choice respected,
   ∅ nag loop). No prompt event (iOS/Firefox) ⇒ nothing shown — those
   platforms install via their own share-sheet, apple-touch-icon wired.
   Also registers ./sw.js (installability ∧ offline shell). */
(function () {
  "use strict";
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("./sw.js").catch(function () {});
    });
  }
  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    if (document.getElementById("pwa-install")) return;
    var b = document.createElement("button");
    b.id = "pwa-install";
    b.type = "button";
    b.textContent = "Install app";
    b.setAttribute("style",
      "position:fixed;right:14px;bottom:14px;z-index:99;padding:10px 16px;" +
      "border-radius:999px;border:1px solid #2ea043;background:#0b0d10;" +
      "color:#e8f5ec;font:600 14px system-ui,sans-serif;cursor:pointer;" +
      "box-shadow:0 4px 18px rgba(0,0,0,.45)");
    b.addEventListener("click", function () {
      b.remove();
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.then(function () { deferred = null; });
    });
    document.body.appendChild(b);
  });
  window.addEventListener("appinstalled", function () {
    var b = document.getElementById("pwa-install");
    if (b) b.remove();
    deferred = null;
  });
})();
