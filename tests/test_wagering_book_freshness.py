import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ci" / "check_wagering_book_freshness.py"
SPEC = importlib.util.spec_from_file_location("wagering_book_freshness", SCRIPT)
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def _write_fixture(root, now):
    book_dir = root / "ops" / "agentic-gambling" / "book"
    money_dir = root / "ops" / "moneyball"
    mirror_dir = root / "apps" / "tribute-dashboard" / "data"
    fixture_dir = root / "tests" / "fixtures"
    for path in (book_dir, money_dir, mirror_dir, fixture_dir):
        path.mkdir(parents=True, exist_ok=True)

    stamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    start = "2026-11-02T00:00:00-08:00"
    wall = "2026-12-31T23:59:59-08:00"
    subject = {
        "id": "PROP-01",
        "window": {"window_start": start, "wall": wall},
        "expectation_record": {"prior": {"value": None}, "posterior": {"value": None}},
        "settle": {"value": None},
    }
    book = {"subjects": [subject], "settlements": [], "positions": []}
    bookfeed = {
        "subjects": [subject],
        "positions": [{"position_id": "P1"}],
        "settlements": [],
        "counts": {"subjects": 1, "expectation_records": 1, "positions": 1, "settlements": 0},
        "pct_block": {"computed_at": stamp},
    }
    feed = {
        "generated_at": stamp,
        "book": {"subjects": 1},
        "horizon": {"start": start, "end": wall},
        "subjects": [{"id": "PROP-01", "settlement": {"value": None}}],
        "positions": [{"position_id": "P1"}],
        "settlements": [],
        "ledger_ref": {"entries": 1},
        "pct_block": {"upstream_computed_at": stamp},
    }
    (book_dir / "challenges-book.json").write_text(json.dumps(book))
    (book_dir / "book-feed.json").write_text(json.dumps(bookfeed))
    (book_dir / "ledger.jsonl").write_text('{"event":"seed"}\n')
    rendered = json.dumps(feed, indent=1) + "\n"
    (money_dir / "wagering-book.json").write_text(rendered)
    (mirror_dir / "wagering-book.json").write_text(rendered)
    (fixture_dir / "wagering-book.fixture.json").write_text(rendered)
    return bookfeed, feed


def test_freshness_observer_passes_consistent_recent_sources(tmp_path):
    now = datetime(2026, 11, 23, 15, 50, tzinfo=timezone.utc)
    _write_fixture(tmp_path, now)
    result = CHECK.build_observation(tmp_path, now=now)
    assert result["status"] == "FRESH"
    assert result["failures"] == []


def test_freshness_observer_detects_stale_upstream_and_ledger_mismatch(tmp_path):
    now = datetime(2026, 11, 23, 15, 50, tzinfo=timezone.utc)
    bookfeed, feed = _write_fixture(tmp_path, now)
    old = "2026-11-01T00:00:00Z"
    bookfeed["pct_block"]["computed_at"] = old
    feed["pct_block"]["upstream_computed_at"] = old
    feed["ledger_ref"]["entries"] = 2
    book_dir = tmp_path / "ops" / "agentic-gambling" / "book"
    money_path = tmp_path / "ops" / "moneyball" / "wagering-book.json"
    mirror_path = tmp_path / "apps" / "tribute-dashboard" / "data" / "wagering-book.json"
    fixture_path = tmp_path / "tests" / "fixtures" / "wagering-book.fixture.json"
    (book_dir / "book-feed.json").write_text(json.dumps(bookfeed))
    rendered = json.dumps(feed, indent=1) + "\n"
    money_path.write_text(rendered)
    mirror_path.write_text(rendered)
    fixture_path.write_text(rendered)

    result = CHECK.build_observation(tmp_path, now=now)
    assert result["status"] == "STALE"
    assert "upstream_source_fresh" in result["failures"]
    assert "ledger_reference_matches" in result["failures"]
