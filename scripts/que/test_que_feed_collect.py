import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import que_feed_collect as q  # noqa: E402

TIERS = {"tiers": [
    {"tier": 1, "patterns": ["gate", "admission", "guard"]},
    {"tier": 2, "patterns": ["release-cut", "sync", "publish"]},
    {"tier": 3, "patterns": ["proof", "build"]},
    {"tier": 4, "patterns": []}]}
AT = datetime(2026, 11, 4, 8, 0, tzinfo=timezone.utc)


def run(rid, name, created, status="queued", **kw):
    return {"id": rid, "name": name, "created_at": created,
            "html_url": f"https://x/{rid}", "status": status, **kw}


def test_classify_first_match_and_default():
    assert q.classify("studysprint-apk-smoke gate", TIERS) == 1
    assert q.classify("Release-Cut publish", TIERS) == 2
    assert q.classify("strands-proof", TIERS) == 3
    assert q.classify("countdowns collect", TIERS) == 4
    # tier 1 wins over a later tier's pattern (first match)
    assert q.classify("gate build", TIERS) == 1


def test_tier_feed_counts_and_wedged_exclusion():
    queued = [run(1, "apk gate", "2026-11-04T07:00:00Z"),
              run(2, "countdowns", "2026-11-04T07:30:00Z"),
              run(3, "countdowns", "2026-10-01T00:00:00Z")]
    feed = q.tier_feed(queued, [], TIERS, AT)
    assert feed["tiers"]["1"]["queued"] == 1
    assert feed["tiers"]["4"]["queued"] == 1
    assert feed["totals"]["queued"] == 2
    assert [w["id"] for w in feed["wedged_ancient"]] == [3]
    assert feed["tiers"]["1"]["oldest_queued_at"] == "2026-11-04T07:00:00Z"


def test_transitions_emit_full_lifecycle():
    r = run(9, "apk gate", "2026-11-04T07:00:00Z")
    ev, st = q.transitions({}, [r], [], [], TIERS, AT)
    assert [e["event"] for e in ev] == ["queued"]
    r2 = dict(r, run_started_at="2026-11-04T07:05:00Z")
    ev, st = q.transitions(st, [], [r2], [], TIERS, AT)
    assert [e["event"] for e in ev] == ["started"]
    assert ev[0]["queue_wait_s"] == 300
    r3 = dict(r, conclusion="success")
    ev, st = q.transitions(st, [], [], [r3], TIERS, AT)
    assert [e["event"] for e in ev] == ["completed"]
    assert st["active"] == {}


def test_queue_feed_shape_and_provenance():
    feed = q.queue_feed([run(1, "apk gate", "2026-11-04T07:00:00Z")],
                         [], TIERS, AT)
    assert feed["schema"] == "que-queue-feed/v1"
    # naming swap (Registry issuance PR #4817): the brand of
    # record is Stagefoil; the priming label survives only
    # in the issuance section itself — never in these records
    assert "Stagefoil" in feed["provenance"]["design_input"]
    assert "AutoDesk" not in feed["provenance"]["design_input"]
    assert "Autodesk" not in feed["provenance"]["design_input"]
    assert feed["queue"]["tiers"]["1"]["queued"] == 1
    # no dispatch-state feed in the test tree: claims stay an
    # honest empty fold with the source named
    assert feed["dispatch_claims"]["active_claims"] == []
    assert feed["dispatch_claims"]["source"].endswith(
        "dispatch-state-feed.json")


def test_governor_fold_tallies_frozen_event_shape(tmp_path,
                                                  monkeypatch):
    events = tmp_path / "events"
    events.mkdir()
    (events / "governor-events-2026-11-04.jsonl").write_text(
        '{"schema":"que-governor-event/v1","ts":"2026-11-04T01:00:00Z",'
        '"kind":"projection","actor":"pat-helper/flow-governor",'
        '"session":"s1","path":"/x","chain":null,'
        '"verdict":"deferred","detail":{"projected_used":4600}}\n'
        '{"schema":"que-governor-event/v1","ts":"2026-11-04T02:00:00Z",'
        '"kind":"session_cap","actor":"pat-helper/flow-governor",'
        '"session":"s2","path":"/y","chain":"d1",'
        '"verdict":"deferred","detail":{"spent":400,"cap":400}}\n')
    monkeypatch.setattr(q, "EVENTS", events)
    monkeypatch.setattr(q, "api",
                        lambda path, token: {"total_count": 0})
    feed = q.governor_feed("t", AT)
    flow = feed["flow_governor"]
    # FREEZE design: this feed is the governor plane; the
    # first emitter batch flips it to populated
    assert flow["state"] == "populated"
    assert flow["events_total"] == 2
    assert flow["by_kind"] == {"projection": 1, "session_cap": 1}
    assert flow["latest_event_at"] == "2026-11-04T02:00:00Z"


def test_transitions_vanished_is_a_gap_event():
    r = run(5, "countdowns", "2026-11-04T07:00:00Z")
    _, st = q.transitions({}, [r], [], [], TIERS, AT)
    ev, _ = q.transitions(st, [], [], [], TIERS, AT)
    assert [e["event"] for e in ev] == ["vanished"]


def test_page_fetch_aliases_pinned():
    # the QUE page fetches the que- prefixed dashboard names
    # (Desk gap report on the #4824 section): the collector
    # must publish both aliases and the workflow must stage
    # them — a contract pin over the source + workflow text
    from pathlib import Path
    src = Path(q.__file__).read_text()
    assert 'alias="que-governor.json"' in src
    assert 'alias="que-priority-windows.json"' in src
    wf = Path(q.__file__).with_name("que-feed-collect.yml")
    if wf.exists():
        text = wf.read_text()
        assert "data/que-governor.json" in text
        assert "data/que-priority-windows.json" in text
