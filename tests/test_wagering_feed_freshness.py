"""Freshness and regeneration contract for the public wagering feed."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts/moneyball/wagering_book_feed.py"
VALIDATOR = ROOT / "scripts/moneyball/validate_wagering_book_feed.py"
WORKFLOW = ROOT / ".github/workflows/tribute-dashboard-deploy.yml"
NOW = "2026-11-25T12:00:00Z"


def _copies(tmp_path, generated_at):
    payload = json.dumps({
        "schema": "moneyball.wagering-book/v2",
        "generated_at": generated_at,
        "pct_block": {"computed_at": generated_at},
    }, indent=1) + "\n"
    paths = [tmp_path / name for name in ("feed.json", "mirror.json", "fixture.json")]
    for path in paths:
        path.write_text(payload)
    return paths


def _validate(paths):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--feed", str(paths[0]),
         "--mirror", str(paths[1]), "--fixture", str(paths[2]),
         "--max-age-hours", "48", "--now", NOW],
        capture_output=True, text=True)


def test_feed_is_stale_at_48_hours(tmp_path):
    paths = _copies(tmp_path, "2026-11-23T12:00:00Z")
    result = _validate(paths)
    assert result.returncode == 1
    assert "stale" in (result.stdout + result.stderr).lower()


def test_validator_rejects_future_and_timezone_naive_timestamps(tmp_path):
    for stamp, message in (("2026-11-26T12:00:00Z", "future"),
                           ("2026-11-25T11:00:00", "timezone")):
        paths = _copies(tmp_path, stamp)
        result = _validate(paths)
        assert result.returncode == 1
        assert message in (result.stdout + result.stderr).lower()


def test_validator_requires_pct_block_timestamp_to_match(tmp_path):
    paths = _copies(tmp_path, "2026-11-25T11:00:00Z")
    feed = json.loads(paths[0].read_text())
    del feed["pct_block"]
    paths[0].write_text(json.dumps(feed))
    missing = _validate(paths)
    assert missing.returncode == 1
    assert "pct_block" in (missing.stdout + missing.stderr).lower()

    paths = _copies(tmp_path, "2026-11-25T11:00:00Z")
    feed = json.loads(paths[0].read_text())
    feed["pct_block"]["computed_at"] = "2026-11-25T10:00:00Z"
    paths[0].write_text(json.dumps(feed))
    mismatched = _validate(paths)
    assert mismatched.returncode == 1
    assert "computed_at" in (mismatched.stdout + mismatched.stderr).lower()


def test_fresh_feed_requires_identical_mirror_and_fixture(tmp_path):
    paths = _copies(tmp_path, "2026-11-23T13:00:00Z")
    result = _validate(paths)
    assert result.returncode == 0, result.stderr

    paths[2].write_text(paths[2].read_text() + " ")
    drift = _validate(paths)
    assert drift.returncode == 1
    assert "fixture" in (drift.stdout + drift.stderr).lower()


def test_generator_refreshes_feed_mirror_and_fixture_from_sources(tmp_path):
    outputs = [tmp_path / name for name in ("feed.json", "mirror.json", "fixture.json")]
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--root", str(ROOT),
         "--out", str(outputs[0]), "--mirror", str(outputs[1]),
         "--fixture", str(outputs[2])],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert outputs[0].read_bytes() == outputs[1].read_bytes() == outputs[2].read_bytes()
    feed = json.loads(outputs[0].read_text())
    amd20 = next(s for s in feed["subjects"] if s["id"].startswith("AMD-20-"))
    assert amd20["settlement"]["value"] is None


def test_deploy_workflow_refreshes_feed_on_source_changes_and_before_publication():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    for path in (
        "ops/agentic-gambling/book/book-feed.json",
        "ops/agentic-gambling/book/challenges-book.json",
        "ops/agentic-gambling/book/ledger.jsonl",
        "scripts/moneyball/wagering_book_feed.py",
        "scripts/moneyball/validate_wagering_book_feed.py",
    ):
        assert path in workflow
    assert workflow.count("python3 scripts/moneyball/wagering_book_feed.py") == 2
    assert workflow.count("python3 scripts/moneyball/validate_wagering_book_feed.py") == 2
    assert workflow.count("--fixture tests/fixtures/wagering-book.fixture.json") == 2
