"""Offline synthetic-only Gemini preflight and active-router boundary tests."""
import copy
import datetime as dt
import json
from pathlib import Path
import socket
from zoneinfo import ZoneInfo

import pytest

from scripts import gemini_quota_gate as gate
from scripts import model_router as router
from scripts.gemini_shared_cap import check_cap

UTC = dt.timezone.utc
NOW = dt.datetime(2030, 3, 10, 12, tzinfo=UTC)
MODEL = "gemini-offline-fixture"


def day_window():
    pacific = ZoneInfo("America/Los_Angeles")
    day = NOW.astimezone(pacific).date()
    return {"kind": "pacific_day",
            "start": dt.datetime.combine(day, dt.time(), pacific).isoformat(),
            "end": dt.datetime.combine(day + dt.timedelta(days=1), dt.time(), pacific).isoformat()}


def policy():
    return {"schema": "gemini-shared-cap-policy/v1", "cap_kind": "operator_configured",
            "scope_alias": "offline-aggregate", "limit": 2, "pacific_day": "2030-03-10",
            "expires_at": day_window()["end"],
            "credentials": {"primary": {"project_alias": "offline-project-a"},
                            "backup": {"project_alias": "offline-project-b"}}}


def evidence(credential="primary", model=MODEL):
    minute = {"kind": "explicit", "start": (NOW - dt.timedelta(seconds=30)).isoformat(),
              "end": (NOW + dt.timedelta(seconds=30)).isoformat()}
    return {"source_kind": "aistudio_project_quota", "project_alias": policy()["credentials"][credential]["project_alias"],
            "credential_alias": credential, "model": model, "tier": "tier_1", "entitlement": "eligible",
            "observed_at": NOW.isoformat(), "dimensions": {
                "rpm": {"limit": 10, "used": 0, "remaining": 10, "window": minute},
                "input_tpm": {"limit": 100, "used": 0, "remaining": 100, "window": minute},
                "rpd": {"limit": 1000, "used": 0, "remaining": 1000, "window": day_window()}}}


def private_file(path, data):
    path.write_text(json.dumps(data))
    path.chmod(0o600)
    return str(path)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def fail(*args, **kwargs):
        pytest.fail("network/inference forbidden in offline quota regressions")
    monkeypatch.setattr(socket, "create_connection", fail)
    monkeypatch.setattr(socket.socket, "connect", fail)


def run_gate(tmp_path, raw=None, configured=None, credential="primary", model=MODEL):
    return gate.preflight(model=model, credential=credential,
                          policy_path=private_file(tmp_path / "policy.json", policy() if configured is None else configured),
                          evidence_path=private_file(tmp_path / "evidence.json", evidence(credential, model) if raw is None else raw),
                          ledger_dir=str(tmp_path / "ledger"), input_tokens=1, now=NOW)


def test_missing_policy_never_infers_1450_or_authorizes_any_key(monkeypatch):
    for key in ("GEMINI_CAP_POLICY_PATH", "GEMINI_PROJECT_EVIDENCE_PATH", "GEMINI_CAP_LEDGER_DIR"):
        monkeypatch.delenv(key, raising=False)
    for credential in ("primary", "backup"):
        monkeypatch.setenv("GEMINI_CREDENTIAL_ALIAS", credential)
        result = gate.from_environment(MODEL)
        assert result["skip"] is True and result["eligible"] is False
        assert result["use_backup_key"] is False


@pytest.mark.parametrize("credential", ["primary", "backup"])
def test_complete_synthetic_evidence_and_configured_cap_still_cannot_admit(tmp_path, credential):
    assert run_gate(tmp_path, credential=credential)["reason"] == "project_quota_or_trusted_binding_unavailable"
    state = json.loads((tmp_path / "ledger/state.json").read_text())
    assert state["reservations"] == 0  # No route/inference reservation on a denied preflight.


def test_project_parser_is_reused_without_conflating_local_and_project_limits(tmp_path, monkeypatch):
    seen = []
    original = gate.project_quota.normalize_gemini_evidence
    def capture(*args, **kwargs):
        result = original(*args, **kwargs)
        seen.append(result)
        return result
    monkeypatch.setattr(gate.project_quota, "normalize_gemini_evidence", capture)
    assert run_gate(tmp_path)["skip"] is True
    assert seen[0]["quota_scope"] == "project"
    assert seen[0]["dimensions"]["rpd"]["limit"] == 1000  # Not local aggregate limit 2.
    assert seen[0]["tier"] == "tier_1"


