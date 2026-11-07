/* Source-tree alias for the shared dashboard navigation.
 * The production deploy copies the canonical site-nav.js to the site root;
 * local source previews load the same implementation from the dashboard.
 */
(function () {
  var script = document.createElement("script");
  script.src = "../tribute-dashboard/site-nav.js";
  script.defer = true;
  document.head.appendChild(script);
})();
