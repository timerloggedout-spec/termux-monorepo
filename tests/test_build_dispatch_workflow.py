"""Contract tests for the build-dispatch port (issue #5108, parent #5096).

Text pins over `.github/workflows/build-dispatch.yml` (ported from
timerloggedout-spec/repo-story) and the claimable-route registry
`ops/dispatch/claimable-routes.json`. These pin the load-bearing shape:
SEC-03 mint-before-checkout with the Swarm App identity, both pullable
triggers, the pre-builder D-h/D-i receipt, failure surfacing, and the
model pin of record, the post-builder verify step (#5142: silent-empty
converts to FAILURE in-run, fail-open on unreadable evidence), and the
builder observability fix (debug logging + artifact upload).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-dispatch.yml"
REGISTRY = ROOT / "ops" / "dispatch" / "claimable-routes.json"


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_mint_step_precedes_checkout():
    text = workflow_text()
    assert "actions/create-github-app-token@b60ed23e06e1e229cd0384bf542ad2781a8df21e" in text
    mint = text.index("create-github-app-token")
    checkout = text.index("actions/checkout")
    assert mint < checkout, "SEC-03: the App token mint must precede checkout"


def test_swarm_app_identity_not_client_id():
    text = workflow_text()
    assert "app-id: ${{ vars.TERMUX_FLEET_SWARM_APP_ID }}" in text
    assert "private-key: ${{ secrets.TERMUX_FLEET_SWARM_PRIVATE_KEY }}" in text
    assert "client-id:" not in text


def test_both_pullable_triggers_present():
    text = workflow_text()
    # Trigger 1: issue_comment "@gemini-cli /build" from trusted associations.
    assert "issue_comment:" in text
    assert "startsWith(github.event.comment.body, '@gemini-cli /build')" in text
    for assoc in ('"OWNER"', '"MEMBER"', '"COLLABORATOR"'):
        assert assoc in text
    assert "github.event.comment.author_association" in text
    # Trigger 2: workflow_dispatch with a required issue_number input.
    assert "workflow_dispatch:" in text
    assert "issue_number:" in text


def test_receipt_step_precedes_builder_and_carries_heartbeat():
    text = workflow_text()
    assert "build-dispatch-receipt:v1" in text
    assert "heartbeat_deadline" in text
    assert "fired_by" in text
    assert "run_id" in text
    receipt = text.index("heartbeat_deadline")
    builder = text.index("uses: google-github-actions/run-gemini-cli")
    assert receipt < builder, "the D-h receipt must be posted before the builder runs"


def test_failure_surfacing_present():
    text = workflow_text()
    assert "if: failure()" in text
    assert "FAILED" in text


def test_model_pin_of_record():
    text = workflow_text()
    assert "google-github-actions/run-gemini-cli@f77273f4c914e4bf38440cf36a0369cb64a37489" in text
    assert "gemini_model: 'gemini-3.5-flash-lite'" in text
    assert "gemini_api_key: ${{ secrets.GEMINI_API_KEY }}" in text


def test_registry_parses_and_names_all_routes():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert data["schema"] == "claimable-routes/v1"
    routes = {row["route"] for row in data["routes"]}
    assert routes == {
        "build-dispatch",
        "project-task-dispatch",
        "game-development-dispatch",
        "provider-command-dispatch",
    }
    for row in data["routes"]:
        for field in ("route", "workflow", "trigger", "inputs", "producer_class", "receipt"):
            assert field in row, f"{row.get('route')} missing registry field {field}"
        assert (ROOT / row["workflow"]).exists(), f"registered workflow missing: {row['workflow']}"


def test_registry_build_dispatch_row_matches_workflow():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    row = next(r for r in data["routes"] if r["route"] == "build-dispatch")
    kinds = {t["kind"] for t in row["trigger"]}
    assert kinds == {"issue_comment", "workflow_dispatch"}
    comment = next(t for t in row["trigger"] if t["kind"] == "issue_comment")
    assert comment["prefix"] == "@gemini-cli /build"
    assert row["inputs"]["issue_number"]["required"] is True

def test_verify_step_exists_runs_after_builder_and_before_failure_step():
    text = workflow_text()
    assert "Verify build completion evidence" in text
    builder = text.index("uses: google-github-actions/run-gemini-cli")
    verify = text.index("Verify build completion evidence")
    failure = text.index("if: failure()")
    assert builder < verify < failure, "the verify step must run after the builder and before failure surfacing"


def test_verify_step_contains_evidence_reads_and_exit_1():
    text = workflow_text()
    start = text.index("Verify build completion evidence")
    end = text.index("if: failure()")
    verify = text[start:end]
    for needle in ("git/ref/heads/", "compare/master...", "pulls?head=",
                   "commits?sha=", "ahead_by", "build-dispatch-empty:v1",
                   "exit 1"):
        assert needle in verify, f"verify step missing: {needle}"


def test_verify_step_fail_open_guard_present():
    text = workflow_text()
    start = text.index("Verify build completion evidence")
    end = text.index("if: failure()")
    verify = text[start:end]
    assert "fail-open" in verify.lower()
    assert "__UNREADABLE__" in verify
    assert "fail_open" in verify


def test_observability_fix_on_builder_step():
    text = workflow_text()
    start = text.index("uses: google-github-actions/run-gemini-cli")
    end = text.index("Verify build completion evidence")
    builder = text[start:end]
    assert "gemini_debug: 'true'" in builder
    assert "upload_artifacts: true" in builder
