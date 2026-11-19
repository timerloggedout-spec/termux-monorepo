"""Owner order 2026-11-18 QUE FIX⊕UPGRADE: kick, freshness, tier basis,
claim scoring, exclusions, watchdog score shape."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "dispatch"))
sys.path.insert(0, str(HERE.parent / "ci"))
import cadence_kick as k  # noqa: E402
import que_feed_collect as q  # noqa: E402
import task_ranking  # noqa: E402

NOW = datetime(2026, 11, 18, 9, 0, tzinfo=timezone.utc)
TIERS = {"tiers": [{"tier": 1, "patterns": ["gate"]},
                   {"tier": 4, "patterns": ["sweep"]}]}


def _ts(minutes_ago):
    return (NOW - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_kick_decisions():
    assert k.decide([], 12, NOW)["action"] == "kick"
    assert k.decide([{"status": "completed", "created_at": _ts(30)}], 12, NOW)["action"] == "kick"
    assert k.decide([{"status": "completed", "created_at": _ts(5)}], 12, NOW)["action"] == "ok"
    d = k.decide([{"status": "queued", "created_at": _ts(40)},
                  {"status": "completed", "created_at": _ts(90)}], 12, NOW)
    assert d["action"] == "skip" and d["in_flight"] == 1
    assert d["oldest_queued_wait_s"] == 2400.0


def test_classify_basis_three_way():
    assert q.classify_basis("gate build", TIERS) == "explicit"
    assert q.classify_basis("lane sweep", TIERS) == "explicit"
    assert q.classify_basis("something else", TIERS) == "default-T4"
    assert q.classify_basis("", TIERS) == "unmatched"
    tb = q.tier_basis([{"name": "gate"}, {"name": "x"}], [{"name": ""}], TIERS, 3, 1)
    assert tb["explicit"]["1"] == 1 and tb["default_t4"] == 1
    assert tb["unmatched"] == 1 and tb["ancient_excluded"] == 3
    assert tb["operator_excluded"] == 1


def test_claim_tier_basis():
    assert q.claim_tier_basis({"entry": "Other", "tier": {"index": 2}}) == "unmatched"
    assert q.claim_tier_basis({"entry": "D5", "tier": {"index": 0, "name": "BASE"}}) == "default"
    assert q.claim_tier_basis({"entry": "D5", "tier": {"index": 2}, "nearest_wall": _ts(-60)}) == "explicit"


def test_fold_scores_every_claim(tmp_path, monkeypatch):
    rows = [{"issue": n, "entry": "D5", "state": "claimed", "age_min": 10 * n,
             "tier": {"index": 1, "name": "CUSHION"}, "claim": {"by": "x"}}
            for n in (1, 2, 3)]
    root = tmp_path
    (root / "ops" / "challenge").mkdir(parents=True)
    (root / "ops" / "challenge" / "dispatch-state-feed.json").write_text(
        json.dumps({"schema": "dispatch-state-feed/v1", "generated_at": _ts(10),
                    "counts": {"claimed": 3}, "dispatches": rows}))
    monkeypatch.setattr(q, "ROOT", root)
    c = q.queue_feed([], [], TIERS, NOW)["dispatch_claims"]
    assert c["scored"] == 3 == len(c["active_claims"])
    assert all(a["rank_method"] == task_ranking.METHOD for a in c["active_claims"])
    assert c["tier_basis"]["explicit"] == 3


def test_source_freshness(tmp_path):
    (tmp_path / "ops" / "challenge").mkdir(parents=True)
    (tmp_path / "ops" / "que" / "events").mkdir(parents=True)
    (tmp_path / "ops" / "challenge" / "dispatch-state-feed.json").write_text(
        json.dumps({"generated_at": _ts(60 * 24)}))
    fr = q.source_freshness(NOW, _ts(8), root=tmp_path)
    s = fr["sources"]
    assert s["que-feed-collect"]["health"] == "FRESH"
    assert s["dispatch-state-feed"]["health"] == "STALE"
    assert s["stall-gap-feed"]["health"] == "MISSING"
    assert s["governor-events"]["health"] == "MISSING"
    assert q.source_freshness(NOW, _ts(400), root=tmp_path)["sources"][
        "que-feed-collect"]["health"] == "STALE"


def test_exclusions_ghost_listed():
    ex = q.load_exclusions()
    assert 37655538554 in ex
    keep, dropped = q.split_excluded([{"id": 37655538554}, {"id": 1}], ex)
    assert [r["id"] for r in keep] == [1] and len(dropped) == 1
    import queue_pitcrew
    assert 37655538554 in queue_pitcrew.load_exclusions(
        str(HERE.parents[1] / "ops" / "queue" / "exclusions.json"))


def test_watchdog_score_row_stays_numeric():
    import auto_claim
    row = {"tier": {"index": 1}, "age_min": 90, "state": "escalated", "wall_in_min": None}
    row.update(task_ranking.score_dispatch(row))
    assert isinstance(row["score"], float)
    claims = [{"issue": 1, "score": row["score"]}, {"issue": 2, "score": None}]
    claims.sort(key=lambda c: (-(c["score"] or 0), c["issue"]))
    assert claims[0]["issue"] == 1
    assert hasattr(auto_claim, "plan")



def test_cadence_api_metrics(monkeypatch):
    class Response:
        status = 200
        headers = {
            "X-RateLimit-Remaining": "4998",
            "X-RateLimit-Limit": "5000",
            "X-RateLimit-Resource": "core",
        }

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"workflow_runs": []}'

    k.API_CALLS = 0
    k.API_STATUSES.clear()
    k.API_ROUTES.clear()
    k.API_LATENCIES_MS.clear()
    k.RATE_LIMIT.clear()
    monkeypatch.setattr(k.urllib.request, "urlopen", lambda *args, **kwargs: Response())
    result = k.gh("GET", "/repos/o/r/actions/workflows/que-feed-collect.yml/runs?per_page=10", "token")
    assert result == {"workflow_runs": []}
    assert k.API_CALLS == 1
    assert k.API_STATUSES == {"200": 1}
    assert k.RATE_LIMIT["x-ratelimit-remaining"] == "4998"
