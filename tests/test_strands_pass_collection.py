"""Strands pass — collection-first variant suites (ITEMS-003, E-06)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from scripts.delphi.ballot_collector import collect  # noqa: E402

HUMAN = {"voter": "registrar:owner", "source_class": "HUMAN_COLLABORATOR",
         "scores": {"a": 20, "b": 12}}
MODEL = {"voter": "provider-runner", "source_class": "MODEL_PROVIDER",
         "run": {"provider": "fixture", "model": "fixture/1", "run_id": "fx-1",
                 "response_hash": "0" * 8, "entitlement": "fixture"},
         "scores": {"a": 18, "b": 15}}


def test_collector_intake_validation():
    receipt = collect([HUMAN, MODEL])
    assert receipt["accepted"] == 2
    try:
        collect([{"voter": "x", "source_class": "MODEL_PROVIDER",
                  "scores": {"a": 1}}])
    except ValueError:
        return
    raise AssertionError("a model ballot without its run record must be refused")


def test_collector_dedupe():
    try:
        collect([MODEL, dict(MODEL)])
    except ValueError as exc:
        assert "duplicate" in str(exc)
        return
    raise AssertionError("duplicate ballots must be refused at intake")


def test_e06_receipt_completeness():
    receipt = collect([HUMAN, MODEL])
    assert receipt["reconstruction_check"] is True
    assert receipt["per_class"] == {"HUMAN_COLLABORATOR": 1,
                                    "MODEL_PROVIDER": 1,
                                    "LOCAL_BASELINE": 0}
    assert len(receipt["ballot_hashes"]) == 2
