import concurrent.futures
import datetime as dt
import json
import os
import sys
from pathlib import Path

import pytest
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import gemini_shared_cap as cap

UTC = dt.timezone.utc
PACIFIC = ZoneInfo("America/Los_Angeles")


def policy(now, limit=2, scope="private-team"):
    local_day = now.astimezone(PACIFIC).date()
    end = dt.datetime.combine(local_day + dt.timedelta(days=1), dt.time(), PACIFIC)
    return {"schema": cap.SCHEMA, "cap_kind": "operator_configured", "scope_alias": scope,
            "limit": limit, "pacific_day": local_day.isoformat(), "expires_at": end.isoformat(),
            "credentials": {"primary": {"project_alias": "proj-a"},
                            "backup": {"project_alias": "proj-b"}}}


def test_models_and_credentials_share_single_aggregate(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    p = policy(now, limit=2)
    assert cap.check_cap(p, tmp_path, model="gemini-1", reserve=True, now=now)["allowed"]
    assert cap.check_cap(p, tmp_path, model="gemini-2", credential="backup", reserve=True, now=now)["allowed"]
    assert cap.check_cap(p, tmp_path, model="gemini-3", reserve=True, now=now)["reason"] == "cap_exhausted"
    assert cap.check_cap(p, tmp_path, model="gemini-1", credential="backup", reserve=False, now=now)["allowed"] is False


def test_separate_ledgers_and_scope_pin(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    p = policy(now, limit=1)
    assert cap.check_cap(p, tmp_path / "a", model="m", reserve=True, now=now)["allowed"]
    assert cap.check_cap(policy(now, 1, "another-scope"), tmp_path / "b", model="m", reserve=True, now=now)["allowed"]
    assert cap.check_cap(policy(now, 3, "another-scope"), tmp_path / "a", model="m", now=now)["reason"] == "scope_mismatch"


def test_invalid_or_missing_policy_denies_and_no_default_limit(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    assert cap.check_cap(None, tmp_path, model="m", now=now)["allowed"] is False
    p = policy(now)
    del p["limit"]
    assert cap.check_cap(p, tmp_path, model="m", now=now)["allowed"] is False
    p = policy(now)
    p["cap_kind"] = "verified"
    assert cap.check_cap(p, tmp_path, model="m", now=now)["allowed"] is False
    assert cap.check_cap(policy(now), tmp_path, model="bad:model", now=now)["allowed"] is False


def test_corrupt_symlink_and_tampering_fail_closed(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    p = policy(now, limit=1)
    assert cap.check_cap(p, tmp_path, model="m", reserve=True, now=now)["allowed"]
    assert cap.check_cap(policy(now, limit=100), tmp_path, model="m", reserve=True, now=now)["reason"] == "cap_exhausted"
    (tmp_path / "state.json").write_text("{broken", encoding="utf-8")
    assert cap.check_cap(p, tmp_path, model="m", now=now)["allowed"] is False
    (tmp_path / "state.json").unlink()
    target = tmp_path / "elsewhere"
    target.write_text("{}", encoding="utf-8")
    (tmp_path / "state.json").symlink_to(target)
    assert cap.check_cap(p, tmp_path, model="m", now=now)["allowed"] is False


def test_symlink_parent_denied(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    assert cap.check_cap(policy(now), link / "ledger", model="m", now=now)["allowed"] is False


@pytest.mark.parametrize("field,value", [
    ("schema", None), ("scope_alias", None), ("pacific_day", None),
    ("pacific_day", 20250115), ("pacific_day", "2025-02-30"),
    ("limit", None), ("reservations", None),
    ("unexpected", 1),
])
def test_malformed_existing_ledger_fails_closed(tmp_path, field, value):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    state = {"schema": "gemini-shared-cap-ledger/v1", "scope_alias": "private-team",
             "pacific_day": "2025-01-15", "limit": 2, "reservations": 0}
    if field == "unexpected":
        state[field] = value
    else:
        state[field] = value
    (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")
    result = cap.check_cap(policy(now), tmp_path, model="m", now=now)
    assert result["allowed"] is False
    assert result["reason"] == "invalid_policy_or_ledger"


def test_invalid_ledger_directory_does_not_chmod_current_directory(tmp_path, monkeypatch):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    monkeypatch.chdir(tmp_path)
    os.chmod(tmp_path, 0o700)
    for path in ("", "relative", "../escape"):
        assert cap.check_cap(policy(now), path, model="m", now=now)["allowed"] is False
        assert tmp_path.stat().st_mode & 0o777 == 0o700


def test_hardlinked_state_and_lock_denied(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    outside = tmp_path / "outside"
    ledger = tmp_path / "ledger"
    ledger.mkdir()
    state = {"schema": "gemini-shared-cap-ledger/v1", "scope_alias": "private-team",
             "pacific_day": "2025-01-15", "limit": 2, "reservations": 0}
    (tmp_path / "original").write_text(json.dumps(state), encoding="utf-8")
    os.link(tmp_path / "original", ledger / "state.json")
    assert cap.check_cap(policy(now), ledger, model="m", now=now)["allowed"] is False
    (ledger / "state.json").unlink()
    (ledger / ".lock").write_text("", encoding="utf-8")
    os.link(ledger / ".lock", outside)
    assert cap.check_cap(policy(now), ledger, model="m", now=now)["allowed"] is False


def test_pacific_midnight_reset_across_dst_day_length(tmp_path):
    # DST starts March 9 2025; this Pacific calendar day lasts 23 hours.
    before = dt.datetime(2025, 3, 9, 7, 30, tzinfo=UTC)
    after = dt.datetime(2025, 3, 10, 7, 30, tzinfo=UTC)
    assert (dt.datetime.combine(dt.date(2025, 3, 10), dt.time(), PACIFIC).astimezone(UTC)
            - dt.datetime.combine(dt.date(2025, 3, 9), dt.time(), PACIFIC).astimezone(UTC)).total_seconds() == 23 * 3600
    p1 = policy(before, limit=1)
    assert cap.check_cap(p1, tmp_path, model="m", reserve=True, now=before)["allowed"]
    assert cap.check_cap(policy(after, limit=1), tmp_path, model="m", reserve=True, now=after)["allowed"]
    assert cap.check_cap(p1, tmp_path, model="m", now=before)["reason"] == "day_rollback"


def test_atomic_concurrent_reservations_and_secure_modes(tmp_path):
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    p = policy(now, limit=7)
    def reserve(i):
        return cap.check_cap(p, tmp_path, model=f"m{i}", credential="primary" if i % 2 else "backup",
                             reserve=True, now=now)["allowed"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(reserve, range(20)))
    assert sum(results) == 7
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["reservations"] == 7
    assert (tmp_path.stat().st_mode & 0o777) == 0o700
    assert (tmp_path / "state.json").stat().st_mode & 0o777 == 0o600
    assert (tmp_path / ".lock").stat().st_mode & 0o777 == 0o600


def test_module_imports_without_zone_data_then_cap_denies(monkeypatch, tmp_path):
    monkeypatch.setattr(cap, "ZoneInfo", lambda name: (_ for _ in ()).throw(
        ZoneInfoNotFoundError(name)))
    now = dt.datetime(2025, 1, 15, 20, tzinfo=UTC)
    result = cap.check_cap(policy(now), tmp_path / "ledger", model="m", reserve=True, now=now)
    assert result["allowed"] is False
    assert result["reason"] == "invalid_policy_or_ledger"
    assert not (tmp_path / "ledger").exists()
