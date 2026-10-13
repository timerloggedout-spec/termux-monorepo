#!/usr/bin/env python3
"""Tests for evidence_to_ops_events (stdlib)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

_LOCAL = Path(__file__).resolve().parent
_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "ops"
for p in (_SCRIPTS, _LOCAL):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from evidence_to_ops_events import (
    build_log,
    load_receipts,
    receipt_to_event,
    summarize,
    tributes_to_receipts,
)


class TestEvidenceToOps(unittest.TestCase):
    def test_receipt_upstream(self):
        ev = receipt_to_event({
            "ts": "2026-09-19T19:20:00Z",
            "kind": "upstream_pr",
            "issue": "https://github.com/DioNanos/codex-termux/issues/14",
            "ok": True,
            "lane": "help-wanted",
            "scout": "oversight",
        })
        self.assertIsNotNone(ev)
        assert ev is not None
        self.assertEqual(ev.op, "A")
        self.assertIn("help-given/upstream_pr/", ev.path)
        self.assertEqual(ev.colour, "00FF00")

    def test_followup_skip(self):
        ev = receipt_to_event({
            "ts": "2026-09-21T04:54:20Z",
            "kind": "followup_skip_idempotent",
            "issue": "https://github.com/vedantnimbarte/zero/pull/81",
            "ok": True,
            "foreign": True,
            "lane": "help-wanted-followup",
        })
        assert ev is not None
        self.assertEqual(ev.meta.get("foreign"), True)
        self.assertIn("followup_skip_idempotent", ev.path)

    def test_tributes_board(self):
        status = {
            "generated_at": "2026-09-21T23:00:00Z",
            "tributes": [{
                "pr_url": "https://github.com/o/r/pull/1",
                "ok": True,
                "last_ts": "2026-09-21T22:00:00Z",
                "repo": "o/r",
                "number": 1,
                "title": "t",
                "state": "open",
                "kinds": ["upstream_pr"],
            }],
            "foreign_open_prs": [{
                "html_url": "https://github.com/o/r/pull/1",
                "title": "t",
                "number": 1,
                "repo": "o/r",
                "state": "open",
                "updated_at": "2026-09-21T22:30:00Z",
            }],
        }
        recs = tributes_to_receipts(status)
        self.assertEqual(len(recs), 2)
        log = build_log(recs)
        self.assertEqual(len(log), 2)
        s = summarize(log)
        self.assertIn("tribute", s["by_kind"])
        self.assertIn("foreign_open", s["by_kind"])

    def test_jsonl_file(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "day.jsonl"
            p.write_text(json.dumps({
                "ts": "2026-09-20T00:00:00Z",
                "kind": "claim_skipped_closed",
                "issue": "https://github.com/a/b/issues/1",
                "ok": True,
                "lane": "help-wanted",
            }) + "\n", encoding="utf-8")
            log = build_log(load_receipts([p]))
            self.assertEqual(len(log), 1)


if __name__ == "__main__":
    unittest.main()
