import json
from pathlib import Path

import pytest

from scripts.prepool_cohort_adapter import build_prepool_cohort


def fixture_registry(count=2):
    services = [
        {"id": f"service.{index:03d}", "provider": f"provider-{index:03d}", "limit": None}
        for index in range(count)
    ]
    return {"schema": "quota.registry.v2", "services": services}


def fixture_decision(record_id):
    return {
        "record_id": record_id,
        "eligible": True,
        "evidence_ref": f"fixture://prepool-adapter/{record_id}",
        "source": "synthetic-test-fixture",
    }


def test_canonical_172_record_registry_round_trips_with_explicit_test_fixture():
    registry_path = Path(__file__).resolve().parents[1] / "ops" / "quota" / "registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    services = registry["services"]
    assert registry["schema"] == "quota.registry.v2"
    assert len(services) == 172
    assert len({row["id"] for row in services}) == 172

    # This is interface-test input only, not output from the authoritative gate.
    gate_output = {"decisions": [fixture_decision(row["id"]) for row in services]}
    result = build_prepool_cohort(registry, gate_output)

    ids = [row["id"] for row in services]
    assert result["registry_schema"] == "quota.registry.v2"
    assert result["gate_decisions_complete"] is True
    assert result["gate_evidence_refs_complete"] is True
    assert [row["record_id"] for row in result["records"]] == ids
    assert [row["registry_record"] for row in result["records"]] == services
    assert result["planned_cohort_ids"] == ids
    assert all(row["gate_decision"]["evidence_ref"].startswith("fixture://") for row in result["records"])
    assert "provider_mapping" not in result and "queue" not in result


def test_gate_decisions_and_evidence_are_preserved_without_reinterpretation():
    registry = fixture_registry()
    decision = fixture_decision("service.000")
    decision["evidence"] = {"sha256": "test-only"}
    output = build_prepool_cohort(
        registry,
        {"decisions": [decision, fixture_decision("service.001")]},
    )
    assert output["records"][0]["gate_decision"] == decision
    assert output["planned_cohort_ids"] == ["service.000", "service.001"]


@pytest.mark.parametrize("gate_output, error", [
    (None, "missing_gate_decisions"),
    ({}, "missing_gate_decisions"),
    ({"decisions": []}, "incomplete_gate_decisions"),
    ({"decisions": [fixture_decision("service.000")]}, "incomplete_gate_decisions"),
    ({"decisions": [fixture_decision("unknown")]}, "unknown_gate_record_id"),
    ({"decisions": [fixture_decision("service.000"), fixture_decision("service.000")]}, "duplicate_gate_record_id"),
    ({"decisions": [{**fixture_decision("service.000"), "eligible": "yes"}]}, "invalid_gate_eligibility"),
    ({"decisions": [{"record_id": "service.000", "eligible": True}]}, "invalid_gate_evidence_ref"),
    ({"decisions": [{**fixture_decision("service.000"), "evidence_ref": "  "}]}, "invalid_gate_evidence_ref"),
])
def test_incomplete_ambiguous_or_unreferenced_gate_output_fails_closed(gate_output, error):
    with pytest.raises(ValueError, match=error):
        build_prepool_cohort(fixture_registry(), gate_output)


def test_registry_with_duplicate_ids_fails_closed():
    registry = fixture_registry()
    registry["services"][1]["id"] = registry["services"][0]["id"]
    with pytest.raises(ValueError, match="duplicate_registry_record_id"):
        build_prepool_cohort(registry, {"decisions": []})
