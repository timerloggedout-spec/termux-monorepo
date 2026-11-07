import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cadence_tick_ledger as ctl  # noqa: E402


def tick(ts, endpoint="/user", resource="core", used=10, counted=True,
         principal="pat", status=200):
    return {"ts": ts, "principal": principal, "session": "s1", "method": "GET",
            "endpoint": endpoint, "resource": resource, "limit": 5000,
            "used": used, "remaining": 5000 - used, "reset": 1793353639,
            "status": status, "counted": counted}


def write(tmp_path, ticks):
    p = tmp_path / "ticks.jsonl"
    p.write_text("\n".join(json.dumps(t) for t in ticks) + "\n")
    return str(p)


def test_check_ok(tmp_path):
    f = write(tmp_path, [tick("2026-10-30T09:32:06Z")])
    assert ctl.main(["check", f]) == 0


def test_check_missing_field_fails(tmp_path):
    bad = tick("2026-10-30T09:32:06Z")
    del bad["used"]
    f = write(tmp_path, [bad])
    assert ctl.main(["check", f]) == 1


def test_summarize_counts_and_latest(tmp_path):
    ticks = [tick("2026-10-30T09:32:06Z", used=10),
             tick("2026-10-30T09:32:40Z", endpoint="/repos/{o}/{r}/pulls", used=11),
             tick("2026-10-30T09:32:50Z", endpoint="/rate_limit", counted=False, used=11),
             tick("2026-10-30T09:33:05Z", endpoint="/search/repositories",
                  resource="search", used=1)]
    ticks[3].update({"limit": 30, "remaining": 29})
    f = write(tmp_path, ticks)
    loaded, errors = ctl.load_ticks([f])
    assert not errors
    feed = ctl.summarize(loaded)
    assert feed["ticks_total"] == 4
    assert feed["ticks_counted"] == 3
    assert feed["counted_by_endpoint"][0] == {"endpoint": "/user", "calls": 1}
    assert {tuple(sorted(d.items())) for d in feed["counted_by_principal_resource"]} >= {
        tuple(sorted({"principal": "pat", "resource": "core", "calls": 2}.items()))}
    assert feed["burn_per_minute"] == [
        {"minute": "2026-10-30T09:32", "counted_calls": 2},
        {"minute": "2026-10-30T09:33", "counted_calls": 1}]
    assert feed["latest_remaining_by_resource"]["core"]["remaining"] == 4989
    assert feed["latest_remaining_by_resource"]["search"]["remaining"] == 29


def test_check_rejects_invalid_timestamp_and_counter_ranges(tmp_path):
    bad_time = tick("not-a-timestamp")
    bad_count = tick("2026-10-30T09:32:06Z", used=-1)
    f = write(tmp_path, [bad_time, bad_count])
    loaded, errors = ctl.load_ticks([f])
    assert loaded == []
    assert any("ISO-8601" in error for error in errors)
    assert any("used must be non-negative" in error for error in errors)
    assert ctl.main(["check", f]) == 1


def test_check_rejects_duplicate_replayed_tick(tmp_path):
    item = tick("2026-10-30T09:32:06Z")
    f = write(tmp_path, [item, item.copy()])
    loaded, errors = ctl.load_ticks([f])
    assert len(loaded) == 1
    assert any("duplicate/replayed" in error for error in errors)
    assert ctl.main(["check", f]) == 1


def test_check_rejects_non_boolean_counted_and_invalid_remaining(tmp_path):
    bad_type = tick("2026-10-30T09:32:06Z")
    bad_type["counted"] = 1
    bad_range = tick("2026-10-30T09:32:07Z")
    bad_range["remaining"] = 5001
    f = write(tmp_path, [bad_type, bad_range])
    loaded, errors = ctl.load_ticks([f])
    assert loaded == []
    assert any("counted must be a boolean" in error for error in errors)
    assert any("remaining exceeds limit" in error for error in errors)
