from pathlib import Path


WORKFLOW = Path(".github/workflows/agent-review-auto-jules.yml")
THROUGHPUT = Path(".github/workflows/agent-throughput-evidence.yml")


def test_review_feedback_uses_a_local_doe_receipt_contract():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "LEGACY_REVIEW_FEEDBACK_RECORDED" in source
    assert "sourceRevision" in source
    assert "pr.head.sha" in source
    assert "pr.base.sha" in source
    assert "docs/ops/DOE-ROLES-EPOCH-2026-11-03.md" in source
    assert "docs/schemas/agent-roster.yaml" in source
    assert "jules.googleapis.com" not in source
    assert "JULES_API_KEY" not in source
    assert "google-labs-code/jules-action@" not in source


def test_review_receipt_admission_filters_authors_before_runner_allocation():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "contains(fromJSON('[\"coderabbitai[bot]\"" in source
    assert "github.event.review.user.login" in source
    assert "github.event.comment.user.login" in source
    assert "actor.type !== 'Bot'" in source


def test_throughput_observer_tracks_retirement_receipts_as_doe_reviewer_work():
    source = THROUGHPUT.read_text(encoding="utf-8")
    assert '"Legacy Google Jules Review Feedback — Retirement Receipt"' in source
    assert "agentId: 'doe-reviewer'" in source
    assert "provider: 'local-doe'" in source
    assert "role: 'reviewer'" in source
