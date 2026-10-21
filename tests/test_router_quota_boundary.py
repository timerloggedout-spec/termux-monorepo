"""Offline-only regression boundary for existing router lane #1441 (MSM-024)."""
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import stat
import subprocess
import textwrap

import pytest

from scripts import model_router as router
from scripts import quota_poll as poll
from scripts import provider_quota_service as service

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)


def snapshot(**changes):
    state = {
        "schema": "3l0.provider-quota-snapshot.v1", "status": "live",
        "source": "https://openrouter.ai/api/v1/key", "provider": "openrouter",
        "metric": "free_model_daily_requests", "window": "UTC day",
        "observed_at": NOW.isoformat(), "used": 4, "limit": 100, "remaining": 96,
    }
    state.update(changes)
    return state


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.setattr(router, "COUNTER_DIR", str(tmp_path))
    monkeypatch.delenv("QUOTA_SNAPSHOT_DIR", raising=False)
    monkeypatch.delenv("OPENROUTER_QUOTA_MAX_AGE_SEC", raising=False)
    monkeypatch.setenv("OPENROUTER_QUOTA_SAFETY", "0.90")
    monkeypatch.setattr(router, "get_usage", lambda *args: 0)


@pytest.mark.parametrize("change", [
    {"remaining": None}, {"remaining": True}, {"remaining": -1}, {"remaining": 97},
    {"remaining": 101}, {"used": 101, "remaining": 0}, {"used": 4.0},
    {"limit": 100.0}, {"remaining": 96.0}, {"used": True},
    {"provider": "ollama"}, {"metric": "USD"}, {"source": "https://example.test"},
    {"window": "month"}, {"source": None},
    {"observed_at": (NOW + timedelta(microseconds=1)).isoformat()},
    {"observed_at": (NOW - timedelta(seconds=901)).isoformat()},
    {"observed_at": NOW.replace(tzinfo=None).isoformat()},
    {"observed_at": "invalid"}, {"status": "observed"},
    {"used": 10**400, "limit": 10**400 + 96},
])
def test_snapshot_rejects_incomplete_or_untrusted_evidence(tmp_path, change):
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(snapshot(**change)))
    result = router.load_openrouter_quota_admission(now=NOW)
    assert result["known"] is False
    assert not result.get("admit", False)


@pytest.mark.parametrize("state", [[], "not a mapping", None, 3, True])
def test_snapshot_malformed_root_is_unknown_not_exception(tmp_path, state):
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(state))
    assert router.load_openrouter_quota_admission(now=NOW)["known"] is False


def test_snapshot_must_be_current_utc_day(tmp_path):
    now = NOW.replace(hour=0, minute=1)
    state = snapshot(observed_at=(now - timedelta(minutes=2)).isoformat())
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(state))
    assert router.load_openrouter_quota_admission(now=now)["known"] is False


def test_fresh_valid_triplet_retains_conservative_reservations(tmp_path, monkeypatch):
    monkeypatch.setattr(router, "ROLE_PEERS", {"triage": [("openrouter", "offline:free")]})
    monkeypatch.setattr(router, "get_usage", lambda *args: 95)
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(snapshot()))
    result = router.load_openrouter_quota_admission(now=NOW)
    assert result["known"] is True
    assert result["official_remaining"] == 96
    assert result["effective_used"] == 95
    assert result["admit"] is False


def test_private_snapshot_path_does_not_fall_back_to_cached_quota(tmp_path, monkeypatch):
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(snapshot()))
    private = tmp_path / "private"
    private.mkdir()
    monkeypatch.setenv("QUOTA_SNAPSHOT_DIR", str(private))
    assert router.load_openrouter_quota_admission(now=NOW)["known"] is False
    (private / "provider-quota-state.json").write_text(json.dumps(snapshot()))
    assert router.load_openrouter_quota_admission(now=NOW)["known"] is True


@pytest.mark.parametrize("state", [[], None, "bad", {
    "schema": "3l0.quota-weights.v1", "generated_at": "2026-10-21T12:00:00",
    "multipliers": {"openrouter": 1},
}])
def test_malformed_weights_are_unknown(tmp_path, monkeypatch, state):
    path = tmp_path / "weights.json"
    path.write_text(json.dumps(state))
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(path))
    assert router.load_quota_multipliers() == {}


@pytest.mark.parametrize("multipliers", [[], {"openrouter": True}, {"openrouter": float("nan")},
                                        {"openrouter": float("inf")}, {"openrouter": 10**400}])
