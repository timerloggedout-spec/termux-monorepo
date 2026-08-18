from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"


def workflow(name):
    return (WORKFLOWS / name).read_text()


def test_validation_workflow_is_read_only_and_never_collects_live_history():
    content = workflow("context-relationship-validate.yml")

    assert "pull_request:" in content
    assert "contents: read" in content
    assert "persist-credentials: false" in content
    assert "GITHUB_TOKEN" not in content
    assert "python -m archwiz.context_relationships.build_index" not in content
    assert "pull_request_target" not in content


def test_publisher_uses_trusted_staging_pushes_and_prevents_generated_data_loops():
    content = workflow("context-relationship-publish.yml")

    assert "branches: [master-staging]" in content
    assert "paths-ignore:" in content
    assert "workspace/llm_map/context_relationships/**" in content
    assert "github.actor != 'github-actions[bot]'" in content
    assert "contents: write" in content
    assert "pull_request_target" not in content
    assert "git push origin HEAD:master-staging" in content
    assert "Implements: CRG-05" in content


def test_reconciliation_is_bounded_and_explicitly_refreshes_history():
    content = workflow("context-relationship-reconcile.yml")

    assert "schedule:" in content
    assert "--full-refresh" in content
    assert "--max-items" in content
    assert "--max-commits" in content
    assert "contents: write" in content
    assert "pull_request_target" not in content
