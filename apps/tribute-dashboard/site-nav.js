/* Cross-repo publisher consumes this shared nav for Tribute, the legacy alias, and Matrix. */
/* Single source of truth for primary navigation across Tribute, matrix and previews. */
(function () {
  "use strict";
  var origin = "https://timerloggedout-spec.github.io";
  var path = window.location.pathname.toLowerCase();
  var previewMatch = path.match(/^\/previews\/([a-z0-9][a-z0-9-]{0,60})\/tribute(?:\/|$)/);
  var tribute = previewMatch
    ? origin + "/previews/" + previewMatch[1] + "/tribute/"
    : origin + "/tribute/";
  var links = [
    ["Marketing", origin + "/", "marketing"],
    ["Tribute", tribute, "tribute"],
    ["Lane matrix", origin + "/matrix/", "matrix"],
    ["Quota", tribute + "quota.html", "quota"],
    ["Quota usage", tribute + "quota-usage.html", "quota-usage"],
    ["Quota graphs", tribute + "quota-graphs.html", "quota-graphs"],
    ["Swarm quota", tribute + "quota-swarm.html", "quota-swarm"],
    ["Admin", tribute + "admin.html", "admin"],
    ["Admin graph", tribute + "admin-graph.html", "admin-graph"],
    ["Oracle", tribute + "oracle.html", "oracle"],
    ["3L0", tribute + "3l0.html", "3l0"],
    ["MoneyBall", tribute + "moneyball.html", "moneyball"],
    ["Wagering Book", tribute + "wagering-book.html", "wagering-book"],
    ["MVT", tribute + "mvt.html", "mvt"],
    ["DoE", tribute + "doe.html", "doe"],
    ["ATES", tribute + "ates.html", "ates"],
    ["Results Index", tribute + "results-index.html", "results-index"],
    ["Free-tier value", tribute + "free-tier-value.html", "free-tier-value"],
    ["Dispatch tree", tribute + "dispatch-tree.html", "dispatch-tree"],
    ["Countdowns", tribute + "countdowns.html", "countdowns"],
    ["Linguist", tribute + "linguist.html", "linguist"],
    ["Delphi RFP", tribute + "delphi-rfp.html", "delphi-rfp"],
    ["Delphi ledger", tribute + "delphi-ledger.html", "delphi-ledger"],
    ["Classifiers", tribute + "classifiers.html", "classifiers"],
    ["PR lanes", tribute + "pr-lanes.html", "pr-lanes"],
    ["Proposals", tribute + "proposals.html", "proposals"],
    ["Referrals", tribute + "referrals.html", "referrals"],
    ["Telemetry", tribute + "telemetry.html", "telemetry"],
    ["Desk", tribute + "desk.html", "desk"],
    ["Tracking", tribute + "tracking.html", "tracking"],
    ["Family", tribute + "family.html", "family"],
    ["Version comparison", tribute + "versioning.html", "versioning"],
    ["Sitemap", tribute + "sitemap.xml", "sitemap"],
    ["Vercel deployment", "https://help-wanted-oversight.vercel.app/", "vercel"],
    ["Project hub", origin + "/termux-monorepo/", "project-hub"],
    ["Monorepo", "https://github.com/timerloggedout-spec/termux-monorepo", "monorepo"]
  ];
  var current = path.split("/").filter(Boolean).pop() || "index.html";
  if (current.indexOf(".") < 0) current = "index.html";
  var active = current === "index.html" && (path.indexOf("/tribute/") >= 0 || path.indexOf("/help-wanted/") >= 0)
    ? "tribute"
    : (path.indexOf("/matrix/") >= 0 || current === "matrix.html" ? "matrix" : current.replace(/\.html$/, ""));
  var nav = document.querySelector('nav[aria-label="Primary"], #site-primary-nav');
  if (!nav) {
    nav = document.createElement("nav");
    document.body.insertBefore(nav, document.body.firstChild);
  }
  nav.id = "site-primary-nav";
  nav.setAttribute("aria-label", "Primary");
  nav.innerHTML = '<a class="site-nav-brand" href="' + origin + '/">Autonomous AI Employees</a>' +
    links.map(function (item) {
      var isCurrent = item[2] === active;
      return '<a href="' + item[1] + '"' + (isCurrent ? ' aria-current="page"' : "") + '>' + item[0] + '</a>';
    }).join("");
  if (!document.getElementById("site-primary-nav-style")) {
    var style = document.createElement("style");
    style.id = "site-primary-nav-style";
    style.textContent = '#site-primary-nav{display:flex;flex-wrap:wrap;align-items:center;gap:.4rem .9rem;padding:.75rem 1rem;background:#0b1118;border-bottom:1px solid #26384a;font:500 13px/1.45 system-ui,sans-serif;position:relative;z-index:900}#site-primary-nav a{color:#b9dfff;text-decoration:none;white-space:nowrap}#site-primary-nav a:hover,#site-primary-nav a[aria-current="page"]{color:#fff;text-decoration:underline;text-underline-offset:3px}#site-primary-nav .site-nav-brand{font-weight:800;color:#fff;margin-right:.4rem}';
    document.head.appendChild(style);
  }
})();
