#!/usr/bin/env python3
from __future__ import annotations
import tempfile, unittest, json
from argparse import Namespace
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sweep_accountability import make_receipt, write_receipt

class SweepAccountabilityTests(unittest.TestCase):
    def base(self):
        return Namespace(
            repository="timerloggedout-spec/termux-monorepo", sweep_version="v1", iteration=7,
            mode="HISTORICAL", status="PARTIAL", coverage="PARTIAL", observed=12, expected=None,
            ref="master", from_time="2026-01-01T00:00:00Z", to_time="2026-09-30T00:00:00Z",
            query="all prior work", cursor="page:3", next_cursor="page:4",
            coverage_reason="source pagination remains", parent_sweep_id="parent-001",
            next_sweep_version=None, sweep_id="sweep-test-001",
            sources='["github://commits","github://pulls"]',
            provenance='{"actor_type":"workflow","actor":"sweep-test","tool":"GitHub","workflow":"test"}',
            findings='[{"id":"f1","classification":"OBSERVED","statement":"example","evidence_refs":["github://commits/abc"],"confidence":1}]',
            actions='[{"id":"a1","type":"scan","status":"SUCCEEDED","actor":"sweep-test","tool":"GitHub"}]',
            effects='[{"id":"e1","type":"receipt","after":{"count":12}}]', errors="[]",
            started_at="2026-09-30T00:00:00Z", completed_at="2026-09-30T00:01:00Z", out_dir=""
        )
    def test_lineage_and_provenance(self):
        r=make_receipt(self.base())
        self.assertEqual(r["schema_version"], "sweep.accountability.v1")
        self.assertEqual(r["parent_sweep_id"], "parent-001")
        self.assertEqual(r["iteration"], 7)
        self.assertEqual(r["coverage"]["next_cursor"], "page:4")
        self.assertIn("input_sha256", r["provenance"])
    def test_append_only_refuses_duplicate_immutable_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            args=self.base(); args.out_dir=td
            r=make_receipt(args); write_receipt(r, Path(td))
            with self.assertRaises(FileExistsError): write_receipt(r, Path(td))

    def test_push_receipt_debounce_is_present(self):
        wf = Path(__file__).resolve().parents[2] / ".github/workflows/sweep-accountability.yml"
        text = wf.read_text()
        self.assertIn("skip receipt push: ref", text)
        self.assertIn("skip receipt: tip is a sweep receipt", text)
        self.assertIn('[ "$age" -lt 900 ]', text)
        self.assertIn('GITHUB_EVENT_NAME" != "schedule"', text)
        self.assertIn('GITHUB_EVENT_NAME" != "workflow_dispatch"', text)
        self.assertNotIn('GITHUB_EVENT_NAME}" = "push"', text)

if __name__ == "__main__":
    unittest.main()
