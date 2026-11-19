#!/usr/bin/env python3
"""Regression checks for the static ICM CCTV card-board publisher."""
from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_icm_cctv_board import build, cards_from


class IcmCctvBoardTests(unittest.TestCase):
    def test_repository_cards_render_with_source_links_and_research_lineage(self) -> None:
        rendered = build(ROOT / "docs/icm/_tv/screens", "test-source-sha")
        self.assertIn("ICM CCTV", rendered)
        self.assertIn("PR #232 master rebuild", rendered)
        self.assertIn("Provider routing evidence", rendered)
        self.assertIn("blocked", rendered)
        self.assertIn("docs/icm/_meta/master-rebuild-integration-evidence.md", rendered)
        self.assertIn("Jake Van Clief", rendered)
        self.assertIn("test-source-sha", rendered)

    def test_published_navigation_and_sitemap_reference_canonical_route(self) -> None:
        route = "https://timerloggedout-spec.github.io/tribute/icm-cctv.html"
        nav = (ROOT / "apps/tribute-dashboard/site-nav.js").read_text(encoding="utf-8")
        sitemap = (ROOT / "apps/tribute-dashboard/sitemap.xml").read_text(encoding="utf-8")
        hub = (ROOT / "apps/project-pages-hub/index.html").read_text(encoding="utf-8")
        self.assertIn('["ICM CCTV", origin + "/tribute/icm-cctv.html", "icm-cctv"]', nav)
        self.assertIn(route, sitemap)
        self.assertIn(route, hub)

    def test_card_parser_requires_canonical_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            card = root / "stage.md"
            card.write_text("# Missing metadata\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                cards_from(root)

    def test_html_escapes_card_metadata_and_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            card = root / "stage.md"
            card.write_text(
                "---\nid: safe\ntitle: <script>alert(1)</script>\nstage: 3\n"
                "status: done\nsource: source.md\n---\n\n<script>payload</script>\n",
                encoding="utf-8",
            )
            rendered = build(root, "sha")
            self.assertNotIn("<script>alert(1)</script>", rendered)
            self.assertNotIn("<script>payload</script>", rendered)
            self.assertIn("&lt;script&gt;", rendered)


    def test_production_and_preview_publishers_generate_board_before_manifests(self) -> None:
        deploy = (ROOT / ".github/workflows/tribute-dashboard-deploy.yml").read_text(encoding="utf-8")
        preview = (ROOT / ".github/workflows/tribute-dashboard-preview.yml").read_text(encoding="utf-8")
        self.assertNotIn("apps/project-pages-hub/brain-ops/index.html", deploy)
        self.assertIn("python3 scripts/build_icm_cctv_board.py --source-sha", deploy)
        self.assertIn("python3 tooling/scripts/build_icm_cctv_board.py --cards-dir production/docs/icm/_tv/screens", preview)
        self.assertIn("python3 tooling/scripts/build_icm_cctv_board.py --cards-dir source/docs/icm/_tv/screens", preview)


if __name__ == "__main__":
    unittest.main()
