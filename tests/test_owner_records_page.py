"""Owner-records page contract (D1-D5): metadata-only rendering, D4
discovery rules, build provenance and the validated envelope explorer."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/tribute-dashboard"
PAGE = APP / "owner-records.html"
ADMIN = APP / "admin.html"
TRACKING = APP / "tracking.html"


class OwnerRecordsPageTests(unittest.TestCase):
    def test_page_fetches_envelope_and_renders_classes(self):
        html = PAGE.read_text()
        self.assertIn("ops/owner-records/index.json", html)
        self.assertIn("./owner-records.json", html)  # staged copy on gated project
        for marker in ("body_status", "NOT_ESTABLISHED", "pending the owner key step"):
            self.assertIn(marker, html)

    def test_d4_no_primary_nav_no_sitemap(self):
        html = PAGE.read_text()
        # D4: Admin + Tracking cross-links only; never add primary navigation.
        self.assertNotIn('aria-label="Primary"', html)
        self.assertNotIn("owner-records.html", (APP / "sitemap.xml").read_text())
        nav_pages = [p for p in APP.glob("*.html") if p != PAGE]
        for page in nav_pages:
            match = re.search(r'<nav aria-label="Primary">([\\s\\S]*?)</nav>', page.read_text())
            if match:
                self.assertNotIn("owner-records", match.group(1), page.name)

    def test_d4_crosslinks_from_admin_and_tracking_only(self):
        self.assertIn("./owner-records.html", ADMIN.read_text())
        self.assertIn("./owner-records.html", TRACKING.read_text())
        # The admin credential scan forbids the literal 'authorization'.
        self.assertNotIn("authorization", ADMIN.read_text().lower())

    def test_versioning_registry_entries(self):
        manifest = json.loads((APP / "version-manifest.json").read_text())
        files = [page["file"] for page in manifest["pages"]]
        self.assertIn("owner-records.html", files)
        self.assertEqual(files, sorted(files))
        vjs = (APP / "versioning.js").read_text()
        self.assertIn('"file":"owner-records.html"', vjs.replace(" ", ""))

    def test_metadata_explorer_controls_are_accessible(self):
        html = PAGE.read_text()
        for control in ('id="record-search"', 'id="class-filter"', 'id="state-filter"',
                        'id="clear-filters"', 'id="results-count"'):
            self.assertIn(control, html)
        self.assertIn('role="status" aria-live="polite"', html)
        self.assertIn("Search covers L1 metadata only.", html)
        self.assertIn("no body search", html)

    def test_build_identity_uses_manifest_without_adding_primary_navigation(self):
        html = PAGE.read_text()
        self.assertIn('fetch("./version-manifest.json"', html)
        self.assertIn("manifest.source_sha", html)
        self.assertIn("URL parameters differ (manifest wins)", html)
        # versioning.js injects shared all-pages navigation; D4 excludes it.
        self.assertNotIn('src="./versioning.js"', html)
        self.assertNotIn("site-nav.js", html)
        self.assertNotIn('aria-label="Primary"', html)

    def test_envelope_validation_fails_closed_and_keeps_bodies_out_of_page(self):
        html = PAGE.read_text()
        for marker in ("validateEnvelope", "ALLOWED_ENVELOPE_FIELDS", "ALLOWED_RECORD_FIELDS",
                       "FORBIDDEN_BODY_FIELDS", "owner-records/v1",
                       "No unvalidated data was rendered.", "Envelope rejected:"):
            self.assertIn(marker, html)
        # Public projection must not request an age identity or decrypt.
        self.assertNotIn('type="password"', html)
        self.assertNotIn("decrypt(", html)
        self.assertNotIn('fetch("ops/owner-records/bodies', html)

    def test_refresh_is_non_overlapping_and_visibility_aware(self):
        html = PAGE.read_text()
        self.assertIn('if (loading || document.visibilityState === "hidden") return;', html)
        self.assertIn('document.addEventListener("visibilitychange"', html)
        self.assertIn("window.setInterval(loadEnvelope, 60000)", html)


if __name__ == "__main__":
    unittest.main()
