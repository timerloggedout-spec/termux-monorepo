import json
import tempfile
import unittest
from pathlib import Path

from scripts.ci.curate_briefing_sources import curate, discover_inputs, is_http_url


class BriefingSourceCurationTests(unittest.TestCase):
    def test_extracts_json_item_sources_with_item_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "brief.json"
            path.write_text(json.dumps({
                "briefing_date": "2026-10-04",
                "items": [{
                    "id": "mcp-release",
                    "headline": "MCP release",
                    "horizon": "H1",
                    "evidence_status": "confirmed",
                    "sources": [{"url": "https://example.org/release", "source_type": "official_release"}],
                }],
            }), encoding="utf-8")
            rows = curate([path], root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["item_id"], "mcp-release")
        self.assertEqual(rows[0]["item_headline"], "MCP release")
        self.assertEqual(rows[0]["source_type"], "official_release")
        self.assertEqual(rows[0]["source_url"], "https://example.org/release")

    def test_markdown_keeps_heading_and_link_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "brief.md"
            path.write_text("# Agent Safety\nPrimary source: [Official release](https://example.org/release).\n", encoding="utf-8")
            rows = curate([path], root)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["item_headline"], "Agent Safety")
        self.assertEqual(rows[0]["citation_text"], "Official release")

    def test_deduplicates_same_citation_but_keeps_cross_document_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "one.json"
            second = root / "two.json"
            payload = {"canonical_source": "https://example.org"}
            first.write_text(json.dumps(payload), encoding="utf-8")
            second.write_text(json.dumps(payload), encoding="utf-8")
            rows = curate([first, first, second], root)
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({row["citation_id"] for row in rows}), 2)

    def test_rejects_malformed_jsonl_instead_of_silently_dropping_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "bad.jsonl"
            path.write_text("{not-json}\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                curate([path], root)

    def test_only_http_sources_are_accepted(self):
        self.assertTrue(is_http_url("https://example.org"))
        self.assertFalse(is_http_url("file:///etc/passwd"))
        self.assertFalse(is_http_url("javascript:alert(1)"))

    def test_discovery_excludes_its_own_generated_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/briefing").mkdir(parents=True)
            (root / "docs/briefing").mkdir(parents=True)
            ledger = root / "data/briefing/source-citations.jsonl"
            index = root / "docs/briefing/SOURCE-CITATION-INDEX.md"
            ledger.write_text("", encoding="utf-8")
            index.write_text("https://example.org", encoding="utf-8")
            discovered = discover_inputs(root)
            self.assertNotIn(ledger, discovered)
            self.assertNotIn(index, discovered)


if __name__ == "__main__":
    unittest.main()
