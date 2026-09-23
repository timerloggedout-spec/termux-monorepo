from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"


def workflow(name):
    return (WORKFLOWS / name).read_text()


def test_freshness_workflow_triggers_automatically_and_stays_read_only():
    content = workflow("context-relationship-linear-freshness.yml")

    # Automatic triggers per docs/LINEAR-AGENT-PROTOCOL.md §3, not just manual.
    assert "pull_request:" in content
    assert "branches:" in content
    assert "master-staging" in content
    assert "push:" in content
    assert "workflow_dispatch:" in content

    # Still read-only and non-blocking (Tier 0-2 cooperative model): no
    # required status gate, only reads repo contents, writes only a summary.
    assert "contents: read" in content
    assert "persist-credentials: false" in content
    assert "GITHUB_STEP_SUMMARY" in content
    assert "contents: write" not in content
    assert "pull_request_target" not in content


def test_freshness_workflow_defaults_max_issues_for_non_dispatch_triggers():
    content = workflow("context-relationship-linear-freshness.yml")

    # inputs.max_issues is only populated on workflow_dispatch; pull_request
    # and push triggers must not crash on an empty/undefined input.
    assert "inputs.max_issues || '100'" in content


def test_freshness_workflow_scopes_concurrency_per_pr():
    content = workflow("context-relationship-linear-freshness.yml")

    assert "concurrency:" in content
    assert "github.event.pull_request.number" in content


def test_implements_tag_check_workflow_is_advisory_only():
    content = workflow("linear-implements-tag-check.yml")

    assert "pull_request:" in content
    assert "contents: read" in content
    assert "pull-requests: write" in content
    assert "contents: write" not in content
    assert "pull_request_target" not in content

    # It must not be wired up as a required/blocking gate: no failing exit,
    # no process.exit / core.setFailed calls anywhere in the script step.
    assert "core.setFailed" not in content
    assert "process.exit" not in content


def test_implements_tag_check_workflow_detects_the_protocol_tag_pattern():
    content = workflow("linear-implements-tag-check.yml")

    assert "Implements:" in content
    assert "TER-N" in content
    assert "docs/LINEAR-AGENT-PROTOCOL.md" in content


def test_implements_tag_check_workflow_uses_a_sticky_comment_marker():
    content = workflow("linear-implements-tag-check.yml")

    assert "linear-implements-tag-check" in content
    assert "listComments" in content
    assert "updateComment" in content
    assert "createComment" in content