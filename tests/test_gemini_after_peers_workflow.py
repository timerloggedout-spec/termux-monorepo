"""Regression contracts for the Gemini after-peers rate-limit boundary."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "gemini-after-peers.yml"


def test_rate_limit_exhaustion_defers_without_invoking_a_review_provider():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "const isRateLimited = error =>" in text
    assert "github_api_rate_limited" in text
    assert "No review provider was invoked" in text
    assert "if: steps.pr.outputs.skip != 'true'" in text


def test_peer_comment_lookup_is_bounded_to_latest_page():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "github.rest.issues.listComments({" in text
    assert "per_page: 100" in text
    assert "sort: 'updated'" in text
    assert "direction: 'desc'" in text
    assert "github.paginate(github.rest.issues.listComments" not in text
