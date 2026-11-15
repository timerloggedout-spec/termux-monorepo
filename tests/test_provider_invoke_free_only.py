"""No-cost provider model selection contract for QUE inference dispatch."""

from scripts.ops import provider_invoke as invoke


def row(model_id, **overrides):
    value = {
        "id": model_id,
        "pricing_classification": "unknown",
        "access_classification": "catalog_pricing_only",
        "entitlement_verification": "unknown",
        "free_suffix": False,
    }
    value.update(overrides)
    return value


def test_selects_zero_price_chat_model_without_requiring_provider_quota_counter():
    candidate = row(
        "daily-pool/free-chat",
        pricing_classification="free_zero_price",
        quota_class="daily_pool_no_provider_quota",
        pool_status="available",
    )
    assert invoke.select_free_chat_model([candidate]) == "daily-pool/free-chat"


def test_selects_openrouter_free_suffix_model():
    candidate = row("vendor/model:free", free_suffix=True)
    assert invoke.select_free_chat_model([candidate]) == "vendor/model:free"


def test_selects_free_trial_only_when_entitlement_is_verified():
    unverified = row(
        "trial/unverified",
        access_classification="free_trial",
        entitlement_verification="unknown",
    )
    verified = row(
        "trial/verified",
        access_classification="free_trial",
        entitlement_verification="verified",
    )
    assert invoke.select_free_chat_model([unverified, verified]) == "trial/verified"


def test_rejects_paid_unknown_and_non_chat_models():
    candidates = [
        row("paid/model", pricing_classification="paid"),
        row("unknown/model"),
        row("free/embed-model", pricing_classification="free_zero_price"),
        row("free/tts-model", free_suffix=True),
    ]
    assert invoke.select_free_chat_model(candidates) is None


def test_explicit_model_must_match_an_exact_verified_no_cost_chat_model():
    candidates = [
        row("free/model", pricing_classification="free_zero_price"),
        row("paid/model", pricing_classification="paid"),
    ]
    assert invoke.select_free_chat_model(candidates, "free/model") == "free/model"
    assert invoke.select_free_chat_model(candidates, "paid/model") is None
    assert invoke.select_free_chat_model(candidates, "free/mod") is None


def test_provider_invoke_workflow_defaults_to_free_only():
    from pathlib import Path
    import yaml

    root = Path(__file__).resolve().parents[1]
    workflow = yaml.safe_load((root / ".github/workflows/provider-invoke.yml").read_text())
    events = workflow.get("on", workflow.get(True))
    assert events["workflow_dispatch"]["inputs"]["free_only"]["default"] is True
    step = next(s for s in workflow["jobs"]["invoke"]["steps"] if s.get("id") == "invoke")
    assert "--free-only" in step["run"]
    assert "inputs.free_only" in step["run"]


def test_free_only_invokes_exactly_one_verified_no_cost_model(tmp_path, monkeypatch, capsys):
    import json
    import sys
    from scripts import provider_model_catalog

    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Return a one-word health acknowledgement.")
    output = tmp_path / "completion.txt"
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.delenv("INVOKE_MODEL", raising=False)
    monkeypatch.setattr(provider_model_catalog, "poll", lambda provider, token: ([
        row("free/chat", pricing_classification="free_zero_price"),
        row("paid/chat", pricing_classification="paid"),
    ], {}))
    calls = []

    def fake_http(method, url, token, payload=None, timeout=90):
        calls.append(payload)
        return 200, {"choices": [{"message": {"content": "OK"}}]}

    monkeypatch.setattr(invoke, "http_json", fake_http)
    monkeypatch.setattr(sys, "argv", [
        "provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt),
        "--out", str(output), "--free-only",
    ])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is True
    assert verdict["no_cost_verified"] is True
    assert verdict["model"] == "free/chat"
    assert len(calls) == 1
    assert calls[0]["model"] == "free/chat"
    assert calls[0]["max_tokens"] == 300
    assert output.read_text() == "OK"


