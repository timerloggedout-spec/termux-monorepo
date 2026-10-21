"""Static offline coverage of every Gemini CLI dispatch path."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CLI = "google-github-actions/run-gemini-cli@"


def test_all_gemini_cli_steps_have_strict_gate_and_adjacent_router_gate():
    found = []
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        if CLI not in path.read_text():
            continue
        docs = yaml.safe_load(path.read_text())
        for job in docs["jobs"].values():
            steps = job.get("steps", [])
            for i, step in enumerate(steps):
                if CLI not in step.get("uses", ""):
                    continue
                found.append(path.name)
                assert i > 0 and steps[i - 1].get("id") == "gemini_quota", path.name
                assert steps[i - 1].get("uses") == "./.github/actions/gemini-quota-gate"
                condition = step.get("if", "")
                assert "steps.router.outputs.skip != 'true'" in condition
                assert "steps.router.outputs.provider == 'gemini'" in condition
                assert "steps.gemini_quota.outputs.skip == 'false'" in condition
                assert steps[i - 1].get("with", {}).get("model") == "${{ steps.router.outputs.model }}"
    assert set(found) == {"gemini-invoke.yml", "gemini-review.yml", "gemini-triage.yml", "gemini-after-peers.yml"}


def test_gate_has_private_path_inputs_and_no_legacy_state_or_rotation():
    action = yaml.safe_load((ROOT / ".github/actions/gemini-quota-gate/action.yml").read_text())
    assert set(action["outputs"]) == {"skip", "reason", "use_backup_key"}
    assert set(action["inputs"]) == {"model", "credential-alias", "cap-policy-path", "project-evidence-path", "ledger-directory"}
    assert action["inputs"]["credential-alias"]["default"] == "primary"
    assert action["inputs"]["ledger-directory"]["default"] == "${{ runner.temp }}/gemini-shared-cap"
    body = (ROOT / ".github/actions/gemini-quota-gate/action.yml").read_text().lower()
    assert "actions/cache" not in body and "1450" not in body and "gemini_api_key_backup" not in body
    assert "python3 -m scripts.gemini_quota_gate" in body


def test_regression_workflow_runs_new_offline_tests_and_tracks_files():
    text = (ROOT / ".github/workflows/quota-router-regression.yml").read_text()
    for path in ["tests/test_gemini_quota_wiring.py", "tests/test_gemini_quota_gate.py", "tests/test_gemini_shared_cap.py"]:
        assert path in text
    for path in [".github/actions/gemini-quota-gate/action.yml", ".github/workflows/gemini-invoke.yml", ".github/workflows/gemini-review.yml", ".github/workflows/gemini-triage.yml", ".github/workflows/gemini-after-peers.yml", "scripts/gemini_quota_gate.py", "scripts/gemini_shared_cap.py"]:
        assert path in text
