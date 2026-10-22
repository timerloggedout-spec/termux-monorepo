"""Static contract checks for the remote, offline Swarms validation workflow."""
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT / ".github/workflows/swarms-validation.yml"


def load_workflow():
    # GitHub's `on` key is YAML 1.2 boolean-like text; PyYAML's YAML 1.1
    # resolver normally converts it to True, which this contract tolerates.
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_workflow_has_path_filtered_pr_push_and_dispatch():
    workflow = load_workflow()
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"pull_request", "push", "workflow_dispatch"}
    expected = {
        "src/swarms_*.py",
        "scripts/swarms/**",
        "integrations/swarms/**",
        "tests/test_swarms*.py",
        ".github/workflows/swarms-validation.yml",
    }
    assert set(triggers["pull_request"]["paths"]) == expected
    assert set(triggers["push"]["paths"]) == expected
    assert triggers["workflow_dispatch"] is None


def test_jobs_are_read_only_bounded_and_do_not_install_sdk():
    workflow = load_workflow()
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["jobs"]) == {"offline-contract", "rust-contract"}
    py_job = workflow["jobs"]["offline-contract"]
    assert py_job["timeout-minutes"] <= 10
    steps = py_job["steps"]
    checkouts = [step for step in steps
                 if step.get("uses", "").startswith("actions/checkout@")]
    assert checkouts and all(step.get("with", {}).get("persist-credentials") is False
                             for step in checkouts)
    install = next(s["run"] for s in steps if s.get("name") == "Install test-only dependencies")
    assert "pytest==" in install and "PyYAML==" in install
    assert "swarms" not in install.lower()
    assert "python -m pytest -q tests/test_swarms*.py" in "\n".join(
        step.get("run", "") for step in steps)
    assert py_job["timeout-minutes"] <= 10
    rust_job = workflow["jobs"]["rust-contract"]
    assert rust_job["timeout-minutes"] <= 20
    assert any("cargo test --locked" in step.get("run", "") for step in rust_job["steps"])


def test_manual_remote_run_is_fixed_fixture_without_user_inputs_or_secrets():
    workflow = load_workflow()
    rendered = WORKFLOW_PATH.read_text()
    dispatch = workflow.get("on", workflow.get(True))["workflow_dispatch"]
    assert dispatch is None  # no inputs; no arbitrary text can enter a shell
    assert "Synthetic offline validation fixture" in rendered
    assert "secrets." not in rendered
    assert "LLM_API_HUB" not in rendered
    assert "--execute" not in rendered
    assert "pip install" in rendered
    assert "integrations/swarms/requirements.txt" not in rendered
    assert "swarms" not in next(s["run"] for s in workflow["jobs"]["offline-contract"]["steps"]
                                  if s.get("name") == "Install test-only dependencies").lower()


def test_every_action_is_immutable_and_collection_dependencies_present():
    workflow = load_workflow()
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[\w/-]+@[0-9a-f]{40}", step["uses"])
    installs = [s.get("run", "") for s in workflow["jobs"]["offline-contract"]["steps"]]
    assert any("uvicorn==" in cmd for cmd in installs)
