"""Admin Graph page contract and live routing-pulse integration."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "tribute-dashboard"
PAGE = APP / "admin-graph.html"
NAV_LINK = ('<a href="https://timerloggedout-spec.github.io/help-wanted/'
            'admin-graph.html">Admin Graph</a>')
NAV_PAGES = ["index.html", "quota.html", "matrix.html", "admin.html",
             "oracle.html", "moneyball.html", "3l0.html", "mvt.html",
             "doe.html", "ates.html", "free-tier-value.html",
             "countdowns.html", "delphi-ledger.html", "delphi-rfp.html",
             "dispatch-tree.html", "linguist.html", "pr-lanes.html",
             "proposals.html", "quota-usage.html", "telemetry.html"]


class AdminGraphPageContractTests(unittest.TestCase):
    def test_page_present_and_self_contained(self):
        html = PAGE.read_text(encoding="utf-8")
        self.assertIn("Admin Interaction Graph", html)
        self.assertNotIn("api.github.com", html)
        self.assertNotIn("raw.githubusercontent", html)

    def test_live_route_pulse_contract(self):
        html = PAGE.read_text(encoding="utf-8")
        markers = ("LIVE ROUTE PULSES", "LIVE_FEED_URL", "task_routed",
                   "routing-orch", "after_seq", "LIVE_CURSOR_KEY", "localStorage", "commitRuntimeCursor", "var reverse=false", "PREPARED",
                   "pull-to-refresh", "DEPLOYMENT-LANES")
        for marker in markers:
            with self.subTest(marker=marker):
                self.assertIn(marker, html)

    def test_nav_link_on_every_published_page(self):
        for name in NAV_PAGES:
            with self.subTest(page=name):
                self.assertIn(NAV_LINK, (APP / name).read_text(encoding="utf-8"))

    def test_in_sitemap(self):
        self.assertIn("help-wanted/admin-graph.html",
                      (APP / "sitemap.xml").read_text(encoding="utf-8"))

    def test_admin_systems_inventory_row(self):
        self.assertIn("<td>Admin Interaction Graph</td>",
                      (APP / "admin.html").read_text(encoding="utf-8"))

    def test_worker_verifies_claim_provenance_and_cursor_reads(self):
        worker = (ROOT / "ops" / "admin-graph-live" / "worker.js").read_text(encoding="utf-8")
        self.assertIn("verifyRouteComment", worker)
        self.assertIn("issues/comments/", worker)
        self.assertIn("after_seq", worker)
        self.assertIn("INSERT OR IGNORE", worker)
        self.assertIn("workflow_path: run.path || null", worker)
        self.assertIn('if (event.kind !== "route") event.payload = null;', worker)


if __name__ == "__main__":
    unittest.main()
