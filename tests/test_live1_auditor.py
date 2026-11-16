"""Tests for the live-1 ledger auditor (rule-5 automation, WO-B)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "live1_auditor", ROOT / "scripts/doe/live1_auditor.py")
AUD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUD)

SCHEMA = json.loads(
    (ROOT / "docs/ops/corpus/EXPERIMENT.schema.json").read_text())

LEDGER = [{"issue": 3001, "entry": "D2", "entry_class": "greenfield",
           "framing": "A-implement-only", "slot": 1},
          {"issue": 3002, "entry": "D2", "entry_class": "greenfield",
           "framing": "B+A-pack", "slot": 2}]

STAMP = ("<!-- live-1-wave-framing | framing: {f} | entry: {e} | "
         "entry_class: {c} | ledger slot: {s} -->")


def issue(num, body):
    return {"number": num, "title": "t", "body": body}


def test_designed_ok_and_record_valid():
    iss = issue(3001, "body " + STAMP.format(
        f="A-implement-only", e="D2", c="greenfield", s=1))
    res = AUD.audit(LEDGER, iss)
    assert res["verdict"] == "designed_ok"
    rec = AUD.build_record(iss, res, "a" * 40, "2026-11-03T00:00:00Z")
    jsonschema.validate(rec, SCHEMA)
    assert rec["status"] == "passed" and rec["outcome"] == "designed_ok"


def test_framing_mismatch_is_observational():
    iss = issue(3001, STAMP.format(
        f="B+A-pack", e="D2", c="greenfield", s=1))
    res = AUD.audit(LEDGER, iss)
    assert res["verdict"] == "observational"
    assert res["checks"]["framing_matches"] is False
    rec = AUD.build_record(iss, res, "a" * 40, "2026-11-03T00:00:00Z")
    jsonschema.validate(rec, SCHEMA)
    assert rec["status"] == "observed"
    assert "framing_matches" in rec["metrics"]["checks_failed"]


def test_missing_ledger_line_is_observational():
    iss = issue(3999, STAMP.format(
        f="A-implement-only", e="D2", c="greenfield", s=1))
    res = AUD.audit(LEDGER, iss)
    assert res["verdict"] == "observational"
    assert res["checks"]["ledger_line_exists"] is False


def test_missing_stamp_is_observational():
    res = AUD.audit(LEDGER, issue(3002, "no stamp here"))
    assert res["verdict"] == "observational"
    assert res["checks"]["stamp_present"] is False


def test_slot_mismatch_is_observational():
    iss = issue(3002, STAMP.format(
        f="B+A-pack", e="D2", c="greenfield", s=1))
    res = AUD.audit(LEDGER, iss)
    assert res["verdict"] == "observational"
    assert res["checks"]["slot_matches"] is False
