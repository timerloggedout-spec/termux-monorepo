"""Pins for the #5219 RE-FIX (creation-layer rate-limit re-fix).

Run: python3 -m pytest tests/test_rate_limit_refix.py
Legs: (i) trigger trims on the top churners + cascade fan-in cut,
(ii) mint-effectiveness root cause is recorded in the audit doc
(docs/ops/rate-limit-refix-audit.md) -- 51/51 hits are the Swarm
installation bucket, not the shared token, (iii) concurrency/cancel
extended to the idempotent collectors only -- never to the provider
collect (recorded failure mode #1125).
"""

from pathlib import Path

import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "ops"))
import verify_rate_limit_window as vr

WF = Path(__file__).parent.parent / ".github" / "workflows"


def _load(name):
    return yaml.safe_load((WF / name).read_text())


def _on(name):
    d = _load(name)
    return d.get(True) or d.get("on") or {}


def test_orchestrator_duplicate_pr_trigger_removed():
    on = _on("peer-review-orchestrator.yml")
    assert "pull_request" not in on
    assert on["pull_request_target"]["types"] == [
        "opened", "synchronize", "ready_for_review", "reopened",
    ]
    # The provider collect must NOT gain cancel-in-progress (runs
    # 37247048701/37247242679 on #1125: cancelled collects recorded
    # as failures). Its concurrency group is untouched by the re-fix.
    assert _load("peer-review-orchestrator.yml")["concurrency"]["cancel-in-progress"] is False


def test_quota_tree_trigger_trims_and_coalescing():
    on = _on("quota-dispatch-tree.yml")
    assert on["pull_request_target"]["types"] == [
        "opened", "synchronize", "reopened", "closed",
    ]
    assert "push" not in on
    assert "issue_comment" in on  # /quota force all has no other intake
    conc = _load("quota-dispatch-tree.yml")["concurrency"]
    assert conc["group"] == "quota-dispatch-tree"
    assert conc["cancel-in-progress"] is True


def test_repo_tracking_pr_types_trimmed():
    on = _on("repo-tracking-collect.yml")
    assert on["pull_request_target"]["types"] == [
        "opened", "synchronize", "reopened", "closed",
    ]
    assert on["workflow_run"]["workflows"] == ["lane events recorder"]


def test_recorder_fan_in_cut():
    on = _on("lane-events-recorder.yml")
    assert "tribute-status-refresh" not in on["workflow_run"]["workflows"]
    assert "tribute execute" in on["workflow_run"]["workflows"]
    # Append-only Neon writer: no cancel (a cancelled mid-write run
    # could drop a batch with no re-scan guarantee).
    assert _load("lane-events-recorder.yml")["concurrency"]["cancel-in-progress"] is False


def test_context_audit_created_only():
    on = _on("context-relationship-audit.yml")
    assert on["issue_comment"]["types"] == ["created"]
    assert on["pull_request_review_comment"]["types"] == ["created"]
    assert on["issues"]["types"] == ["opened", "closed", "reopened"]
    assert on["pull_request_review"]["types"] == ["submitted", "dismissed"]


# --- verification script ---

def test_slice_windows_cover_the_hour():
    start = vr._parse_ts("2026-11-12T13:09:35Z")
    wins = vr.slice_windows(start, 1)
    assert len(wins) == 6
    assert wins[0][0] == start
    assert wins[-1][1] == start + vr.timedelta(hours=1)


def test_verdict_pass_and_fail():
    def window(total, hits, complete=True):
        return {
            "slices": [{"server_total_count": total, "capped": False}],
            "annotations": {
                "installation_limit_hits": [{}] * hits,
                "coverage_complete": complete,
            },
        }
    ok = vr.verdict(window(150, 0))
    assert ok["criterion_2_pass"] is True and ok["criterion_4_pass"] is True
    bad = vr.verdict(window(4799, 51))
    assert bad["criterion_2_pass"] is False and bad["criterion_4_pass"] is False
    partial = vr.verdict(window(150, 0, complete=False))
    assert partial["criterion_4_pass"] is False  # capped sweep never passes
    capped = vr.verdict({
        "slices": [{"server_total_count": 1000, "capped": True}],
        "annotations": {"installation_limit_hits": [], "coverage_complete": True},
    })
    assert capped["criterion_2_pass"] is False  # cap hit fails loud


class _FakeGh:
    def __init__(self, jobs_by_run, anns_by_url):
        self.jobs_by_run = jobs_by_run
        self.anns_by_url = anns_by_url

    def call(self, method, path):
        if "/jobs" in path:
            jobs = self.jobs_by_run.get(path.split("/runs/")[1].split("/")[0], [])
            return {"total_count": len(jobs), "jobs": jobs}
        return self.anns_by_url.get(path.split("?")[0], [])


def test_sweep_counts_only_installation_limit():
    gh = _FakeGh(
        jobs_by_run={"1": [{"id": 10, "name": "collect-peer-responses",
                            "check_run_url": "https://api.github.com/repos/x/check-runs/10"}]},
        anns_by_url={"/repos/x/check-runs/10/annotations": [
            {"message": "Unhandled error: HttpError: API rate limit exceeded for installation. req 1"},
            {"message": "some other failure"},
        ]},
    )
    out = vr.sweep_annotations(gh, [{"id": 1, "conclusion": "failure"}], max_runs=10)
    assert len(out["installation_limit_hits"]) == 1
    assert out["installation_limit_hits"][0]["run_id"] == 1
    assert out["coverage_complete"] is True


def test_paged_list_reads_server_total():
    calls = {"n": 0}

    class _OnePageGh:
        def call(self, method, path):
            calls["n"] += 1
            if calls["n"] > 1:
                return {"total_count": 250, "workflow_runs": [{"id": 2}] * 50}
            return {"total_count": 250, "workflow_runs": [{"id": 1}] * 100}

    total, items = vr.paged_list(_OnePageGh(), "/repos/x/actions/runs", "workflow_runs")
    assert total == 250
    assert len(items) == 150