def test_free_only_refuses_when_catalog_has_no_verified_no_cost_model(tmp_path, monkeypatch, capsys):
    import json
    import sys
    from scripts import provider_model_catalog

    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Do not execute.")
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.delenv("INVOKE_MODEL", raising=False)
    monkeypatch.setattr(provider_model_catalog, "poll", lambda provider, token: ([
        row("paid/chat", pricing_classification="paid"),
        row("unknown/chat"),
    ], {}))

    def forbidden_http(*args, **kwargs):
        raise AssertionError("free-only must not invoke when no no-cost model is verified")

    monkeypatch.setattr(invoke, "http_json", forbidden_http)
    monkeypatch.setattr(sys, "argv", [
        "provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt), "--free-only",
    ])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is False
    assert verdict["diagnosis"] == "no_verified_no_cost_chat_model"

def test_native_provider_validation_matrix_covers_every_manual_provider_with_free_only_gate():
    from pathlib import Path
    import yaml

    root = Path(__file__).resolve().parents[1]
    single = yaml.safe_load((root / ".github/workflows/provider-invoke.yml").read_text())
    batch = yaml.safe_load((root / ".github/workflows/provider-inference-validation.yml").read_text())
    single_events = single.get("on", single.get(True))
    batch_events = batch.get("on", batch.get(True))
    expected = set(single_events["workflow_dispatch"]["inputs"]["provider"]["options"])
    actual = set(batch["jobs"]["validate"]["strategy"]["matrix"]["provider"])
    assert actual == expected
    assert len(actual) == 30
    assert set(batch_events) == {"workflow_dispatch"}
    assert batch_events["workflow_dispatch"]["inputs"]["experiment_label"]["required"] is True
    assert batch_events["workflow_dispatch"]["inputs"]["emit_stamps"]["default"] is True
    assert batch["jobs"]["validate"]["strategy"]["max-parallel"] == 2
    assert batch["jobs"]["stamp"]["needs"] == ["validate"]
    assert "inputs.emit_stamps" in batch["jobs"]["stamp"]["if"]
    stamp_step = next(s for s in batch["jobs"]["stamp"]["steps"] if "provider_validation_stamp.py" in s.get("run", ""))
    assert "dispatch-stamp-fanout" in (root / "scripts/ops/provider_validation_stamp.py").read_text()
    assert "GH_TOKEN" in stamp_step["env"]
    step = next(s for s in batch["jobs"]["validate"]["steps"] if "scripts/ops/provider_invoke.py" in s.get("run", ""))
    assert "--free-only" in step["run"]
    assert "inference-health-smoke.md" in step["run"]
    upload = next(s for s in batch["jobs"]["validate"]["steps"] if "upload-artifact" in s.get("uses", ""))
    assert upload["with"]["path"] == "/tmp/receipt.json"
    assert "completion.txt" not in upload["with"]["path"]

def test_free_only_does_not_fallback_to_second_free_model_after_404(tmp_path, monkeypatch, capsys):
    import json
    import sys
    from scripts import provider_model_catalog

    prompt = tmp_path / "prompt.txt"
    prompt.write_text("Return a one-word health acknowledgement.")
    monkeypatch.setenv("GROQ_API_KEY", "fixture-secret")
    monkeypatch.delenv("INVOKE_MODEL", raising=False)
    monkeypatch.setattr(provider_model_catalog, "poll", lambda provider, token: ([
        row("free/chat-a", pricing_classification="free_zero_price"),
        row("free/chat-b", pricing_classification="free_zero_price"),
    ], {}))
    calls = []

    def fake_http(method, url, token, payload=None, timeout=90):
        calls.append(payload)
        return 404, {"error": "not served"}

    monkeypatch.setattr(invoke, "http_json", fake_http)
    monkeypatch.setattr(sys, "argv", [
        "provider_invoke.py", "--provider", "groq", "--prompt-file", str(prompt), "--free-only",
    ])
    assert invoke.main() == 0
    verdict = json.loads(capsys.readouterr().out.removeprefix("INVOKE_VERDICT "))
    assert verdict["ok"] is False
    assert verdict["model"] == "free/chat-a"
    assert len(calls) == 1
    assert calls[0]["model"] == "free/chat-a"