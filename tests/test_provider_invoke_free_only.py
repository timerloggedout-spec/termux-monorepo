"""Policy-gated no-cost provider inference contract for QUE."""

import json
import sys
from pathlib import Path

import yaml

from scripts import provider_model_catalog
from scripts.ops import provider_invoke as invoke
from scripts.ops.provider_population_census import build_census
from llm_api_hub.server import research_providers


def row(model_id, **overrides):
    value = {"id": model_id, "pricing_classification": "unknown",
             "access_classification": "catalog_pricing_only", "entitlement_verification": "unknown",
             "free_suffix": False}
    value.update(overrides)
    return value


def policy_entry(**overrides):
    value = {
        "provider": "groq", "model": "free/chat", "free_account_verified": True,
        "terms_accepted": True, "data_class": "public", "expires_at": "2099-01-01T00:00:00Z",
        "no_cost_verified": True, "pricing_source": "https://provider.example/pricing",
        "pricing_verified_at": "2026-11-15T12:00:00Z", "terms_source": "https://provider.example/terms",
        "terms_verified_at": "2026-11-15T12:00:00Z", "capability_source": "https://provider.example/models",
        "capability_verified_at": "2026-11-15T12:00:00Z", "quota_class": "daily_pool_no_provider_quota",
        "pool_id": "daily-free-inference", "pool_evidence_ref": "https://provider.example/free-pool"}
    value.update(overrides)
    return value


def test_selects_zero_price_chat_model_without_provider_quota_counter():
    candidate = row("daily-pool/free-chat", pricing_classification="free_zero_price",
                    quota_class="daily_pool_no_provider_quota", pool_status="available")
    assert invoke.select_free_chat_model([candidate]) == "daily-pool/free-chat"


def test_free_suffix_alone_is_not_no_cost_evidence():
    assert invoke.select_free_chat_model([row("vendor/model:free", free_suffix=True)]) is None


def test_selects_free_trial_only_when_entitlement_is_verified():
    unverified = row("trial/unverified", access_classification="free_trial", entitlement_verification="unknown")
    verified = row("trial/verified", access_classification="free_trial", entitlement_verification="verified")
    assert invoke.select_free_chat_model([unverified, verified]) == "trial/verified"


def test_rejects_paid_unknown_and_non_chat_models():
    candidates = [row("paid/model", pricing_classification="paid"), row("unknown/model"),
                  row("free/embed-model", pricing_classification="free_zero_price"),
                  row("free/tts-model", free_suffix=True)]
    assert invoke.select_free_chat_model(candidates) is None


def test_explicit_model_must_match_an_exact_verified_no_cost_chat_model():
    candidates = [row("free/model", pricing_classification="free_zero_price"), row("paid/model", pricing_classification="paid")]
    assert invoke.select_free_chat_model(candidates, "free/model") == "free/model"
    assert invoke.select_free_chat_model(candidates, "paid/model") is None
    assert invoke.select_free_chat_model(candidates, "free/mod") is None


def test_daily_pool_policy_requires_pool_evidence():
    assert research_providers.validate_activation_entry(policy_entry()) is None
    assert research_providers.validate_activation_entry(policy_entry(pool_evidence_ref="")) == "policy_daily_pool_evidence_missing"


def test_provider_invoke_workflow_defaults_to_policy_gated_free_only():
    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/provider-invoke.yml").read_text())
    events = workflow.get("on", workflow.get(True))
    assert events["workflow_dispatch"]["inputs"]["free_only"]["default"] is True
    assert events["workflow_dispatch"]["inputs"]["emit_stamps"]["default"] is False
    steps = workflow["jobs"]["invoke"]["steps"]
    policy_step = next(step for step in steps if "provider-admission.json" in step.get("run", ""))
    assert "LLM_API_HUB_PROVIDER_POLICY_JSON" in policy_step["env"]
    invoke_step = next(step for step in steps if "scripts/ops/provider_invoke.py" in step.get("run", ""))
    assert "inference-health-smoke.md" in invoke_step["run"] and "--free-only" in invoke_step["run"] and "--max-tokens 16" in invoke_step["run"]
    assert "OLLAMA_API_KEY" in invoke_step["env"]
    assert "inference-batch-ww3.md" not in invoke_step["run"]
    assert "issues: write" not in (root / ".github/workflows/provider-invoke.yml").read_text()