def test_invalid_weights_are_unknown(tmp_path, monkeypatch, multipliers):
    path = tmp_path / "weights.json"
    path.write_text(json.dumps({"schema": "3l0.quota-weights.v1",
                               "generated_at": datetime.now(timezone.utc).isoformat(),
                               "multipliers": multipliers}))
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(path))
    assert router.load_quota_multipliers() == {}


def test_future_weights_are_unknown(tmp_path, monkeypatch):
    path = tmp_path / "weights.json"
    path.write_text(json.dumps({"schema": "3l0.quota-weights.v1",
                               "generated_at": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
                               "multipliers": {"openrouter": 2}}))
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(path))
    assert router.load_quota_multipliers() == {}


@pytest.mark.parametrize("change", [{"remaining": None}, {"remaining": 95}, {"remaining": True},
                                     {"used": 4.0}, {"extra": "invalid"},
                                     {"extra": {"source": "untrusted"}}])
def test_poller_never_publishes_invalid_triplet_as_live(tmp_path, monkeypatch, change):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps({"services": [{
        "id": "openrouter.free_models", "provider": "openrouter", "lane": "model",
        "metric": "free requests", "unit": "requests/day", "window": "UTC day",
        "reset": "unknown", "zone": "UTC", "source": "https://example.test/docs",
        "limit": 999,
    }]}))
    reading = {"used": 4, "limit": 100, "remaining": 96,
               "extra": {"source": "official OpenRouter GET /api/v1/key"}}
    reading.update(change)
    monkeypatch.setattr(poll, "LIVE", {"openrouter.free_models": lambda now: reading})
    monkeypatch.setattr(poll, "MULTI", [])
    out = tmp_path / "out"
    poll.main(["--registry", str(registry), "--out", str(out)])
    state = json.loads((out / "provider-quota-state.json").read_text())
    assert state["status"] == "unknown"
    assert state["used"] is state["limit"] is state["remaining"] is None
    assert "openrouter" not in json.loads((out / "routing-weights.json").read_text())["multipliers"]


def test_no_request_reset_is_inferred(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "offline-only")
    monkeypatch.setattr(poll, "_get", lambda *args: {"data": {
        "free_model_daily_requests": {"used": 4, "limit": 100, "remaining": 96}}})
    assert poll.openrouter_reader(NOW)["reset"] is None


def test_service_observation_is_not_a_router_snapshot(tmp_path):
    # A real private service schema is still not authenticated router admission.
    observation = service.observe_service("openrouter.key", "", scope="offline", now=NOW,
                                          request=lambda **kwargs: pytest.fail("no account call authorized"))
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(observation))
    assert router.load_openrouter_quota_admission(now=NOW)["known"] is False


def action_run(name):
    action = (ROOT / ".github/actions/model-router/action.yml").read_text()
    section = action.split(f"    - name: {name}\n", 1)[1].split("\n    - name:", 1)[0]
    return textwrap.dedent(section.split("      run: |\n", 1)[1])


