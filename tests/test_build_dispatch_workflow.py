"""Contract tests for the build-dispatch port (issue #5108, parent #5096).

Text pins over `.github/workflows/build-dispatch.yml` (ported from
timerloggedout-spec/repo-story) and the claimable-route registry
`ops/dispatch/claimable-routes.json`. These pin the load-bearing shape:
SEC-03 mint-before-checkout with the Swarm App identity, both pullable
triggers, the pre-builder D-h/D-i receipt, failure surfacing, and the
model pin of record, the post-builder verify step (#5142: silent-empty
converts to FAILURE in-run, fail-open on unreadable evidence), and the
builder observability fix (debug logging + artifact upload), and the
failure-path observability legs (#5172: artifact upload on builder
failure, step-summary size guard, gemini_errors memory guard,
work-preservation checkpoint).
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "build-dispatch.yml"
REGISTRY = ROOT / "ops" / "dispatch" / "claimable-routes.json"


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_mint_step_after_builders_before_consumers():
    # SEC-03 redesign (accepted at the #5151 rebase adjudication, Desk
    # 2026-11-12): the builder steps never hold the App token. Checkout
    # runs on the read-only workflow token with persist-credentials off;
    # the narrowly-scoped Swarm App token is minted after all model
    # execution and before every step that consumes it (commit/PR,
    # verify).
    text = workflow_text()
    assert "actions/create-github-app-token@b60ed23e06e1e229cd0384bf542ad2781a8df21e" in text
    assert "Mint narrowly-scoped Swarm App token after all model execution (SEC-03)" in text
    mint = text.index("Mint narrowly-scoped Swarm App token")
    gemini_builder = text.index("Run Gemini CLI builder")
    generic_builder = text.index("Run the generic agent-loop builder")
    assert mint > gemini_builder and mint > generic_builder, \
        "the App token mint must follow all model execution"
    for consumer in ("Commit and open PR for the generic builder",
                     "Commit and open PR for Gemini builder",
                     "Verify build completion evidence"):
        assert mint < text.index(consumer), f"the App token mint must precede {consumer}"
    checkout = text.index("actions/checkout")
    assert "persist-credentials: false" in text[checkout:checkout + 400], \
        "checkout must not persist credentials"


def test_baseline_capture_step_and_output():
    # The verify step's evidence model rests on a run-start baseline:
    # the branch-resolution step captures baseline_sha (and started_at)
    # before any builder runs, and verify consumes the baseline output.
    text = workflow_text()
    assert "Resolve build branch and capture run baseline" in text
    start = text.index("Resolve build branch and capture run baseline")
    end = text.index("Select build arm")
    step = text[start:end]
    assert "id: branch" in step
    assert 'echo "baseline_sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"' in step
    assert 'echo "started_at=$(date -u' in step
    assert "BASE_BRANCH_SHA: ${{ steps.branch.outputs.baseline_sha }}" in text
    assert "BUILD_STARTED_AT: ${{ steps.branch.outputs.started_at }}" in text


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
    for needle in ("git/ref/heads/", "pulls?head=",
                   "build-dispatch-empty:v1", "exit 1",
                   "__UNREADABLE__", "fail_open",
                   "outcome=completed", "outcome=failed"):
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

def test_verify_never_accepts_inherited_branch_commits_as_completion():
    text = workflow_text()
    start = text.index("Verify build completion evidence")
    end = text.index("if: failure()", start)
    verify = text[start:end]
    assert 'if [ "$REF_SHA" != "$BASE_BRANCH_SHA" ]' in verify, (
        "branch evidence must require the ref to move vs the run-start baseline SHA"
    )
    assert "Existing branch commits and old PRs never" in verify
    assert "(p.get('created_at') or '') >= started" in verify, (
        "PR evidence must require a PR created during this run"
    )
    assert 'commits?sha=' not in verify, (
        "the branch commits endpoint includes inherited commits and cannot prove new output"
    )


def test_verify_checks_pr_even_when_branch_ref_is_missing():
    text = workflow_text()
    start = text.index("Verify build completion evidence")
    end = text.index("if: failure()", start)
    verify = text[start:end]
    ref_guard = verify.index('if [ "$REF" != "__NOT_FOUND__" ]')
    pr_check = verify.index('pulls?head=')
    assert pr_check > ref_guard
    assert "Check PRs even if the branch ref was deleted after merge" in verify

def test_verify_only_treats_missing_branch_ref_as_positive_empty():
    text = workflow_text()
    start = text.index("Verify build completion evidence")
    end = text.index("if: failure()", start)
    verify = text[start:end]
    assert 'not_found_is_empty="${2:-false}"' in verify
    assert 'gh_get "repos/$REPO/git/ref/heads/$BUILD_BRANCH" true' in verify
    assert 'BASE_BRANCH_SHA: ${{ steps.branch.outputs.baseline_sha }}' in verify
    assert 'if [ "$REF" != "__NOT_FOUND__" ]' in verify
    assert 'gh_get "repos/$REPO/pulls?head=$OWNER:$BUILD_BRANCH&state=all")' in verify
    assert 'if [ "$not_found_is_empty" = "true" ]' in verify
    assert "A 404 from compare/PR endpoints is not proof of emptiness" in verify

def test_builder_step_has_id_for_failure_path_outcome():
    text = workflow_text()
    assert "      - name: Run Gemini CLI builder\n        id: builder\n" in text


def test_failure_artifact_upload_step():
    text = workflow_text()
    assert "Upload Gemini CLI outputs on builder failure" in text
    start = text.index("Upload Gemini CLI outputs on builder failure")
    end = text.index("Checkpoint builder work to branch on failure")
    step = text[start:end]
    assert "always()" in step
    assert "steps.builder.outcome == 'failure'" in step
    assert "actions/upload-artifact@" in step
    assert "gemini-artifacts/" in step
    assert "if-no-files-found: warn" in step


def test_step_summary_size_guard():
    text = workflow_text()
    assert "Guard step-summary size (1024k cap)" in text
    start = text.index("Guard step-summary size (1024k cap)")
    end = text.index("Upload Gemini CLI outputs on builder failure")
    step = text[start:end]
    assert "if: always()" in step
    assert "GITHUB_STEP_SUMMARY" in step
    assert "1048576" in step  # the 1024k cap, in bytes
    assert "tail -c" in step


def test_checkpoint_step_fail_closed():
    text = workflow_text()
    assert "Checkpoint builder work to branch on failure" in text
    start = text.index("Checkpoint builder work to branch on failure")
    end = text.index("Verify build completion evidence")
    step = text[start:end]
    assert "always()" in step
    assert "steps.builder.outcome == 'failure'" in step
    assert "git commit" in step
    assert "git push" in step
    assert "--force" not in step
    assert "gh pr create" not in step
    assert "WIP checkpoint" in step


def test_no_builder_output_references_memory_guard():
    # #5172(c): the action maps its `error` output to
    # steps.gemini_run.outputs.gemini_errors, whose evaluation OOM'd at
    # multi-MB stderr. The workflow must never reference the builder
    # step's outputs in any expression.
    text = workflow_text()
    assert "steps.builder.outputs" not in text
