import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "que"))

from sie_pipeline import (
    StageValidationError, build_receipt, item_key, next_stage,
    stable_event_id, validate_receipt, validate_transition,
)


def receipt(stage="OBSERVE", state="COMPLETED", **kwargs):
    return build_receipt(
        source_kind="workflow_run", source_id="123",
        source_revision="a" * 40, failure_class="ci",
        stage=stage, state=state, sha="a" * 40,
        observed_at="2026-11-13T00:00:00Z", **kwargs,
    )


def test_event_identity_is_deterministic_and_revision_sensitive():
    a = stable_event_id("workflow_run", "123", "a" * 40)
    assert a == stable_event_id("workflow_run", "123", "a" * 40)
    assert a != stable_event_id("workflow_run", "123", "b" * 40)


def test_item_identity_groups_repeated_failure_observations():
    assert item_key("workflow_run", "build.yml", "lint") == item_key("workflow_run", "build.yml", "lint")
    assert item_key("workflow_run", "build.yml", "lint") != item_key("workflow_run", "build.yml", "test")


def test_receipt_is_valid_and_evidence_refs_are_canonical():
    r = receipt(evidence_refs=["run:2", "sha:a", "run:2"])
    assert validate_receipt(r) == []
    assert r["evidence_refs"] == ["run:2", "sha:a"]


def test_receipt_rejects_invalid_sha_and_source():
    r = receipt()
    r["sha"] = "bad"
    r["source"]["kind"] = "mystery"
    errors = validate_receipt(r)
    assert any("sha:" in e for e in errors)
    assert any("source.kind:" in e for e in errors)


def test_lifecycle_order_is_linear_and_complete():
    assert next_stage("OBSERVE") == "TRIAGE"
    assert next_stage("DELPHI") == "DESIGN"
    assert next_stage("LEARN") is None
    try:
        next_stage("UNKNOWN")
    except StageValidationError:
        pass
    else:
        raise AssertionError("unknown stage must fail")


def test_transition_preserves_identity_and_advances_one_stage():
    before = receipt("OBSERVE", "COMPLETED")
    after = receipt("TRIAGE", "READY")
    assert validate_transition(before, after) == []


def test_transition_rejects_stage_skip_and_identity_drift():
    before = receipt("OBSERVE", "COMPLETED")
    skipped = receipt("RESEARCH", "READY")
    changed = receipt("TRIAGE", "READY", source_id="999")
    assert any("advance exactly one stage" in e for e in validate_transition(before, skipped))
    assert any("item_key" in e for e in validate_transition(before, changed))


def test_blocked_stage_resumes_in_place():
    before = receipt("RESEARCH", "BLOCKED")
    resumed = receipt("RESEARCH", "READY")
    assert validate_transition(before, resumed) == []


def test_terminal_lineage_requires_new_item():
    before = receipt("LEARN", "REJECTED")
    after = receipt("OBSERVE", "READY")
    assert any("terminal lineage" in e for e in validate_transition(before, after))