@pytest.mark.parametrize("exit_code", [0, 1])
def test_private_preflight_shell_hides_values_and_cleanup_runs(tmp_path, exit_code):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    stub = bindir / "python3"
    stub.write_text('#!/bin/bash\nprintf "PRIVATE_QUOTA_CANARY\\n"\nprintf "PRIVATE_ERROR_CANARY\\n" >&2\n'
                    'printf "PRIVATE_QUOTA_CANARY" > "${@: -1}/provider-quota-state.json"\n'
                    f'exit {exit_code}\n')
    stub.chmod(0o700)
    output = tmp_path / "output"
    output.touch()
    env = {**os.environ, "PATH": f"{bindir}:{os.environ['PATH']}",
           "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output)}
    result = subprocess.run(["bash", "-c", action_run("Refresh live provider quota weights")],
                            env=env, text=True, capture_output=True)
    assert result.returncode == exit_code
    assert "PRIVATE_QUOTA_CANARY" not in result.stdout + result.stderr
    assert "PRIVATE_ERROR_CANARY" not in result.stdout + result.stderr
    private = Path(output.read_text().strip().removeprefix("path="))
    if exit_code == 0:
        assert stat.S_IMODE(private.stat().st_mode) == 0o700
        assert stat.S_IMODE((private / "provider-quota-state.json").stat().st_mode) == 0o600
    else:
        assert not private.exists()
    cleanup = subprocess.run(["bash", "-c", action_run("Remove private quota preflight files")],
                             env={**env, "PRIVATE_QUOTA_DIR": str(private)}, capture_output=True)
    assert cleanup.returncode == 0
    assert not private.exists()


def test_action_never_caches_private_quota_or_service_data():
    action = (ROOT / ".github/actions/model-router/action.yml").read_text()
    assert "default: 'v5'" in action
    for name in ("Restore versioned model-router capacity cache", "Save versioned model-router capacity cache"):
        section = action.split(f"    - name: {name}\n", 1)[1].split("\n    - name:", 1)[0]
        assert "path: /tmp/model-router\n" not in section
        assert "/tmp/model-router/*.txt" in section
        for private in ("provider-quota-state.json", "routing-weights.json", "quota-records.jsonl",
                        "hindsight-retain.jsonl", "provider_quota_service"):
            assert private not in section
    assert "if: always() && steps.quota.outputs.path != ''" in action
    assert "QUOTA_SNAPSHOT_DIR:" in action
    assert "QUOTA_WEIGHTS_PATH:" in action


@pytest.mark.parametrize("state", [[], None, snapshot(remaining=95)])
def test_strict_router_emits_explicit_skip_for_bad_snapshot(tmp_path, monkeypatch, state):
    monkeypatch.setenv("ROLE", "triage")
    monkeypatch.setenv("HAS_OPENROUTER", "true")
    monkeypatch.setenv("HAS_GEMINI", "false")
    monkeypatch.setenv("HAS_OMNI", "false")
    monkeypatch.setenv("REQUIRE_LIVE_OPENROUTER_QUOTA", "true")
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(tmp_path / "absent-weights.json"))
    monkeypatch.setattr(router, "parse_yaml", lambda *args: {})
    monkeypatch.setattr(router, "emit_decision", lambda *args, **kwargs: None)
    monkeypatch.setattr(router, "ROLE_PEER_MODELS", {"triage": {"openrouter": ["offline:free"]}})
    monkeypatch.setattr(router, "fetch_openrouter_free_models_cached_with_source",
                        lambda: (["offline:free"], "offline_fixture"))
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(state))
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    router.main()
    assert "provider=none" in output.read_text()
    assert "skip=true" in output.read_text()


def test_router_logs_withhold_official_quota_values(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HAS_OPENROUTER", "true")
    monkeypatch.setenv("HAS_GEMINI", "false")
    monkeypatch.setenv("HAS_OMNI", "false")
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(tmp_path / "absent-weights.json"))
    monkeypatch.setattr(router, "parse_yaml", lambda *args: {})
    monkeypatch.setattr(router, "emit_decision", lambda *args, **kwargs: None)
    monkeypatch.setattr(router, "ROLE_PEER_MODELS", {})
    monkeypatch.setattr(router, "fetch_openrouter_free_models_cached_with_source", lambda: ([], "offline_fixture"))
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(snapshot(
        observed_at=datetime.now(timezone.utc).isoformat(), used=714239, limit=900000, remaining=185761)))
    router.main()
    captured = capsys.readouterr()
    assert "private values withheld" in captured.err
    for private in ("714239", "900000", "185761", "810000"):
        assert private not in captured.out + captured.err


@pytest.mark.parametrize("stamp", [None, 1, True, [], {}])
def test_timestamp_types_fail_closed(tmp_path, monkeypatch, stamp):
    (tmp_path / "provider-quota-state.json").write_text(json.dumps(snapshot(observed_at=stamp)))
    assert router.load_openrouter_quota_admission(now=NOW)["known"] is False
    path = tmp_path / "weights.json"
    path.write_text(json.dumps({"schema": "3l0.quota-weights.v1", "generated_at": stamp,
                               "multipliers": {"openrouter": 2}}))
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(path))
    assert router.load_quota_multipliers() == {}


def test_weights_symlink_is_not_trusted(tmp_path, monkeypatch):
    target = tmp_path / "target.json"
    target.write_text(json.dumps({"schema": "3l0.quota-weights.v1",
                                 "generated_at": datetime.now(timezone.utc).isoformat(),
                                 "multipliers": {"openrouter": 2}}))
    link = tmp_path / "weights.json"
    link.symlink_to(target)
    monkeypatch.setenv("QUOTA_WEIGHTS_PATH", str(link))
    assert router.load_quota_multipliers() == {}


def test_preflight_output_publication_failure_removes_private_directory(tmp_path):
    env = {**os.environ, "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(tmp_path)}
    result = subprocess.run(["bash", "-c", action_run("Refresh live provider quota weights")],
                            env=env, capture_output=True)
    assert result.returncode != 0
    assert not list(tmp_path.glob("model-router-quota.*"))
