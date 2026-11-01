import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "doe"))
import nc1_continuous_log as log  # noqa: E402


def _rows():
    return [
        {"unit_id": "a", "stratum": "chat", "density": 0.10,
         "tokens_scanned": 100, "layer": "L2",
         "layer_verdict": {"drift": True, "borderline": False, "score": 0.2}},
        {"unit_id": "b", "stratum": "chat", "density": 0.30,
         "tokens_scanned": 300, "layer": "L2",
         "layer_verdict": {"drift": False, "borderline": True, "score": 0.45}},
        {"unit_id": "c", "stratum": "records", "density": 0.0,
         "tokens_scanned": 50, "layer": "L3",
         "layer_verdict": {"drift": True, "borderline": False, "score": 0.1},
         "class_hint": "empty-signal"},
    ]


def test_aggregate_strata():
    per = log.aggregate(_rows())
    assert per["chat"]["n"] == 2
    assert per["chat"]["density_mean"] == 0.2
    assert per["chat"]["tokens_total"] == 400
    assert per["chat"]["layer_verdicts"]["drift"] == 1
    assert per["chat"]["layer_verdicts"]["borderline"] == 1
    assert per["chat"]["layer_verdicts"]["score_mean"] == 0.325
    assert per["records"]["class_hints"] == {"empty-signal": 1}
    assert "github" not in per  # absent strata omitted, not zero-filled


def test_run_appends_both_logs(tmp_path):
    pop = tmp_path / "pop"
    pop.mkdir()
    (pop / "shakedown-001-units.jsonl").write_text(
        "\n".join(json.dumps(r) for r in _rows()) + "\n")
    logs = tmp_path / "logs"
    line = log.run(pop, logs, "2026-11-01T00:00:00Z")
    assert line["status"] == "ok" and line["population_units"] == 3
    pop_lines = (logs / "population-log.jsonl").read_text().splitlines()
    den_lines = (logs / "density-stats.jsonl").read_text().splitlines()
    assert len(pop_lines) == 1 and len(den_lines) == 2
    log.run(pop, logs, "2026-11-02T00:00:00Z")  # append-only: grows
    assert len((logs / "population-log.jsonl").read_text().splitlines()) == 2


def test_defer_line_shape(tmp_path):
    line = log.defer(tmp_path / "logs", "2026-11-01T00:00:00Z", "boom")
    assert line["status"] == "DEFER" and line["reason"] == "boom"
    saved = json.loads((tmp_path / "logs" / "population-log.jsonl").read_text())
    assert saved["status"] == "DEFER"


def test_population_hash_stable():
    assert log.population_hash(_rows()) == log.population_hash(_rows()[::-1])


if __name__ == "__main__":
    import tempfile
    test_aggregate_strata()
    with tempfile.TemporaryDirectory() as d:
        test_run_appends_both_logs(Path(d))
    with tempfile.TemporaryDirectory() as d:
        test_defer_line_shape(Path(d))
    test_population_hash_stable()
    print("ok 4 tests")
