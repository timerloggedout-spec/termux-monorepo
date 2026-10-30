"""Pins for the Actions corpus observer grouping (Slice 2).

group_runs is pure: synthetic run objects in, RED blocks out. Rates
and durations must be derived from the runs themselves, runs without
both duration stamps are excluded (counted, never estimated), and
the window is the runs' own created_at span.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "actions_observe", ROOT / "scripts" / "dashboards" / "actions_observe.py")
ao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ao)


def _run(path, created, conclusion="success", started=None, updated=None,
         status="completed", rid=1):
    return {"path": path, "name": path.split("/")[-1], "id": rid,
            "created_at": created, "conclusion": conclusion,
            "status": status, "event": "push", "head_sha": "abc",
            "run_attempt": 1, "html_url": "https://example.invalid/r",
            "run_started_at": started, "updated_at": updated}


def test_group_runs_red_math():
    runs = [
        _run("w/a.yml", "2026-10-30T00:00:00Z", "success",
             "2026-10-30T00:00:00Z", "2026-10-30T00:01:00Z", rid=1),
        _run("w/a.yml", "2026-10-30T01:00:00Z", "failure",
             "2026-10-30T01:00:00Z", "2026-10-30T01:03:00Z", rid=2),
        # completed but no stamps: excluded from duration, counted
        _run("w/a.yml", "2026-10-30T02:00:00Z", "success", rid=3),
        _run("w/b.yml", "2026-10-30T02:30:00Z", "cancelled",
             "2026-10-30T02:30:00Z", "2026-10-30T02:30:10Z", rid=4),
    ]
    g = ao.group_runs(runs)
    assert g["totals"] == {"runs": 4, "workflows": 2, "concluded": 4,
                           "failures": 1, "failure_rate": 0.25}
    assert g["window"]["earliest_created_at"] == "2026-10-30T00:00:00Z"
    assert g["window"]["span_hours"] == 2.5
    a = g["workflows"]["w/a.yml"]
    assert a["failure_rate"] == round(1 / 3, 6)
    assert a["duration_excluded"] == 1
    assert a["red"]["duration_s"]["n"] == 2
    assert a["red"]["duration_s"]["median"] == 180.0
    assert a["red"]["sample_rate_per_hour"] == round(3 / 2.5, 4)
    assert a["latest"]["id"] == 3


def test_group_runs_no_conclusions_no_fake_rate():
    runs = [_run("w/a.yml", "2026-10-30T00:00:00Z", None,
                 status="in_progress", rid=1)]
    g = ao.group_runs(runs)
    assert g["totals"]["failure_rate"] is None
    assert g["workflows"]["w/a.yml"]["red"]["duration_s"]["median"] is None
