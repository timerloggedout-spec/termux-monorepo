"""Public challenge projection contract (Hackathon Desk / HD-002).

The browser consumes an explicit public allowlist, never the coordinator SSOT.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "dashboards" / "challenge_public_feed.py"
FORBIDDEN = {"metrics_internal", "win_probability"}


def _module():
    spec = importlib.util.spec_from_file_location("challenge_public_feed", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def test_real_coordinator_projects_events_without_internal_metrics():
    feed = _module().build_feed(ROOT)
    coordinator = json.loads((ROOT / "ops/challenge/coordinator.json").read_text())
    assert feed["schema"] == "challenge-public-feed/v1"
    assert [event["id"] for event in feed["events"]] == [
        event["id"] for event in coordinator["events"]
    ]
    assert FORBIDDEN.isdisjoint(set(_walk_keys(feed)))
    assert all("projects" not in event for event in feed["events"])
    assert all("opportunity_cost" not in event for event in feed["events"])
    c11 = next(event for event in feed["events"] if event["id"] == "C11")
    assert [match["id"] for match in c11["matches"]] == ["M1", "M2", "M3", "M4", "M5", "M6"]
    assert c11["matches"][4]["name"] == "AI-Powered Code Repository Repair"
    assert "queue" not in c11["matches"][1]
    assert c11["deadline"] == "2026-12-01T11:00:00-08:00"
    c12 = next(event for event in feed["events"] if event["id"] == "C12")
    assert c12["dates"]["final_due"] == "2026-11-30T23:45:00-08:00"
    assert isinstance(c12["prizes"]["tiers"], str)


def test_projection_is_closed_allowlist_and_preserves_public_gate_fields(tmp_path):
    source = tmp_path / "ops/challenge/coordinator.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({
        "schema_version": 1,
        "events": [{
            "id": "D9",
            "name": "Public event",
            "host": "Host",
            "platform": "lablab",
            "official_url": "https://example.com/event",
            "status": "active",
            "dates": {
                "deadline": {"at": "2026-12-01T00:00:00Z", "tz": "UTC",
                             "source": "official page", "metrics_internal": {"win_probability": 0.8}},
                "private_field": "drop",
            },
            "gates": [{
                "id": "G1", "label": "Public gate", "blocks": True,
                "status": "open", "text": "Public gate text", "evidence": [{"secret": "drop"}],
                "metrics_internal": {"win_probability": 0.9},
            }],
            "prizes": {
                "status": "ESTABLISHED", "pool": "$100",
                "tiers": [{"place": "1st", "award": "$100",
                           "source_url": "https://example.com/rules",
                           "win_probability": 1.0}],
                "metrics_internal": {"win_probability": 0.5},
            },
            "registration": {"state": "registered", "token": "drop"},
            "submission": {"state": "submitted", "at": "2026-11-20T00:00:00Z",
                           "confirmation_ref": "drop"},
            "projects": [{"name": "internal"}],
            "opportunity_cost": {"gross_foregone": 100},
            "metrics_internal": {"win_probability": 0.7},
            "win_probability": 0.7,
            "extension": {"nested": {"metrics_internal": {"win_probability": 0.1}}},
        }],
    }), encoding="utf-8")

    feed = _module().build_feed(tmp_path)
    event = feed["events"][0]
    assert event["id"] == "D9"
    assert event["dates"]["deadline"] == {
        "at": "2026-12-01T00:00:00Z", "tz": "UTC", "source": "official page"
    }
    assert event["gates"] == [{
        "id": "G1", "label": "Public gate", "blocks": True,
        "status": "open", "text": "Public gate text"
    }]
    assert event["prizes"]["tiers"] == [{
        "place": "1st", "award": "$100", "source_url": "https://example.com/rules"
    }]
    assert event["registration"] == {"state": "registered"}
    assert event["submission"] == {"state": "submitted", "at": "2026-11-20T00:00:00Z"}
    assert FORBIDDEN.isdisjoint(set(_walk_keys(feed)))
    assert "projects" not in event
    assert "opportunity_cost" not in event
    assert "extension" not in event


def test_projection_output_is_deterministic_except_generation_stamp(tmp_path):
    source = tmp_path / "ops/challenge/coordinator.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({
        "schema_version": 1,
        "events": [{"id": "D1", "name": "Event", "gates": []}],
    }), encoding="utf-8")
    module = _module()
    first = module.build_feed(tmp_path)
    second = module.build_feed(tmp_path)
    assert first.pop("generated_at")
    assert second.pop("generated_at")
    assert first == second


def test_invalid_coordinator_schema_fails_closed(tmp_path):
    source = tmp_path / "ops/challenge/coordinator.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({"schema_version": 2, "events": []}), encoding="utf-8")
    try:
        _module().build_feed(tmp_path)
    except ValueError as exc:
        assert "schema_version" in str(exc)
    else:
        raise AssertionError("unsupported coordinator schema must fail closed")


def test_missing_or_non_list_events_fails_closed(tmp_path):
    source = tmp_path / "ops/challenge/coordinator.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({"schema_version": 1, "events": {}}), encoding="utf-8")
    try:
        _module().build_feed(tmp_path)
    except ValueError as exc:
        assert "events" in str(exc)
    else:
        raise AssertionError("invalid events collection must fail closed")
