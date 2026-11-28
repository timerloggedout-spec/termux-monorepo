import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

from scripts.ops import render_teammate_portal_status as renderer

class PortalLocaleRenderingTests(unittest.TestCase):
    def test_urdu_page_has_rtl_metadata_and_language_links(self):
        page = renderer.page("اردو", "<main>مواد</main>", "ur")
        self.assertIn('<html lang="ur" dir="rtl">', page)
        self.assertIn('href="../index.html"', page)
        self.assertIn('href="./index.html"', page)

    def test_urdu_catalog_contains_native_locale_and_messages(self):
        messages = renderer.load_catalog("ur")
        self.assertEqual(messages["nav.urdu"], "اردو")
        self.assertTrue(messages["page.title"])

    def test_render_writes_english_and_urdu_entrypoints(self):
        with tempfile.TemporaryDirectory() as temp:
            argv = ["render_teammate_portal_status.py", "--out", temp, "--source-ref", "test", "--source-sha", "abc1234", "--repo", "timerloggedout-spec/termux-monorepo", "--pr", "5840"]
            with patch.object(sys, "argv", argv):
                renderer.main()
            english = (Path(temp) / "index.html").read_text(encoding="utf-8")
            urdu = (Path(temp) / "ur" / "index.html").read_text(encoding="utf-8")
            self.assertIn('lang="en" dir="ltr"', english)
            self.assertIn('lang="ur" dir="rtl"', urdu)
            self.assertIn("ٹیم میٹ پورٹل", urdu)

if __name__ == "__main__":
    unittest.main()
