from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_operator_wake_exposes_only_allowlisted_provider_availability_dispatch():
    text = (ROOT / ".github/workflows/operator-wake.yml").read_text()
    workflow = yaml.safe_load(text)
    events = workflow.get("on", workflow.get(True))
    assert "issue_comment" in events and "workflow_dispatch" in events
    choices = events["workflow_dispatch"]["inputs"]["command"]["options"]
    assert "wake-provider-availability" in choices
    job = workflow["jobs"]["operate"]
    assert "secrets.ARCHWIZ_GITHUB_TOKEN" in job["env"]["GH_TOKEN"]
    assert "secrets.OPERATOR_GITHUB_TOKEN" in job["env"]["GH_TOKEN"]
    assert "secrets.OPERATOR_TOKEN" in job["env"]["GH_TOKEN"]
    run = next(step["run"] for step in job["steps"] if step.get("id") == "exec")
    assert "gh workflow run provider-availability.yml" in run
    assert "--ref master" in run
    assert "workflow_dispatch" in run
    assert "wake-provider-availability" in run
    assert "echo $GH_TOKEN" not in run and "printf '%s' \"$GH_TOKEN\"" not in run
    assert "provider-availability.yml" in text