def test_free_only_invokes_exact_policy_admitted_zero_price_model(tmp_path, monkeypatch, capsys):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Return a one-word health acknowledgement.")
    output = tmp_path / "completion.txt"
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.setattr(research_providers, "admitted_models", lambda: ["groq/free/chat"])
    monkeypatch.setattr(research_providers, "admission_entry", lambda provider, model: policy_entry(model=model))
    monkeypatch.setattr(provider_model_catalog, "poll", lambda provider, token: ([
        row("free/chat", pricing_classification="free_zero_price"), row("paid/chat", pricing_classification="paid")], {}))
    calls = []
    def fake_complete(provider, model, payload, timeout):
        calls.append((provider, model, payload, timeout))
        return {"choices": [{"message": {"content": "OK"}}], "usage": {"prompt_tokens": 1, "completion_tokens": 1}}
    monkeypatch.setattr(research_providers, "complete", fake_complete)
    monkeypatch.setattr(sys, "argv", ["provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt),
        "--out", str(output), "--free-only"])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is True and verdict["no_cost_verified"] is True
    assert verdict["policy_admitted"] is True and verdict["terms_accepted"] == "policy_asserted"
    assert verdict["entitlement_verified"] == "policy_asserted" and verdict["dispatch_eligible"] is False
    assert verdict["quota_class"] == "daily_pool_no_provider_quota" and verdict["pool_id"] == "daily-free-inference"
    assert verdict["model"] == "free/chat" and len(calls) == 1 and calls[0][1] == "free/chat"
    assert calls[0][2]["max_tokens"] == 300 and output.read_text() == "OK"