@pytest.mark.parametrize("mutation", ["credential", "project", "model"])
def test_backup_cannot_reuse_primary_or_other_project_model_evidence(tmp_path, mutation):
    raw = evidence("backup")
    raw[{"credential": "credential_alias", "project": "project_alias", "model": "model"}[mutation]] = {
        "credential": "primary", "project": "offline-project-a", "model": "gemini-other-fixture"}[mutation]
    assert run_gate(tmp_path, raw=raw, credential="backup")["reason"] == "project_credential_or_model_mismatch"


def test_model_switch_or_backup_does_not_restore_exhausted_shared_scope(tmp_path):
    configured = policy()
    ledger = str(tmp_path / "ledger")
    assert check_cap(configured, ledger, model=MODEL, now=NOW, reserve=True)["allowed"]
    assert check_cap(configured, ledger, model="gemini-other-fixture", credential="backup", now=NOW, reserve=True)["allowed"]
    for credential in ("primary", "backup"):
        result = run_gate(tmp_path, credential=credential, model="gemini-third-fixture")
        assert result["reason"] == "shared_cap_unavailable_or_exhausted"
        assert result["skip"] is True


@pytest.mark.parametrize("change", ["timestamp", "stale", "dimension", "tier", "triplet"])
def test_project_unknowns_fail_closed_even_with_local_headroom(tmp_path, change):
    raw = copy.deepcopy(evidence())
    if change == "timestamp":
        del raw["observed_at"]
    elif change == "stale":
        raw["observed_at"] = (NOW - dt.timedelta(seconds=120)).isoformat()
    elif change == "dimension":
        del raw["dimensions"]["input_tpm"]
    elif change == "tier":
        raw["tier"] = "untrusted-tier"
    else:
        raw["dimensions"]["rpd"]["remaining"] = 999
    assert run_gate(tmp_path, raw=raw)["skip"] is True


def test_forged_eligibility_still_does_not_enable_production(tmp_path, monkeypatch):
    monkeypatch.setattr(gate.project_quota, "evaluate_gemini_quota", lambda *args, **kwargs: {"eligible": True})
    assert run_gate(tmp_path)["reason"] == "production_admission_disabled"


@pytest.mark.parametrize("unsafe", ["symlink", "public", "malformed", "directory"])
def test_private_policy_input_rejected(tmp_path, unsafe):
    path = Path(private_file(tmp_path / "policy.json", policy()))
    if unsafe == "symlink":
        link = tmp_path / "link.json"
        link.symlink_to(path)
        path = link
    elif unsafe == "public":
        path.chmod(0o644)
    elif unsafe == "directory":
        path = tmp_path
    else:
        path.write_text("[]")
    result = gate.preflight(model=MODEL, credential="primary", policy_path=str(path),
                            evidence_path="", ledger_dir=str(tmp_path / "ledger"), now=NOW)
    assert result["reason"] == "private_quota_policy_or_evidence_unavailable"


def test_cli_outputs_no_private_alias_counters_or_backup_rotation(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gate, "from_environment", lambda: gate._deny("production_admission_disabled"))
    output = tmp_path / "github-output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    assert gate.main() == 0
    assert output.read_text() == "skip=true\nreason=production_admission_disabled\nuse_backup_key=false\n"
    public = capsys.readouterr().out + output.read_text()
    for private in ("offline-aggregate", "offline-project", "1000", "1450", "tier_1"):
        assert private not in public


@pytest.mark.parametrize("credential", ["primary", "backup"])
def test_actual_router_cannot_dispatch_by_switching_models_or_keys(tmp_path, monkeypatch, credential):
    monkeypatch.setenv("ROLE", "invoke")
    monkeypatch.setenv("HAS_GEMINI", "true")
    monkeypatch.setenv("HAS_OMNI", "false")
    monkeypatch.setenv("HAS_OPENROUTER", "false")
    monkeypatch.setenv("GEMINI_CREDENTIAL_ALIAS", credential)
    monkeypatch.delenv("GEMINI_CAP_POLICY_PATH", raising=False)
    monkeypatch.setattr(router, "COUNTER_DIR", str(tmp_path))
    monkeypatch.setattr(router, "parse_yaml", lambda *args: {})
    monkeypatch.setattr(router, "emit_decision", lambda *args, **kwargs: None)
    monkeypatch.setattr(router, "increment_usage", lambda *args: pytest.fail("denied route must not reserve"))
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    router.main()
    assert "provider=none\n" in output.read_text() and "skip=true\n" in output.read_text()
