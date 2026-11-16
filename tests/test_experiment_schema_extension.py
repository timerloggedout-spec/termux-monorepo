"""EXPERIMENT.schema.json rev 1.1 — additive extension proof.

Ruling (doe-expert, on the Viz schema question): optional slots
{session_id, window, usage{value, unit, source, match, status}}
(readings-row shape); additive minor bump; every existing record
validates UNCHANGED; usage carries a value only when measured;
the slots are not configured-instance identity fields.

Proof obligations encoded here:
1. For every experiments/doe/*/records/*.json in the tree, the
   validation verdict under the rev-1.0 schema (vendored fixture)
   equals the verdict under the current schema — including the
   pilot-1 records (conform in both) and live-3 dispatch-0001
   (campaign-native; non-conform in both).
2. The new slots accept their lawful shapes and reject unlawful
   ones (bad status, value present while activity_only /
   not_established, unknown keys).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

ROOT = Path(__file__).resolve().parents[1]
NEW = json.loads((ROOT / "docs/ops/corpus/EXPERIMENT.schema.json")
                 .read_text())
OLD = json.loads((Path(__file__).parent / "fixtures" /
                  "EXPERIMENT.schema.v1.0.json").read_text())
RECORDS = sorted((ROOT / "experiments/doe").glob("*/records/*.json"))


def verdict(schema, rec) -> bool:
    try:
        jsonschema.validate(rec, schema)
        return True
    except Exception:
        return False


def test_every_landed_record_verdict_unchanged():
    assert RECORDS, "no doe records found"
    changed = []
    for path in RECORDS:
        rec = json.loads(path.read_text())
        if verdict(OLD, rec) != verdict(NEW, rec):
            changed.append(str(path.relative_to(ROOT)))
    assert changed == [], f"verdict changed for: {changed}"


def _pilot_base():
    for path in RECORDS:
        if "pilot-1" in path.name or "pilot-1" in str(path):
            rec = json.loads(path.read_text())
            if verdict(NEW, rec):
                return rec
    raise AssertionError("no conforming pilot-1 record found")


def test_new_slots_accepted_on_a_conforming_record():
    rec = copy.deepcopy(_pilot_base())
    rec["session_id"] = "sess-123"
    rec["window"] = {"start": "2026-11-03T00:00:00Z",
                     "end": "2026-11-03T01:00:00Z"}
    rec["usage"] = {"value": 1234, "unit": "tokens",
                    "source": "openrouter/usage",
                    "match": "exact", "status": "measured"}
    assert verdict(NEW, rec)


def test_usage_value_only_when_measured():
    base = _pilot_base()
    for status in ("activity_only", "not_established"):
        rec = copy.deepcopy(base)
        rec["usage"] = {"value": 5, "unit": "tokens",
                        "source": "x", "match": None,
                        "status": status}
        assert not verdict(NEW, rec), status
        rec["usage"]["value"] = None
        assert verdict(NEW, rec), status
    rec = copy.deepcopy(base)
    rec["usage"] = {"value": 5, "unit": None, "source": None,
                    "match": None, "status": "estimated"}
    assert verdict(NEW, rec)


def test_usage_status_vocab_and_shape_closed():
    base = _pilot_base()
    rec = copy.deepcopy(base)
    rec["usage"] = {"value": None, "status": "guessed"}
    assert not verdict(NEW, rec)
    rec = copy.deepcopy(base)
    rec["usage"] = {"value": None, "status": "measured", "zz": 1}
    assert not verdict(NEW, rec)
    rec = copy.deepcopy(base)
    rec["bogus_top_level"] = 1
    assert not verdict(NEW, rec)
