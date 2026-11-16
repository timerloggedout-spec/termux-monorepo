"""Registry-feed repair (2026-11-15): aliases/host, submission-wall
timebox anchor, terminal/archived rows, freshness flag."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "opportunities"))
sys.path.insert(0, str(ROOT / "scripts" / "que"))

import opportunity_cycle as oc  # noqa: E402
import que_feed_collect as qfc  # noqa: E402
import task_ranking  # noqa: E402


def test_wall_anchors_to_deadline_not_winners():
    rec = {"dates": {"deadline": "2026-11-19T20:00:00Z", "winners_at": "2026-11-20T19:30:00Z"}}
    wall, src = oc.find_wall(rec)
    assert src == "dates.deadline"
    box = oc.derive_timebox(wall)
    assert box["escalation"] < box["wall"] == "2026-11-19T20:00:00Z"


def test_search_aliases_carry_sponsor_terms():
    _, aliases, terms = oc.search_aliases({"name": "AMD AI League", "host": "AMD x lablab.ai"})
    assert "AMD x lablab.ai" in aliases and "amd" in terms and "lablab.ai" in terms
    _, _, terms = oc.search_aliases({"name": "Kiroween 2026", "host": "Devpost (Kiro)"})
    assert "kiroween" in terms and "2026" not in terms


def test_screened_and_archived_states_are_terminal():
    for s in ("SCREENED OUT this cycle", "archived — x", "promoted ⇒ D1", "lapsed — y"):
        assert task_ranking.is_terminal_state(s)
    assert not task_ranking.is_terminal_state("registering")


def test_terminal_records_file_covers_c1_to_c10_and_d1_d2():
    doc = json.loads((ROOT / "ops/challenge/terminal-records.json").read_text())
    assert {a["id"] for a in doc["archived"]} == {f"C{i}" for i in range(1, 11)}
    assert {r["id"] for r in doc["terminal_records"]} >= {"D1", "D2"}


def test_staleness_flag_flips_after_fresh_until(tmp_path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"generated_at": "2026-11-14T18:46:00Z",
                             "fresh_until": "2026-11-15T06:46:00Z", "stale": False}))
    assert qfc.mark_opportunity_staleness(datetime(2026, 11, 15, 7, 0, tzinfo=timezone.utc), p) is True
    assert json.loads(p.read_text())["stale"] is True
    assert qfc.mark_opportunity_staleness(datetime(2026, 11, 15, 6, 0, tzinfo=timezone.utc), p) is False
