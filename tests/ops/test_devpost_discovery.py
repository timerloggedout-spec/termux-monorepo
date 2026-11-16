from pathlib import Path
import json

from scripts.challenge.devpost_discovery import (
    canonical_event_url, parse_directory, triage_score, collect,
)


def test_collector_paginates_both_devpost_discovery_surfaces():
    assert len(SOURCES) == 10
    assert SOURCES[0] == "https://devpost.com/hackathons?page=1"
    assert SOURCES[-1] == "https://devpost.com/c/artificial-intelligence?page=5"


def test_only_devpost_event_subdomains_are_accepted():
    assert canonical_event_url("https://sample.devpost.com/", "https://devpost.com/hackathons") == "https://sample.devpost.com/"
    assert canonical_event_url("https://devpost.com/hackathons", "https://devpost.com") is None
    assert canonical_event_url("https://example.com/", "https://devpost.com") is None


def test_directory_parser_deduplicates_event_links_and_ignores_non_events():
    html = """
    <a href="/hackathons">Directory</a>
    <a href="https://alpha-ai.devpost.com/">Alpha AI Hackathon</a>
    <a href="https://alpha-ai.devpost.com/">Alpha AI</a>
    <a href="https://beta.devpost.com/">Beta Build</a>
    """
    rows = parse_directory(html, "https://devpost.com/hackathons")
    assert {r["url"] for r in rows} == {"https://alpha-ai.devpost.com/", "https://beta.devpost.com/"}
    assert next(r for r in rows if "alpha-ai" in r["url"])["title"] == "Alpha AI Hackathon"


def test_triage_is_explicitly_heuristic():
    score, terms = triage_score("Agentic AI Hackathon")
    assert score > 0
    assert "agent" in terms and "ai" in terms


def test_collect_preserves_review_state_and_never_promotes(tmp_path: Path):
    coordinator = tmp_path / "ops/challenge/coordinator.json"
    coordinator.parent.mkdir(parents=True)
    coordinator.write_text(json.dumps({"events": [], "candidate_events": []}))
    pages = {"https://devpost.com/hackathons": '<a href="https://alpha.devpost.com/">AI Agent Hackathon</a>'}
    first = collect(tmp_path, pages, "2026-11-16T00:00:00Z")
    feed_path = tmp_path / "ops/challenge/discovery/devpost-directory.json"
    feed = json.loads(feed_path.read_text())
    feed["leads"][0]["review_note"] = "needs eligibility check"
    feed_path.write_text(json.dumps(feed))
    collect(tmp_path, pages, "2026-11-17T00:00:00Z")
    updated = json.loads(feed_path.read_text())["leads"][0]
    assert first["discovered_this_run"] == 1
    assert updated["verification_state"] == "UNVERIFIED_LEAD"
    assert updated["eligibility_state"] == "NOT_ESTABLISHED"
    assert updated["review_note"] == "needs eligibility check"
    assert updated["first_seen"] == "2026-11-16T00:00:00Z"
    assert updated["last_seen"] == "2026-11-17T00:00:00Z"
    assert not updated.get("admitted")
