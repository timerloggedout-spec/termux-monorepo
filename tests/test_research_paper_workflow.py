"""Contracts for attributable, secret-free THUB-017/MSM-005 validation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/research-paper-validation.yml"


def test_workflow_tests_candidate_with_read_only_fixed_inputs():
    text = WORKFLOW.read_text()
    value = yaml.safe_load(text)
    assert value["permissions"] == {"contents": "read"}
    triggers = value.get("on", value.get(True))
    assert triggers["workflow_dispatch"] is None
    job = value["jobs"]["bounded-offline"]
    assert job["timeout-minutes"] <= 15
    steps = job["steps"]
    checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"]["ref"] == "${{ github.event.pull_request.head.sha || github.sha }}"
    assert checkout["with"]["persist-credentials"] is False
    for step in steps:
        if "uses" in step:
            assert re.fullmatch(r"[\w/-]+@[0-9a-f]{40}", step["uses"])
    for expected in ("test_advanced_research_runtime.py", "test_research_admission.py",
                     "test_research_telemetry.py", "test_paper_accounting.py",
                     "repo_gate.py", "termux_smoke.py", "research_paper_receipt.py"):
        assert expected in text
    assert "secrets." not in text
    assert "pull_request_target" not in text
    assert "--execute" not in text
    uploads = [s for s in steps if s.get("uses", "").startswith("actions/upload-artifact@")]
    assert len(uploads) == 1 and uploads[0]["if"] == "always()"


def test_receipt_binds_artifacts_source_and_commit(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    source = repo / "src/advanced_research_adapter.py"
    source.parent.mkdir()
    source.write_text("# fixture\n")
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"], check=True)
    artifact = tmp_path / "tests.xml"
    artifact.write_text("<testsuite/>\n")
    spec = importlib.util.spec_from_file_location("receipt", ROOT / "scripts/ci/research_paper_receipt.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("GITHUB_WORKFLOW_SHA", "a" * 40)
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    result = module.receipt(repo, [artifact])
    assert result["candidate_sha"] == subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    assert result["workflow_sha"] == "a" * 40
    assert result["source_sha256"]["src/advanced_research_adapter.py"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert result["artifact_sha256"]["tests.xml"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert result["task_outcome"] == "UNKNOWN"
    assert result["merged_or_deployed"] is False
    assert result["dirty_tracked_files"] is False
    json.dumps(result, allow_nan=False)
    source.write_text("# changed\n")
    assert module.receipt(repo, [artifact])["dirty_tracked_files"] is True
