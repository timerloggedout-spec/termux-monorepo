"""Behavioral contract for the Brain BioFeedBack event-raster chart."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "apps/project-pages-hub/brain-ops/index.html"
SIGNAL = ROOT / "apps/project-pages-hub/brain-ops/signal.js"

SIM = r"""
const signal = require(process.argv[2]);
const runs = [
  {
    id: 170017, name: "Brain Kernel CI", run_number: 17, created_at: "2026-11-21T01:00:00Z",
    status: "completed", conclusion: "success", run_started_at: "2026-11-21T01:00:02Z",
    updated_at: "2026-11-21T01:02:02Z", head_sha: "a".repeat(40)
  },
  {
    id: 80008, name: "MOSAIC Adapter", run_number: 8, created_at: "2026-11-21T02:00:00Z",
    status: "completed", conclusion: "failure", run_started_at: "2026-11-21T02:00:02Z",
    updated_at: "2026-11-21T02:01:02Z", head_sha: "b".repeat(40)
  },
  {
    id: 90009, name: "<script>alert(1)</script>", run_number: 9, created_at: "2026-11-21T03:00:00Z",
    status: "in_progress", conclusion: null, head_sha: "c".repeat(40)
  }
];
const svg = signal.render(runs);
console.log(JSON.stringify({
  svg: svg,
  empty: signal.render([]),
  malformed: signal.render([{name: "bad timestamp", created_at: "unknown"}])
}));
"""


@pytest.mark.skipif(not shutil.which("node"), reason="Node required")
def test_brain_signal_raster_uses_observed_events(tmp_path):
    sim = tmp_path / "sim.cjs"
    sim.write_text(SIM, encoding="utf-8")
    result = subprocess.run(
        ["node", str(sim), str(SIGNAL)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    rendered = json.loads(result.stdout)
    svg = rendered["svg"]
    assert '<svg class="brain-signal-chart"' in svg
    assert 'role="img"' in svg
    assert "Brain Kernel CI" in svg
    assert "MOSAIC Adapter" in svg
    assert "signal-success" in svg
    assert "signal-failure" in svg
    assert "signal-pending" in svg
    assert "2026-11-21T01:00:00.000Z" in svg
    assert "2026-11-21 01:00" in svg
    assert "run id 170017" in svg
    assert "SHA aaaaaaaaaaaa" in svg
    assert "&lt;script&gt;" in svg
    assert "<script>" not in svg
    assert "Awaiting observed Brain workflow events" in rendered["empty"]
    assert "Awaiting observed Brain workflow events" in rendered["malformed"]


def test_brain_operations_page_wires_biofeedback_to_live_actions_data():
    html = PAGE.read_text(encoding="utf-8")
    assert '<script src="./signal.js"></script>' in html
    assert 'id="signal-chart"' in html
    assert 'id="signal-meta"' in html
    assert "BioFeedBack" in html
    assert "BrainSignal.render(all)" in html
    assert "GitHub Actions public workflow-run metadata" in html
    assert "EEG-inspired event raster" in html
