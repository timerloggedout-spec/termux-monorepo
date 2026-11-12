"""Pins for the dispatch-executor workflow (#5176).

Run: python3 -m pytest tests/test_dispatch_executor_workflow.py
The machinery contract: scheduled + manual trigger, Swarm mint with
actions:write (to fire build-dispatch), decide via the repo script,
claim (comment + label) BEFORE fire, holds recorded in the receipt
artifact only (no per-hold comment flurry), executor errors stamped
on #5176.
"""

from pathlib import Path

import yaml

WF = Path(__file__).parent.parent / ".github" / "workflows" / "dispatch-executor.yml"


def _doc():
    return yaml.safe_load(WF.read_text())


def _steps():
    return _doc()["jobs"]["execute"]["steps"]


def _step(name_part):
    for s in _steps():
        if name_part in (s.get("name") or ""):
            return s
    raise AssertionError(f"no step named ~{name_part!r}")


def test_schedule_and_manual_trigger():
    doc = _doc()
    on = doc.get(True) or doc.get("on")
    assert on["schedule"][0]["cron"] == "*/15 * * * *"
    assert "max_conversions" in on["workflow_dispatch"]["inputs"]
    assert on["workflow_dispatch"]["inputs"]["max_conversions"]["default"] == "1"


def test_mint_scopes_cover_claim_and_fire():
    mint = _step("Mint Termux Fleet Swarm token")
    assert mint["uses"].startswith("actions/create-github-app-token")
    with_ = mint["with"]
    assert with_["permission-issues"] == "write"
    assert with_["permission-actions"] == "write"
    assert with_["permission-contents"] == "read"


def test_decide_uses_repo_script_and_feeds():
    step = _step("Decide (executor)")
    run = step["run"]
    assert "scripts/ops/dispatch_executor.py decide" in run
    assert "ops/dispatch/build-arms.json" in run
    assert "ops/que/feeds/arm-census.json" in run
    assert "--max-conversions" in run


def test_claim_precedes_fire_in_one_step():
    step = _step("Claim + fire")
    run = step["run"]
    claim = run.index("gh issue comment")
    label = run.index("gh issue edit")
    fire = run.index("gh workflow run build-dispatch.yml")
    assert claim < label < fire
    assert '-f arm="$arm"' in run and '-f quota_class="$qc"' in run
    assert step["if"] == "inputs.dry_run != true"


def test_holds_leave_no_comment_step():
    names = [s.get("name") or "" for s in _steps()]
    assert not any("hold" in n.lower() and "comment" in n.lower() for n in names)


def test_executor_error_stamped_on_filing_of_record():
    step = _step("Stamp executor error on #5176")
    assert step["if"] == "failure()"
    assert "gh issue comment 5176" in step["run"]


def test_no_hard_selected_arm():
    text = WF.read_text()
    assert "gemini-cli" not in text
