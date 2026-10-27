import json
import math
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "apps/help-wanted-dashboard/data/free-tier-value.json"
PAGE = ROOT / "apps/help-wanted-dashboard/free-tier-value.html"
DOC = ROOT / "docs/ops/FREE-TIER-USE-VALUE-BOARD.md"


class FreeTierValueBoardContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.doc = DOC.read_text(encoding="utf-8")

    def test_schema_and_pricing_records_are_source_linked(self):
        self.assertEqual(self.data["schema"], "3l0.free-tier-use-value.v1")
        self.assertGreaterEqual(len(self.data["pricing"]), 3)
        ids = set()
        canonical_ids = set()
        for row in self.data["pricing"]:
            self.assertTrue(row["pricing_id"])
            self.assertTrue(row["canonical_model_id"])
            self.assertNotIn(row["canonical_model_id"], canonical_ids)
            canonical_ids.add(row["canonical_model_id"])
            self.assertNotIn(row["pricing_id"], ids)
            ids.add(row["pricing_id"])
            self.assertGreaterEqual(row["input_usd_per_million"], 0)
            self.assertGreaterEqual(row["output_usd_per_million"], 0)
            self.assertTrue(row["source_url"].startswith("https://"))
            self.assertTrue(row["price_observed_at"])
            for field in ("input_usd_per_million", "output_usd_per_million"):
                rate = row[field]
                self.assertIsInstance(rate, (int, float))
                self.assertNotIsInstance(rate, bool)
                self.assertTrue(math.isfinite(rate))
                self.assertGreaterEqual(rate, 0)

    def test_openai_price_basis_matches_standard_rates(self):
        row = next(p for p in self.data["pricing"] if p["pricing_id"] == "openai-gpt-5.3-codex-standard")
        self.assertEqual(row["price_basis"], "Standard API list price")
        self.assertEqual(row["input_usd_per_million"], 1.75)
        self.assertEqual(row["output_usd_per_million"], 14)

    def test_missing_session_feed_is_explicit_not_synthesized(self):
        self.assertEqual(self.data["sessions"], [])
        self.assertIn("unknown", self.data["policy"]["unknown_semantics"].lower())
        self.assertIn("Missing data is not zero", self.page)

    def test_value_headline_requires_all_validation_gates(self):
        for gate in ("validation_status", "basksweep_status", "publication_status"):
            self.assertIn(gate, self.page)
        self.assertIn("VALIDATED", self.page)
        self.assertIn("PASS", self.page)
        self.assertIn("PUBLIC_SAFE", self.page)
        self.assertIn("VERIFIED_NO_COST", self.page)
        self.assertIn("SUCCESS_OUTCOMES", self.page)
        self.assertIn("SUCCESS", self.page)
        self.assertIn("SUCCEEDED", self.page)
        self.assertIn("Number.isFinite(p.input_usd_per_million)", self.page)
        self.assertIn("Number.isFinite(p.output_usd_per_million)", self.page)
        self.assertIn("typeof p.canonical_model_id==='string'", self.page)
        self.assertIn("p.canonical_model_id===s.canonical_model_id", self.page)
        self.assertIn("SESSION_KEYS", self.page)
        self.assertIn("safeHref(p.source_url)", self.page)
        self.assertIn("unavailable??", self.page)
        self.assertIn("safeHref", self.page)
        self.assertIn("u.protocol==='https:'", self.page)

    def test_public_page_and_methodology_are_linked(self):
        self.assertIn("free-tier-value.json", self.page)
        self.assertIn("FREE-TIER-USE-VALUE-BOARD.md", self.page)
        self.assertIn("time_invested_value", self.doc)
        self.assertIn("paid_equivalent_usd", self.doc)
        self.assertIn("billing_status=VERIFIED_NO_COST", self.doc)

    def test_session_contract_has_explicit_allowlist_and_success_gate(self):
        match = re.search(r"const SESSION_KEYS=new Set\(\[(.*?)\]\);", self.page)
        self.assertIsNotNone(match, "browser must declare an explicit session-field allowlist")
        allowed = set(re.findall(r"'([^']+)'", match.group(1)))
        expected = {
            "session_label", "run_uid", "workflow", "source_sha", "observed_at",
            "provider", "model_id", "canonical_model_id", "input_tokens", "output_tokens",
            "elapsed_seconds", "outcome_status", "evidence_url",
            "validation_status", "basksweep_status", "publication_status",
            "billing_status", "pricing_id",
        }
        self.assertEqual(allowed, expected)
        self.assertIn("Object.keys(s).every(k=>SESSION_KEYS.has(k))", self.page)
        self.assertIn("SUCCESS_OUTCOMES", self.page)
        self.assertIn("outcome_status", self.doc)
        self.assertTrue({"run_uid", "outcome_status"}.issubset(allowed))
        forbidden = {"prompt_text", "messages", "tool_payload", "private_balance", "prompt", "completion"}
        self.assertTrue(allowed.isdisjoint(forbidden))

    def test_session_value_requires_provenance_and_safe_evidence(self):
        self.assertIn("typeof s.run_uid==='string'&&s.run_uid.trim().length>0", self.page)
        self.assertIn("typeof s.workflow==='string'&&s.workflow.trim().length>0", self.page)
        self.assertIn("typeof s.source_sha==='string'&&/^[0-9a-f]{40}$/i.test(s.source_sha)", self.page)
        self.assertIn("Number.isFinite(Date.parse(s.observed_at))&&/Z$/.test(s.observed_at)", self.page)
        self.assertIn("typeof s.model_id==='string'&&s.model_id.trim().length>0", self.page)
        self.assertIn("typeof s.canonical_model_id==='string'&&s.canonical_model_id.trim().length>0", self.page)
        self.assertIn("!!safeHref(s.evidence_url)", self.page)
        self.assertIn("Number.isFinite(s.elapsed_seconds)&&s.elapsed_seconds>=0", self.page)

    def test_public_payload_has_no_prompt_or_completion_fields(self):
        encoded = json.dumps(self.data).lower()
        self.assertNotIn('"prompt":', encoded)
        self.assertNotIn('"completion":', encoded)
        self.assertNotIn('"api_key":', encoded)
        self.assertNotIn('"private_balance":', encoded)


class DedupeTest(unittest.TestCase):
    def test_headline_deduplicates_by_stable_row_identity(self):
        html = PAGE.read_text()
        self.assertIn("function rowIdentity(s)", html)
        self.assertIn("function dedupe(rows)", html)
        # identity must distinguish multiple rows from the same run
        ident = html.split("function rowIdentity(s)")[1].split("}")[0]
        for field in ("run_uid", "session_label", "observed_at", "source_sha"):
            self.assertIn(field, ident)
        self.assertIn("const rows=dedupe(d.sessions.filter(valid))", html)


if __name__ == "__main__":
    unittest.main()
