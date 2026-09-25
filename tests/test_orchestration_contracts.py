import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_schema(name: str) -> dict:
    return json.loads((ROOT / "docs" / "ops" / name).read_text())


def test_treatment_schema_is_strict_and_separates_lifecycle():
    schema = load_schema("ORCHESTRATION-TREATMENT.schema.json")
    assert schema["additionalProperties"] is False
    assert schema["properties"]["status"]["enum"] == [
        "candidate", "experimental", "accepted", "deprecated", "rejected"
    ]
    assert "wait_policy" in schema["required"]
    assert "evidence_contract" in schema["required"]


def test_receipt_schema_separates_state_outcome_and_promotion():
    schema = load_schema("ORCHESTRATION-RECEIPT.schema.json")
    props = schema["properties"]
    assert props["state"]["enum"] == [
        "DISPATCHED", "QUEUED", "RUNNING", "WAITING", "STEERED",
        "RETRYING", "COMPLETED", "FAILED", "CANCELLED"
    ]
    assert props["outcome"]["enum"] == ["TASK_PASS", "TASK_FAIL", "UNKNOWN"]
    assert props["promotion"]["enum"] == [
        "PROMOTABLE", "NOT_PROMOTABLE", "UNKNOWN"
    ]
    assert all(key in schema["required"] for key in (
        "orchestration_id", "cycle_id", "attempt_id", "action_id",
        "event_id", "repo", "ref", "sha", "evidence_ids"
    ))


def test_existing_contracts_remain_referenced_not_replaced():
    skill = (ROOT / ".agents" / "skills" / "orchestration-treatment-registry" / "SKILL.md").read_text()
    assert "EVIDENCE-ENVELOPE.schema.json" in skill
    assert "ACTION-EFFECT-EVENT.schema.json" in skill
    assert "adaptive-wait" in skill
    assert "context-relationship-graph" in skill
