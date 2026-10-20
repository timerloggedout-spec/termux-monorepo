import base64
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts.model_selection_market.publish_recon import GATES, SNAPSHOT_PATH, GitHub, publish, validate_snapshot

SHA = "a" * 40


def snapshot():
    return (json.dumps({"schema_version": "msm-provider-recon-v1", "sources": [
            {"repo": repo, "commit_sha": SHA, "files": {"data": {
                "url": f"https://raw.githubusercontent.com/{repo}/{SHA}/data", "sha256": "b" * 64}}}
            for repo in ("mnfst/awesome-free-llm-apis", "tashfeenahmed/freellmapi")],
        "model_candidates": [{"provider_key": "test", "model_key": "m", "source_repo": "mnfst/awesome-free-llm-apis",
                        "evidence_class": "THIRD_PARTY_CLAIM", "runtime_eligible": False,
                        "quota_remaining": None}]}, indent=2, sort_keys=True) + "\n").encode()


def fake_api(*, current=None, existing=False, recover=False):
    api = Mock()
    def call(method, path, payload=None):
        if path == "git/ref/heads/master": return {"object": {"sha": SHA}}
        if path == "git/commits/" + SHA: return {"tree": {"sha": "b" * 40}}
        if path.startswith("git/trees/") and method == "GET":
            return {"tree": [] if current is None else [{"path": SNAPSHOT_PATH, "sha": "old"}]}
        if path == "git/blobs/old": return {"content": base64.b64encode(current).decode()}
        if path.startswith("pulls?"): return [{"state": "open", "html_url": "https://github.com/test/pr/1"}] if existing else []
        if path.startswith("git/matching-refs/"):
            branch = path.split("heads/", 1)[1]
            return [{"ref": "refs/heads/" + branch}] if recover else []
        if path.startswith("contents/"): return {"content": base64.b64encode(snapshot()).decode()}
        if method == "POST" and path == "pulls": return {"html_url": "https://github.com/test/pr/2"}
        return {"sha": "c" * 40}
    api.call.side_effect = call
    return api


def test_first_publish_is_path_restricted_and_dispatches_named_gates():
    api = fake_api()
    result = publish(api, snapshot())
    assert result["status"] == "created"
    tree = next(c.args[2] for c in api.call.call_args_list if c.args[:2] == ("POST", "git/trees"))
    assert [r["path"] for r in tree["tree"]] == [SNAPSHOT_PATH]
    assert tree["base_tree"] == "b" * 40
    refs = [c for c in api.call.call_args_list if c.args[:2] == ("POST", "git/refs")]
    assert len(refs) == 1
    dispatches = [c for c in api.call.call_args_list if "/dispatches" in c.args[1]]
    assert len(dispatches) == len(GATES)
    assert all(c.args[2]["ref"].startswith("q/provider-recon-") for c in dispatches)
    assert not any(c.args[0] in {"PATCH", "PUT", "DELETE"} for c in api.call.call_args_list)


def test_no_change_never_mutates_or_dispatches():
    api = fake_api(current=snapshot())
    assert publish(api, snapshot())["status"] == "unchanged"
    assert all(c.args[0] == "GET" for c in api.call.call_args_list)


def test_existing_pr_retry_dispatches_gates_without_duplicate_pr():
    api = fake_api(existing=True)
    assert publish(api, snapshot())["status"] == "existing"
    assert not any(c.args[:2] == ("POST", "pulls") for c in api.call.call_args_list)
    assert sum("/dispatches" in c.args[1] for c in api.call.call_args_list) == 2


def test_interrupted_ref_creation_recovers_identical_snapshot_only():
    api = fake_api(recover=True)
    assert publish(api, snapshot())["status"] == "created"
    assert not any(c.args[:2] == ("POST", "git/refs") for c in api.call.call_args_list)


@pytest.mark.parametrize("field,value", [("runtime_eligible", True), ("runtime_eligible", 0), ("quota_remaining", 500)])
def test_claims_cannot_become_runtime_authority(field, value):
    data = json.loads(snapshot()); data["model_candidates"][0][field] = value
    with pytest.raises(ValueError): validate_snapshot(json.dumps(data).encode())


def test_invalid_schema_or_missing_sources_fail_before_network():
    api = fake_api()
    with pytest.raises(ValueError): publish(api, b'{}')
    api.call.assert_not_called()
    data = json.loads(snapshot()); data["sources"] = []
    with pytest.raises(ValueError): validate_snapshot(json.dumps(data).encode())
    with pytest.raises(ValueError): GitHub("not-a-real-token", "other/repository")


def test_workflow_separates_untrusted_pr_contracts_from_publication():
    text = (Path(__file__).resolve().parents[1] / ".github/workflows/provider-recon-compound.yml").read_text()
    assert "permissions: {}" in text
    assert "pull_request_target" not in text
    assert "head_repository.full_name == github.repository" in text
    assert "ref: ${{ github.event.repository.default_branch }}" in text
    assert "needs: collect" in text
    assert "cron:" not in text
    assert "provider-research-${{ github.run_id }}-${{ github.run_attempt }}" in text


def test_real_discovery_shape_is_accepted_offline():
    from scripts.model_selection_market.provider_recon import build_snapshot
    from tests.test_provider_recon import ProviderReconTests
    _, blobs = ProviderReconTests().fixtures()
    result = build_snapshot(lambda url: blobs[url])
    assert validate_snapshot(json.dumps(result).encode()) == result


@pytest.mark.parametrize("kind", ["source", "sha", "hash", "claim", "duplicate"])
def test_bad_provenance_is_rejected(kind):
    data = json.loads(snapshot())
    if kind == "source": data["sources"][0]["repo"] = "untrusted/repo"
    if kind == "sha": data["sources"][0]["commit_sha"] = "short"
    if kind == "hash": data["sources"][0]["files"]["data"]["sha256"] = "bad"
    if kind == "claim": data["model_candidates"][0]["evidence_class"] = "VERIFIED"
    if kind == "duplicate": data["model_candidates"].append(data["model_candidates"][0])
    with pytest.raises(ValueError): validate_snapshot(json.dumps(data).encode())
