/* Shared page identity, version header, navigation and comparison affordances.
 * Deploy builds replace version-manifest.json with commit-pinned SHA-256 metadata.
 * This file never treats a query parameter as authoritative build provenance.
 */
(function () {
  "use strict";
  var APP = "timerloggedout-spec/termux-monorepo";
  var PRODUCTION_ROOT = "https://timerloggedout-spec.github.io/help-wanted/";
  var manifestUrl = new URL("./version-manifest.json", window.location.href).href;
  var fallbackPages = [{"id":"3l0","file":"3l0.html","title":"3l0"},{"id":"admin-graph","file":"admin-graph.html","title":"Admin Graph"},{"id":"admin","file":"admin.html","title":"Admin"},{"id":"ates","file":"ates.html","title":"Ates"},{"id":"countdowns","file":"countdowns.html","title":"Countdowns"},{"id":"delphi-ledger","file":"delphi-ledger.html","title":"Delphi Ledger"},{"id":"delphi-rfp","file":"delphi-rfp.html","title":"Delphi Rfp"},{"id":"desk","file":"desk.html","title":"Desk"},{"id":"dispatch-tree","file":"dispatch-tree.html","title":"Dispatch Tree"},{"id":"doe","file":"doe.html","title":"Doe"},{"id":"free-tier-value","file":"free-tier-value.html","title":"Free Tier Value"},{"id":"help-wanted-home","file":"index.html","title":"Help-Wanted Home"},{"id":"lanes-and-scopes","file":"lanes-and-scopes.html","title":"Lanes And Scopes"},{"id":"linguist","file":"linguist.html","title":"Linguist"},{"id":"matrix","file":"matrix.html","title":"Matrix"},{"id":"moneyball","file":"moneyball.html","title":"Moneyball"},{"id":"mvt","file":"mvt.html","title":"Mvt"},{"id":"oracle","file":"oracle.html","title":"Oracle"},{"id":"pr-lanes","file":"pr-lanes.html","title":"Pr Lanes"},{"id":"proposals","file":"proposals.html","title":"Proposals"},{"id":"quota-usage","file":"quota-usage.html","title":"Quota Usage"},{"id":"quota","file":"quota.html","title":"Quota"},{"id":"telemetry","file":"telemetry.html","title":"Telemetry"},{"id":"version-comparison","file":"versioning.html","title":"Version Comparison"}];
  function paramsFor(page, manifest) {
    var q = new URLSearchParams();
    q.set("page_unique_id", page.id);
    q.set("version", page.version || manifest.version || "unverified");
    q.set("channel", manifest.channel || "unknown");
    if (manifest.source_sha) q.set("source_sha", manifest.source_sha);
    return q.toString();
  }
  function currentFile() {
    var path = window.location.pathname.split("/").pop() || "index.html";
    return path.toLowerCase().endsWith(".html") ? path : "index.html";
  }
  function esc(value) {
    return String(value).replace(/[&<>"]/g, function (c) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];
    });
  }
  function makeUrl(page, manifest, root) {
    return root + page.file + "?" + paramsFor(page, manifest);
  }
  function render(manifest) {
    var pages = Array.isArray(manifest.pages) && manifest.pages.length ? manifest.pages : fallbackPages;
    var file = currentFile();
    var current = pages.find(function (p) { return p.file === file; }) || pages[0];
    if (!current) return;
    current.version = manifest.version || "unverified";
    var bar = document.createElement("section");
    bar.id = "page-version-bar";
    bar.setAttribute("aria-label", "Page identity and version navigation");
    bar.innerHTML =
      '<div class="pv-meta"><strong>' + esc(current.id) + '@' + esc(current.version) +
      '</strong><span class="pv-chip">' + esc(manifest.channel || "unknown") + '</span>' +
      '<span class="pv-sha">source: ' + esc((manifest.source_sha || "unverified").slice(0, 12)) + '</span></div>' +
      '<nav class="pv-nav" aria-label="Versioned pages">' +
      '<a href="' + esc(makeUrl({id:"version-comparison",file:"versioning.html"},manifest,"./")) + '">Compare versions</a>' +
      '<details><summary>All pages · unique ID @ version</summary><div class="pv-page-list">' +
      pages.map(function (p) {
        return '<a href="' + esc(makeUrl(p,manifest,"./")) + '">' + esc(p.id) + '@' +
          esc(manifest.version || "unverified") + ' <small>' + esc(p.title || p.file) + '</small></a>';
      }).join("") + '</div></details></nav>';
    var style = document.createElement("style");
    style.textContent = '#page-version-bar{position:relative;z-index:1000;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:.55rem;padding:.55rem max(1rem,calc((100vw - 1440px)/2));background:#101a26;color:#edf3f8;border-bottom:1px solid #35506a;font:13px/1.4 system-ui,sans-serif}#page-version-bar a{color:#8dd5ff;text-decoration:none}#page-version-bar a:hover{text-decoration:underline}.pv-meta,.pv-nav{display:flex;flex-wrap:wrap;align-items:center;gap:.7rem}.pv-chip{border:1px solid #54718a;border-radius:99px;padding:.12rem .5rem;text-transform:uppercase;font-size:10px;letter-spacing:.08em}.pv-sha{color:#a7b8c9;font-family:ui-monospace,monospace;font-size:11px}.pv-nav details{position:relative}.pv-nav summary{cursor:pointer;color:#8dd5ff}.pv-page-list{position:absolute;right:0;top:1.6rem;display:grid;gap:.2rem;min-width:min(360px,90vw);max-height:65vh;overflow:auto;padding:.65rem;background:#101a26;border:1px solid #35506a;border-radius:8px;box-shadow:0 12px 30px #0009}.pv-page-list a{display:grid;padding:.25rem;border-bottom:1px solid #26384a}.pv-page-list small{color:#a7b8c9}';
    document.head.appendChild(style);
    document.body.insertBefore(bar, document.body.firstChild);
    if (manifest.channel === "preview") {
      var banner = document.createElement("div");
      banner.setAttribute("role","status");
      banner.textContent = "PREVIEW BUILD — not production. Source " + (manifest.source_sha || "unverified").slice(0,12) + ". Compare before merge.";
      banner.style.cssText = "padding:.5rem 1rem;background:#49351a;color:#fff0c4;font:600 12px system-ui,sans-serif;text-align:center";
      bar.insertAdjacentElement("afterend", banner);
    }
  }
  function renderComparison() {
    if (!/versioning\.html$/.test(currentFile())) return;
    var root = document.getElementById("version-comparison");
    if (!root) return;
    root.innerHTML = '<p>Loading production and preview manifests…</p>';
    Promise.all([
      fetch(manifestUrl, {cache:"no-store"}).then(function (r) { if(!r.ok) throw new Error("current manifest HTTP "+r.status); return r.json(); }),
      fetch(PRODUCTION_ROOT + "version-manifest.json", {cache:"no-store"}).then(function (r) { if(!r.ok) throw new Error("production manifest HTTP "+r.status); return r.json(); })
    ]).then(function (results) {
      var current = results[0], prod = results[1];
      var currentPages = current.pages || [];
      var productionPages = prod.pages || [];
      var ids = Object.create(null);
      currentPages.concat(productionPages).forEach(function (p) { ids[p.id] = true; });
      var rows = Object.keys(ids).sort().map(function (id) {
        var p = currentPages.find(function (q) { return q.id === id; });
        var old = productionPages.find(function (q) { return q.id === id; });
        var page = p || old;
        var changed = !p ? "REMOVED FROM PREVIEW" : (!old ? "NEW PAGE" : (!old.content_sha256 || !p.content_sha256 ? "HASH UNAVAILABLE" : (old.content_sha256 !== p.content_sha256 ? "CHANGED" : "same content")));
        var previewLink = p ? '<a href="./' + esc(p.file) + '?page_unique_id=' +
          encodeURIComponent(p.id) + '&amp;version=' + encodeURIComponent(current.version) +
          '&amp;channel=' + encodeURIComponent(current.channel) + '">Open preview</a>' : '—';
        var productionLink = old ? '<a href="' + esc(PRODUCTION_ROOT + old.file) + '">Open production</a>' : '—';
        return '<tr><th scope="row">' + esc(id) + '</th><td>' + esc(page.title || page.file) +
          '</td><td>' + esc(changed) + '</td><td>' + previewLink + '</td><td>' + productionLink + '</td></tr>';
      }).join("");
      root.innerHTML = '<p><strong>Current:</strong> ' + esc(current.channel) + ' · ' +
        esc(current.version) + ' · <code>' + esc(current.source_sha || "unverified") +
        '</code></p><p><strong>Production:</strong> ' + esc(prod.version || "unverified") +
        ' · <code>' + esc(prod.source_sha || "unverified") + '</code></p>' +
        (current.source_sha && prod.source_sha ? '<p><a href="https://github.com/' + APP + '/compare/' +
        encodeURIComponent(prod.source_sha) + '...' + encodeURIComponent(current.source_sha) +
        '">GitHub source diff</a></p>' : '<p>Source diff unavailable: one or both manifest source SHAs are missing.</p>') +
        '<div class="pv-table-wrap"><table><thead><tr><th>Page unique ID</th><th>Page</th><th>Comparison</th><th>Preview</th><th>Production</th></tr></thead><tbody>' +
        rows + '</tbody></table></div>';
    }).catch(function (error) {
      root.innerHTML = '<p role="alert">Comparison unavailable: ' + esc(error.message) +
        '. This build is not verified against production.</p>';
    });
  }
  fetch(manifestUrl, {cache:"no-store"}).then(function (r) {
    if (!r.ok) throw new Error("manifest unavailable");
    return r.json();
  }).then(function (manifest) {
    render(manifest);
    renderComparison();
  }).catch(function () {
    render({version:"unverified",channel:"development",source_sha:"",pages:fallbackPages});
    renderComparison();
  });
}());
