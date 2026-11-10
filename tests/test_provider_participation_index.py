import json
from pathlib import Path
import pytest
from scripts.provider_participation_index import build

def write(root: Path, rel: str, data: dict):
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data),encoding="utf-8")

def fixture(root: Path):
    write(root,"ops/quota/registry.json",{"services":[{"id":"deepseek.api","provider":"DeepSeek","lane":"model","live":"provider-invoke","limit":None},{"id":"agentrouter.models","provider":"agentrouter","lane":"model","live":"GET /v1/models"},{"id":"unmapped.models","provider":"unmapped","lane":"model"}]})
    write(root,"ops/challenge/desk-feed.json",{"dispatch":{"provider_catalog":{"rotation_rule":{"rule":"task fit"},"inference_availability":{"records":[{"id":"deepseek.api","provider":"DeepSeek","class":"proven","availability_probe":"not-covered","inference_route":["provider-invoke"]},{"id":"agentrouter.models","provider":"agentrouter","class":"catalog-only","availability_probe":"authenticated-catalog","inference_route":[]}]}}}})
    write(root,"ops/tracking/nested-family.json",{"providers":[{"provider":"deepseek","models":[{"model":"deepseek-chat","roles":["builder"],"tasks":[{"role":"builder","task_class":"inference-invoke","source_ref":"records/run.json","run_id":42,"outcome":{"status":"passed"}}]},{"model":"NOT ESTABLISHED","roles":["reviewer"],"tasks":[]}]}]})
    write(root,"experiments/doe/util-1-provider-rotation/DESIGN.json",{"campaign_id":"util-1-provider-rotation","status":"admitted_implementing","design":{"assignment":"desk","window_rule":"24 stamps"},"conditional_provider_arms":[{"provider":"agentrouter","status":"pre_registered_conditional_not_dispatchable","protocols":["openai-compatible"],"activation_gates":["approval"]}]})

def test_exhaustive_and_separates_evidence(tmp_path):
    fixture(tmp_path);d=build(tmp_path,"2026-11-10T00:00:00Z")
    assert d["summary"]["registry_model_records"]==3
    assert d["summary"]["dispatch_mapped_records"]==2
    assert d["summary"]["dispatch_unmapped_records"]==1
    rows={r["id"]:r for r in d["records"]}
    assert rows["deepseek.api"]["inference_dispatchable"] is True
    assert rows["deepseek.api"]["invocation_proofs"][0]["run_id"]==42
    assert rows["deepseek.api"]["observed_roles"]==["builder","reviewer"]
    assert rows["agentrouter.models"]["dispatch_class"]=="catalog-only"
    assert rows["agentrouter.models"]["inference_dispatchable"] is False
    assert rows["agentrouter.models"]["free_eligibility"] is None
    assert rows["unmapped.models"]["dispatch_mapping_status"]=="unmapped"
    assert rows["deepseek.api"]["quota"]["limit"] is None

def test_unknown_model_label_is_not_identity(tmp_path):
    fixture(tmp_path);d=build(tmp_path)
    row=next(r for r in d["records"] if r["id"]=="deepseek.api")
    assert row["observed_models"]==["deepseek-chat"]

def test_duplicate_dispatch_ids_fail_closed(tmp_path):
    fixture(tmp_path);p=tmp_path/"ops/challenge/desk-feed.json";d=json.loads(p.read_text())
    rows=d["dispatch"]["provider_catalog"]["inference_availability"]["records"];rows.append(dict(rows[0]));p.write_text(json.dumps(d))
    with pytest.raises(ValueError,match="duplicate dispatch record"):build(tmp_path)
