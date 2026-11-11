#!/usr/bin/env python3
"""Offline integrity tests for Tribute Family / Swarm Quota / DoE Settings links."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "apps/tribute-dashboard"


class TributeFamilyIntegrityTests(unittest.TestCase):
    def test_nested_family_page_uses_canonical_feed_twin(self):
        page = (DASH / "family.html").read_text()
        self.assertIn("apps/tribute-dashboard/data/nested-family-feed.json", page)
        self.assertNotIn("apps/help-wanted-dashboard/data/nested-family-feed.json", page)
        self.assertIn("nested-family/v1", page)
        self.assertIn("doe-settings.html", page)
        self.assertIn("instance_key", page)
        self.assertIn("instance_key NOT ESTABLISHED", page)

    def test_swarm_page_uses_canonical_nested_family_twin(self):
        page = (DASH / "quota-swarm.html").read_text()
        self.assertIn("apps/tribute-dashboard/data/nested-family-feed.json", page)
        self.assertNotIn("apps/help-wanted-dashboard/data/nested-family-feed.json", page)
        self.assertIn("quota-usage-series-refresh.yml", page)
        self.assertNotIn("refresh automation pending", page.lower())
        self.assertIn("doe-settings.html", page)

    def test_shared_navigation_exposes_doe_settings(self):
        nav = (DASH / "site-nav.js").read_text()
        self.assertIn('["DoE settings", tribute + "doe-settings.html", "doe-settings"]', nav)

    def test_nested_family_contract_remains_v1_and_instance_key_is_not_enriched(self):
        spec = (ROOT / "docs/ops/NESTED-FAMILY.md").read_text()
        collector = (ROOT / "scripts/tracking/nested_family.py").read_text()
        self.assertIn("nested-family/v1", spec)
        self.assertIn("instance_key", spec)
        fill_fields = collector.split('_FILL_FIELDS = (', 1)[1].split(')', 1)[0]
        self.assertNotIn('"instance_key"', fill_fields)

    def test_settings_dashboard_reads_the_static_mirror(self):
        page = (DASH / "doe-settings.html").read_text()
        self.assertIn("./data/doe-settings-register.json", page)
        self.assertIn("doe.settings-register/v1", page)
        self.assertIn("chartkit.js", page)
        self.assertIn("CK.bars", page)
        self.assertIn("chart-stamp", page)
        surface_map = (DASH / "surfaces-map.html").read_text()
        self.assertIn('["doe-settings.html","tribute","scoring"', surface_map)
        surfaces_doc = (ROOT / "docs/ops/SURFACES-MAP.md").read_text()
        self.assertIn("doe-settings.html", surfaces_doc)
        sitemap = (DASH / "sitemap.xml").read_text()
        self.assertIn("doe-settings.html", sitemap)
        source = (ROOT / "ops/doe/settings-register.json").read_bytes()
        mirror = (DASH / "data/doe-settings-register.json").read_bytes()
        self.assertEqual(source, mirror)

    def test_dashboard_does_not_rewrite_the_generated_feed_contract(self):
        feed = json.loads((DASH / "data/nested-family-feed.json").read_text())
        self.assertEqual(feed["schema"], "nested-family/v1")
        self.assertIn("providers", feed)
        self.assertIn("summary", feed)


if __name__ == "__main__":
    unittest.main()
