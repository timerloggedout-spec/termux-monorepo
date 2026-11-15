"""Owner-records page contract (D1-D5): metadata-only rendering, D4
discovery rules, build provenance and the validated envelope explorer."""
import json
import re
import subprocess
import sys
import tempfile
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
            match = re.search(r'<nav aria-label="Primary">([\s\S]*?)</nav>', page.read_text())
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

    def test_deployed_build_preserves_owner_records_d4_boundary(self):
        # The deployment builder injects versioning.js into ordinary pages;
        # that script loads shared navigation and an all-pages menu. Owner
        # Records verifies its manifest itself and must remain excluded.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "owner-records.html").write_text(
                """<!doctype html><html><head></head><body>Owner Records</body></html>"""
            )
            (root / "admin.html").write_text(
                """<!doctype html><html><head></head><body>Admin</body></html>"""
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_dashboard_manifest.py"),
                 "--root", tmp, "--channel", "preview",
                 "--source-ref", "refs/pull/5448/head",
                 "--source-sha", "4b0a550750c9230b17669eda09713ea593cbb370"],
                cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            owner_html = (root / "owner-records.html").read_text()
            admin_html = (root / "admin.html").read_text()
            self.assertNotIn('src="./versioning.js"', owner_html)
            self.assertIn('src="./versioning.js"', admin_html)
            manifest = json.loads((root / "version-manifest.json").read_text())
            self.assertIn("owner-records.html", [page["file"] for page in manifest["pages"]])

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

    def test_canonical_envelope_passes_store_validator(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/owner_records.py"),
             "validate", "--root", str(ROOT)],
            cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("envelope valid: 5 classes", result.stdout)

    def test_vercel_stages_build_pinned_envelope_before_raw_fallback(self):
        workflow = (ROOT / ".github/workflows/owner-records-vercel.yml").read_text()
        self.assertIn(
            'cp "$GITHUB_WORKSPACE/ops/owner-records/index.json" "$W/owner-records.json"',
            workflow)
        html = PAGE.read_text()
        local_copy = html.index('"./owner-records.json?t="')
        public_fallback = html.index(
            '"https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/master/ops/owner-records/index.json?t="')
        self.assertLess(local_copy, public_fallback)

    def test_owner_records_contract_runs_in_repo_gate(self):
        workflow = (ROOT / ".github/workflows/repo-gate.yml").read_text()
        self.assertIn("test_owner_records_page.py", workflow)

    def test_refresh_is_non_overlapping_and_visibility_aware(self):
        html = PAGE.read_text()
        self.assertIn('if (loading || document.visibilityState === "hidden") return;', html)
        self.assertIn('document.addEventListener("visibilitychange"', html)
        self.assertIn("window.setInterval(loadEnvelope, 60000)", html)
        self.assertIn("showing last validated envelope", html)


if __name__ == "__main__":
    unittest.main()
