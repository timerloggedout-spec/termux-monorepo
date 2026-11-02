"""Stamp fan-out: one canonical stamp populates every plane's intake."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMITTER = ROOT / "scripts/dispatch/stamp_fanout.py"
SHA = "a" * 40

STAMP = {
    "dispatch_id": "test-dispatch-0001",
    "ts": "2026-11-01T00:00:00Z",
    "task_class": "certifications-unit",
    "entry": "506",
    "trigger": "workflow_dispatch",
    "provider": "cohere",
    "model": "command-a-03-2025",
    "role": "builder",
    "moniker": "optimizations-assurance",
    "context": "certifications-unit l1-relational-databases-v9/what-is-ci-cd",
    "run": {"workflow": "cert-unit.yml", "run_id": "41364184062", "session_id": None},
    "outcome": {"status": "completed", "summary": "unit ok", "artifact": "issue 506 comment",
                "gate_call": None, "confirmed": None},
    "quota": {"pool": "cohere-free-tier", "cost_class": "free-tier", "slice": None},
    "baseline_sha": SHA,
    "candidate_sha": SHA,
}


def _run(tmp_path):
    (tmp_path / "ops/challenge").mkdir(parents=True, exist_ok=True)
    feed = tmp_path / "ops/challenge/desk-feed.json"
    if not feed.exists():
        feed.write_text(json.dumps({"traversals": []}))
    stamp_file = tmp_path / "stamp.json"
    stamp_file.write_text(json.dumps(STAMP))
    return subprocess.run(
        [sys.executable, str(EMITTER), "--stamp", str(stamp_file), "--root", str(tmp_path)],
        capture_output=True, text=True, cwd=ROOT)


def test_fanout_populates_all_intakes(tmp_path):
    proc = _run(tmp_path)
    assert proc.returncode == 0, proc.stderr
    # 3L0
    rec = json.loads((tmp_path / "ops/3l0/intake.jsonl").read_text().strip())
    assert rec["schema"] == "3l0-intake/v1"
    assert rec["provider"] == "cohere" and rec["model"] == "command-a-03-2025"
    assert rec["run"]["run_id"] == "41364184062"
    assert rec["quota"]["cost_class"] == "free-tier"
    assert rec["instance"]["instance_key"] == "NOT_ESTABLISHED"  # no tuple in stamp -> honest NE
    # MoneyBall: a valid moneyball-plane/v2 record (quantities unidentified)
    mb = json.loads((tmp_path / "ops/moneyball/routed-dispatch/test-dispatch-0001.json").read_text())
    assert mb["schema"] == "moneyball-plane/v2"
    assert abs(sum(mb["weights"]["axes"].values()) - 1.0) < 1e-9
    comp = sum(mb["weights"]["axes"][a["axis"]] * a["value"] for a in mb["axes"])
    assert abs(comp - mb["composite"]) <= 0.05
    assert all(mb["quantities"][k] is None for k in
               ("capability", "forecast", "incremental_effect", "value", "surplus",
                "portfolio_marginal_contribution"))
    validator = ROOT / "scripts/moneyball/moneyball_v2.py"
    if validator.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("mbv2", validator)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        assert mod.validate_v2(mb) == [], mod.validate_v2(mb)
    # EXPERIMENT record (DoE + MVT/ATES)
    exp = json.loads((tmp_path / "experiments/doe/routed-dispatch/records/test-dispatch-0001.json").read_text())
    for key in ("schema_version", "experiment_id", "observed_at", "baseline_sha",
                "candidate_sha", "suite", "treatment", "status", "provenance", "confidence"):
        assert key in exp, key
    assert exp["baseline_sha"] == SHA and exp["status"] == "passed"
    assert exp["usage"]["value"] is None  # never fabricated
    assert exp["treatment"]["provider"] == "cohere"
    # DoE desk-feed carrier
    feed = json.loads((tmp_path / "ops/challenge/desk-feed.json").read_text())
    trav = [t for t in feed["traversals"] if t["entry"] == "routed-dispatch"]
    assert trav and trav[0]["provider_usage"][0]["provider"] == "cohere"


def test_fanout_idempotent(tmp_path):
    assert _run(tmp_path).returncode == 0
    proc = _run(tmp_path)
    assert proc.returncode == 0
    assert "already emitted" in proc.stdout
    lines = (tmp_path / "ops/3l0/intake.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1


def test_outcome_fill_updates_record_without_duplicates(tmp_path):
    assert _run(tmp_path).returncode == 0
    fill = {"dispatch_id": STAMP["dispatch_id"],
            "outcome_fill": {"first_pass_success": True, "rework_cycles": 0,
                             "dispatch_to_pr_wall_time": 3600,
                             "stalled_action_required": False, "pr": 3369}}
    fill_file = tmp_path / "fill.json"
    fill_file.write_text(json.dumps(fill))
    proc = subprocess.run(
        [sys.executable, str(EMITTER), "--stamp", str(fill_file), "--root", str(tmp_path),
         "--phase", "outcome"], capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    exp = json.loads((tmp_path / "experiments/doe/routed-dispatch/records/test-dispatch-0001.json").read_text())
    assert exp["metrics"]["first_pass_success"] is True
    assert exp["metrics"]["pr"] == 3369
    # append-only intakes untouched by the fill
    assert len((tmp_path / "ops/3l0/intake.jsonl").read_text().strip().splitlines()) == 1
