import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add repository root to sys.path so the script module is importable.
repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import scripts.ci.engineering_health as eh


def test_headers():
    assert eh._headers(None) == eh.BASE_HEADERS
    assert eh._headers("mytoken")["Authorization"] == "Bearer mytoken"


def test_gate_label():
    assert eh.gate_label({"status": "completed", "conclusion": "success"}) == "green"
    assert eh.gate_label({"status": "completed", "conclusion": "failure"}) == "red"
    assert eh.gate_label({"status": "completed", "conclusion": "timed_out"}) == "red"
    assert eh.gate_label({"status": "completed", "conclusion": "cancelled"}) == "red"
    assert eh.gate_label({"status": "in_progress", "conclusion": None}) == "pending"
    assert eh.gate_label({"status": "queued", "conclusion": None}) == "pending"
    assert eh.gate_label({"status": "missing", "conclusion": None}) == "unknown"
    assert eh.gate_label({"status": "unknown_status", "conclusion": None}) == "unknown"


def test_summarize_run():
    assert eh.summarize_run(None) == {
        "status": "missing",
        "conclusion": None,
        "html_url": None,
        "head_sha": None,
    }
    run = {
        "status": "completed",
        "conclusion": "success",
        "html_url": "https://github.com/run/1",
        "head_sha": "1234567890abcdef",
        "created_at": "2026-09-13T07:00:00Z",
        "display_title": "Run Title",
    }
    res = eh.summarize_run(run)
    assert res["status"] == "completed"
    assert res["conclusion"] == "success"
    assert res["head_sha"] == "1234567890ab"


def test_collect_and_to_markdown(tmp_path, monkeypatch):
    def mock_gh_get(path, token, params=None):
        if "/actions/workflows/" in path:
            return {
                "workflow_runs": [
                    {
                        "status": "completed",
                        "conclusion": "success",
                        "html_url": "https://github.com/gate/1",
                        "head_sha": "abcdefabcdef",
                    }
                ]
            }
        if path.endswith("/pulls"):
            return [
                {
                    "number": 10,
                    "title": "Fix something | test",
                    "draft": False,
                    "mergeable_state": "clean",
                    "html_url": "https://github.com/pull/10",
                    "updated_at": "2026-09-13T07:00:00Z",
                    "user": {"login": "jules"},
                }
            ]
        if path.endswith("/runs"):
            return {
                "workflow_runs": [
                    {
                        "name": "CI Run 1",
                        "status": "completed",
                        "conclusion": "failure",
                        "event": "push",
                        "html_url": "https://github.com/run/1",
                        "head_sha": "abcdef1234567890",
                        "created_at": "2026-09-13T07:00:00Z",
                    },
                    {
                        "name": "CI Run 2",
                        "status": "completed",
                        "conclusion": "success",
                        "event": "push",
                        "html_url": "https://github.com/run/2",
                        "head_sha": "123456abcdef7890",
                        "created_at": "2026-09-13T07:05:00Z",
                    },
                ]
            }
        return {"default_branch": "master", "pushed_at": "2026-09-13T07:00:00Z"}

    monkeypatch.setattr(eh, "gh_get", mock_gh_get)

    snap = eh.collect("owner", "repo", "master", None)
    assert snap["dual_gates"]["combined"] == "green"
    assert snap["open_prs"]["count"] == 1
    assert len(snap["actions_hygiene"]["recent_runs"]) == 2
    assert len(snap["actions_hygiene"]["failed_recent"]) == 1
    assert snap["actions_hygiene"]["failed_recent"][0]["name"] == "CI Run 1"

    md = eh.to_markdown(snap)
    assert "# Engineering health — `owner/repo`" in md
    assert "[10](https://github.com/pull/10)" in md
    assert "CI Run 1" in md


def test_main(tmp_path, monkeypatch):
    out_dir = tmp_path / "eng_out"
    monkeypatch.setattr(
        sys,
        "argv",
        ["engineering_health.py", "--repo", "owner/repo", "--out-dir", str(out_dir)],
    )

    with patch.object(
        eh,
        "collect",
        return_value={
            "schema": "engineering-health/v1",
            "observed_at": "2026-09-13T07:00:00Z",
            "repository": "owner/repo",
            "default_branch": "master",
            "head_sha_hint": "pushed",
            "dual_gates": {
                "repo_gate": {"label": "green", "status": "completed", "conclusion": "success", "head_sha": "123"},
                "termux_smoke": {"label": "green", "status": "completed", "conclusion": "success", "head_sha": "123"},
                "combined": "green",
            },
            "open_prs": {"count": 0, "items": []},
            "actions_hygiene": {"recent_runs": [], "failed_recent": []},
            "cellcog_dashboard_ref": {"url": "https://cellcog.ai", "note": "test"},
            "credit_policy": "zero_cellcog_llm_credits",
        },
    ):
        ret = eh.main()
        assert ret == 0
        assert (out_dir / "snapshot.json").exists()
        assert (out_dir / "snapshot.md").exists()
