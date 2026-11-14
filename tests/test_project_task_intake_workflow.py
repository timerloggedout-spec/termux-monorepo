"""Project-task intake lifecycle label reconciliation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/project-task-dispatch.yml"


def test_successful_intake_clears_prior_incomplete_diagnosis():
    text = WORKFLOW.read_text(encoding="utf-8")
    valid = text.split("Post routing receipt + queue (valid intake)", 1)[1].split(
        "Post intake diagnosis (malformed intake)", 1
    )[0]
    assert "--add-label dispatch-queued" in valid
    assert "--remove-label intake-incomplete" in valid


def test_malformed_intake_keeps_explicit_diagnosis():
    text = WORKFLOW.read_text(encoding="utf-8")
    malformed = text.split("Post intake diagnosis (malformed intake)", 1)[1]
    assert "--add-label intake-incomplete" in malformed