def test_policy_missing_defers_without_catalog_or_inference(tmp_path, monkeypatch, capsys):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Do not execute.")
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.setattr(research_providers, "admitted_models", lambda: [])
    monkeypatch.setattr(provider_model_catalog, "poll", lambda *a, **k: (_ for _ in ()).throw(AssertionError("catalog must not be polled")))
    monkeypatch.setattr(sys, "argv", ["provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt), "--free-only"])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is False and verdict["diagnosis"] == "provider_model_not_admitted"


def test_policy_evidence_incomplete_defers_without_inference(tmp_path, monkeypatch, capsys):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Do not execute.")
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.setattr(research_providers, "admitted_models", lambda: ["groq/free/chat"])
    monkeypatch.setattr(research_providers, "admission_entry", lambda provider, model: policy_entry(model=model, no_cost_verified=False))
    monkeypatch.setattr(provider_model_catalog, "poll", lambda provider, token: ([row("free/chat", pricing_classification="free_zero_price")], {}))
    monkeypatch.setattr(research_providers, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("inference must not run")))
    monkeypatch.setattr(sys, "argv", ["provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt), "--free-only"])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is False and verdict["diagnosis"] == "policy_no_cost_not_verified"


def test_free_only_does_not_fallback_to_second_free_model_after_failure(tmp_path, monkeypatch, capsys):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Return a one-word health acknowledgement.")
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.setattr(research_providers, "admitted_models", lambda: ["groq/free/chat-a", "groq/free/chat-b"])
    monkeypatch.setattr(research_providers, "admission_entry", lambda provider, model: policy_entry(model=model))
    monkeypatch.setattr(provider_model_catalog, "poll", lambda provider, token: ([
        row("free/chat-a", pricing_classification="free_zero_price"), row("free/chat-b", pricing_classification="free_zero_price")], {}))
    calls = []
    def fail_once(provider, model, payload, timeout):
        calls.append(model)
        raise research_providers.ProviderAdmissionError(404, "not served", "upstream_error")
    monkeypatch.setattr(research_providers, "complete", fail_once)
    monkeypatch.setattr(sys, "argv", ["provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt), "--free-only"])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is False and verdict["model"] == "free/chat-a"
    assert calls == ["free/chat-a"]


def test_non_free_only_invocation_fails_closed(tmp_path, monkeypatch, capsys):
    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Do not execute.")
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.setattr(research_providers, "admitted_models", lambda: (_ for _ in ()).throw(AssertionError("policy should not be read")))
    monkeypatch.setattr(sys, "argv", ["provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt)])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["diagnosis"] == "free_only_required"


def test_native_provider_validation_matrix_is_policy_gated_and_bounded():
    root = Path(__file__).resolve().parents[1]
    single = yaml.safe_load((root / ".github/workflows/provider-invoke.yml").read_text())
    batch = yaml.safe_load((root / ".github/workflows/provider-inference-validation.yml").read_text())
    single_events = single.get("on", single.get(True))
    batch_events = batch.get("on", batch.get(True))
    assert len(single_events["workflow_dispatch"]["inputs"]["provider"]["options"]) == 31
    assert {"ollama", "felo", "omni"} <= set(single_events["workflow_dispatch"]["inputs"]["provider"]["options"])
    discover = batch["jobs"]["discover"]
    assert discover["outputs"]["providers"] == "${{ steps.matrix.outputs.providers }}"
    matrix_step = next(step for step in discover["steps"] if "provider_population_census.py" in step.get("run", ""))
    assert "native_provider_ids" in (root / "scripts/ops/provider_population_census.py").read_text()
    assert "GITHUB_OUTPUT" in matrix_step["run"]
    census = build_census(root)
    native_ids = set(census["adapter_population"]["native_provider_ids"])
    assert native_ids == set(research_providers.ENDPOINTS)
    assert "ollama" in native_ids and "felo" not in native_ids and "omni" not in native_ids
    assert batch["jobs"]["validate"]["needs"] == ["discover"]
    assert batch["jobs"]["validate"]["strategy"]["matrix"]["provider"] == "${{ fromJson(needs.discover.outputs.providers) }}"
    assert batch["jobs"]["validate"]["strategy"]["max-parallel"] == 2
    assert set(batch_events) == {"workflow_dispatch"}
    assert batch_events["workflow_dispatch"]["inputs"]["experiment_label"]["required"] is True
    assert batch_events["workflow_dispatch"]["inputs"]["emit_stamps"]["default"] is False
    policy_step = next(step for step in batch["jobs"]["validate"]["steps"] if "provider-admission.json" in step.get("run", ""))
    assert "LLM_API_HUB_PROVIDER_POLICY_JSON" in policy_step["env"]
    invoke_step = next(step for step in batch["jobs"]["validate"]["steps"] if "scripts/ops/provider_invoke.py" in step.get("run", ""))
    assert "--free-only" in invoke_step["run"] and "inference-health-smoke.md" in invoke_step["run"] and "--max-tokens 16" in invoke_step["run"]
    assert "'dispatch_eligible': False" in invoke_step["run"]
    assert "OLLAMA_API_KEY" in invoke_step["env"]
    census_job = batch["jobs"]["census"]
    assert census_job["needs"] == ["discover", "validate"]
    assert any("provider-population-census" in step.get("with", {}).get("name", "") for step in census_job["steps"])
    stamp_job = batch["jobs"]["stamp"]
    assert stamp_job["needs"] == ["discover", "validate"] and "inputs.emit_stamps" in stamp_job["if"] and "needs.discover.result == 'success'" in stamp_job["if"]
    stamp_step = next(step for step in stamp_job["steps"] if "provider_validation_stamp.py" in step.get("run", ""))
    assert "GH_TOKEN" in stamp_step["env"]
    assert "dispatch-stamp-fanout" in (root / "scripts/ops/provider_validation_stamp.py").read_text()
    upload = next(step for step in batch["jobs"]["validate"]["steps"] if "upload-artifact" in step.get("uses", ""))
    assert upload["with"]["path"] == "/tmp/receipt.json"
