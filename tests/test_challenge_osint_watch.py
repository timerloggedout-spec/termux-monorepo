import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "challenge" / "osint_watch.py"
SPEC = importlib.util.spec_from_file_location("challenge_osint_watch", SCRIPT)
WATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WATCH)


def test_records_to_watch_separates_events_and_candidates():
    records = list(WATCH.records_to_watch({
        "events": [{"id": "D1"}],
        "candidate_events": [{"id": "C18"}],
    }))
    assert records == [("event", {"id": "D1"}),
                       ("candidate", {"id": "C18"})]


def test_candidate_coverage_counts_dates_prizes_and_watch_sources():
    record = {
        "id": "C18",
        "status": "upcoming — submissions open",
        "host": "PICO",
        "dates": {"window": "Nov 18–Feb 1", "kickoff": "Nov 24"},
        "prizes": {"pool": "$50,000", "tiers": "32 prizes"},
        "constraints": ["18+", "eligible country"],
        "gates": ["Devpost registration", "PICO developer account"],
        "watch_sources": [
            {"label": "program", "url": "https://example.test/program"},
            {"label": "rules", "url": "https://example.test/rules"},
        ],
    }
    coverage = WATCH.coverage_of(record, "candidate")
    assert coverage["record_type"] == "candidate"
    assert coverage["dates"] == 2
    assert coverage["prizes"] == {"status": "ESTABLISHED", "tiers": 1}
    assert coverage["rules_constraints"] == 4
    assert coverage["page_watch_urls"] == 2
    assert coverage["official_page_watch"] is True


def test_main_watches_candidate_sources_and_deduplicates(tmp_path, monkeypatch):
    root = tmp_path
    osint = root / "ops" / "challenge" / "osint"
    osint.mkdir(parents=True)
    (root / "ops" / "challenge" / "coordinator.json").write_text(
        json.dumps({
            "events": [{"id": "D1", "official_url": "https://example.test/d1"}],
            "candidate_events": [{
                "id": "C18",
                "watch_sources": [
                    {"label": "program", "url": "https://example.test/pico"},
                    {"label": "rules", "url": "https://example.test/rules"},
                ],
            }],
        })
    )
    (osint / "snapshots.json").write_text('{"snapshots": []}\n')
    monkeypatch.setattr(WATCH, "fetch_text", lambda url: "stable " + url)

    assert WATCH.main(["--root", str(root)]) == 0
    coverage = json.loads((osint / "coverage.json").read_text())
    snapshots = json.loads((osint / "snapshots.json").read_text())["snapshots"]
    assert "C18" in coverage["candidates"]
    assert coverage["summary"]["candidates"] == 1
    assert len([s for s in snapshots if s["record_type"] == "candidate"]) == 2
    assert {s["source_label"] for s in snapshots if s["event"] == "C18"} == {
        "program", "rules"
    }

    assert WATCH.main(["--root", str(root)]) == 0
    snapshots_again = json.loads((osint / "snapshots.json").read_text())["snapshots"]
    assert len(snapshots_again) == len(snapshots)
