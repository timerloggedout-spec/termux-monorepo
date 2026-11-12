"""Pins for the ListingLens video-render workflow (#5137).

Run: python3 -m pytest tests/test_video_render_workflow.py
The machinery contract: dispatch-only trigger, the REAL demo run is
the capture of record, beats/receipt helpers are the repo scripts,
MP4 + receipt go up as artifacts, and the receipt comment rides the
Swarm App token (never the shared bucket, never a Gemini draw).
"""

from pathlib import Path

import yaml

WF = Path(__file__).parent.parent / ".github" / "workflows" / "video-render.yml"


def _doc():
    return yaml.safe_load(WF.read_text())


def _steps():
    return _doc()["jobs"]["render"]["steps"]


def _step(name_part):
    for s in _steps():
        if name_part in (s.get("name") or ""):
            return s
    raise AssertionError(f"no step named ~{name_part!r}")


def test_dispatch_trigger_with_target_issue_default():
    doc = _doc()
    on = doc.get(True) or doc.get("on")  # YAML 1.1 parses `on:` as True
    dispatch = on["workflow_dispatch"]
    assert dispatch["inputs"]["issue_number"]["default"] == "5124"


def test_real_demo_run_is_the_capture():
    step = _step("Run the REAL ListingLens demo")
    run = step["run"]
    assert "node apps/listinglens/demo/run-demo.mjs" in run
    assert "demo-output.txt" in run
    assert "DEMO OK" in run  # fail-closed if the demo run breaks


def test_beats_and_receipt_come_from_repo_helpers():
    derive = _step("Derive the beats manifest")
    assert "scripts/listinglens/derive_manifest.py" in derive["run"]
    render = _step("Render frames + assemble MP4")
    assert "scripts/listinglens/render_frames.py" in render["run"]
    probe = _step("Probe + build the receipt")
    assert "ffprobe" in probe["run"]
    assert "scripts/listinglens/build_receipt.py" in probe["run"]


def test_artifacts_and_receipt_comment():
    pub = _step("Publish MP4 + receipt artifacts")
    assert pub["uses"].startswith("actions/upload-artifact")
    paths = pub["with"]["path"]
    assert "listinglens-demo.mp4" in paths and "receipt.json" in paths
    comment = _step("Post the receipt on the target issue")
    assert "gh issue comment" in comment["run"]
    assert comment["env"]["GH_TOKEN"] == "${{ steps.swarm.outputs.token }}"


def test_ffmpeg_installed_before_render():
    # Run 43236477759: the ubuntu-26.04 runner image ships no ffmpeg;
    # the workflow must install it (plus DejaVu for drawtext) before
    # the render step runs.
    names = [s.get("name") or "" for s in _steps()]
    install = next(i for i, n in enumerate(names) if "Install ffmpeg" in n)
    render = next(i for i, n in enumerate(names) if "Render frames" in n)
    assert install < render
    assert "ffmpeg" in _steps()[install]["run"]


def test_no_gemini_no_generation_services():
    text = WF.read_text()
    assert "gemini" not in text.lower()
    mint = _step("Mint Termux Fleet Swarm token")
    assert mint["uses"].startswith("actions/create-github-app-token")
