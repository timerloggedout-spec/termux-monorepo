import json
from pathlib import Path
import pytest
from scripts.provider_participation_index import build

def write(root: Path, rel: str, data: dict):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")

def fixture(root: Path):
    write(root, "ops/quota/registry.json", {"services": [
        {"id":"deepseek.api","provider":"DeepSeek","lane":"model","live":"provider-invoke","limit":None},
        {"id":"deepseek.chat","provider":"DeepSeek","lane":"model","live":"provider-invoke","limit":None},
        {"id":"agentrouter.models","provider":"agentrouter","lane":"model","live":"GET /v1/models"},
        {"id":"unmapped.models","provider":"unmapped","lane":"model"}
    ]})
    write(root, "ops/challenge/desk-feed.json", {"dispatch":{"provider_catalog":{
        "rotation_rule":{"rule":"task fit"},"inference_availability":{"records":[
            {"id":"deepseek.api","provider":"DeepSeek","class":"proven","availability_probe":"not-covered","inference_route":["provider-invoke"]},
            {"id":"deepseek.chat","provider":"DeepSeek","class":"proven","availability_probe":"not-covered","inference_route":["provider-invoke"]},
            {"id":"agentrouter.models","provider":"agentrouter","class":"catalog-only","availability_probe":"authenticated-catalog","inference_route":[]}
        ]}}}})
    write(root, "ops/tracking/nested-family.json", {"providers":[{"provider":"deepseek","models":[
        {"model":"deepseek-chat","roles":["builder"],"tasks":[{"role":"builder","task_class":"inference-invoke","source_ref":"records/run.json","run_id":42,"outcome":{"status":"passed"}}]},
        {"model":"NOT ESTABLISHED","roles":["reviewer"],"tasks":[]}
    ]}]})
    write(root, "experiments/doe/util-1-provider-rotation/DESIGN.json", {
        "campaign_id":"util-1-provider-rotation","status":"admitted_implementing",
        "design":{"assignment":"desk","window_rule":"24 stamps"},
        "conditional_provider_arms":[{"provider":"agentrouter","status":"pre_registered_conditional_not_dispatchable","protocols":["openai-compatible"],"activation_gates":["approval"]}]
    })

def test_exhaustive_and_separates_evidence(tmp_path):
    fixture(tmp_path)
    doc = build(tmp_path, "2026-11-10T00:00:00Z")
    assert doc["summary"]["registry_model_records"] == 4
    assert doc["summary"]["dispatch_mapped_records"] == 3
    assert doc["summary"]["dispatch_unmapped_records"] == 1
    records = {row["id"]: row for row in doc["records"]}
    providers = {row["provider"].casefold(): row for row in doc["providers"]}
    assert records["deepseek.api"]["inference_dispatchable"] is True
    assert records["deepseek.api"]["participation"]["inference_invocations_passed"] == 1
    assert providers["deepseek"]["record_count"] == 2
    assert providers["deepseek"]["task_count"] == 1
    assert providers["deepseek"]["inference_invocations_passed"] == 1
    assert len(providers["deepseek"]["participation_evidence"]) == 1
    assert len(providers["deepseek"]["invocation_proofs"]) == 1
    assert providers["deepseek"]["invocation_proofs"][0]["run_id"] == 42
    assert records["deepseek.api"]["observed_roles"] == ["builder", "reviewer"]
    assert records["agentrouter.models"]["dispatch_class"] == "catalog-only"
    assert records["agentrouter.models"]["inference_dispatchable"] is False
    assert records["agentrouter.models"]["free_eligibility"] is None
    assert records["agentrouter.models"]["free_tier_claim_text_present"] is False
    assert records["unmapped.models"]["dispatch_mapping_status"] == "unmapped"
    assert records["deepseek.api"]["quota"]["limit"] is None

def test_unknown_model_label_is_not_identity(tmp_path):
    fixture(tmp_path)
    doc = build(tmp_path)
    deepseek = next(row for row in doc["providers"] if row["provider"].casefold() == "deepseek")
    assert deepseek["observed_models"] == ["deepseek-chat"]

def test_duplicate_dispatch_ids_fail_closed(tmp_path):
    fixture(tmp_path)
    path = tmp_path / "ops/challenge/desk-feed.json"
    desk = json.loads(path.read_text(encoding="utf-8"))
    rows = desk["dispatch"]["provider_catalog"]["inference_availability"]["records"]
    rows.append(dict(rows[0]))
    path.write_text(json.dumps(desk), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate dispatch record"):
        build(tmp_path)


def test_free_tier_claim_text_never_establishes_eligibility(tmp_path):
    fixture(tmp_path)
    path = tmp_path / "ops/quota/registry.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["services"][0]["planned_use"] = {"note": "Public free-tier model listing"}
    path.write_text(json.dumps(data), encoding="utf-8")
    doc = build(tmp_path)
    row = next(r for r in doc["records"] if r["id"] == "deepseek.api")
    assert row["free_tier_claim_text_present"] is True
    assert row["free_eligibility"] is None
    assert doc["summary"]["records_mentioning_free_tier_claim_text"] == 1
