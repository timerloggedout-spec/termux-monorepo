import importlib.util
import json
from pathlib import Path

import pytest

from archwiz.context_relationships.evidence_matrix import EvidenceMatrixError, project_evidence_matrix

ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = ROOT / "scripts/ci/context_relationship_index.py"


def load_audit_module():
    spec = importlib.util.spec_from_file_location("context_relationship_index_under_test", AUDIT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def graph_summary():
    return {
        "ref": "master-staging",
        "parser_failures": 14,
        "history_window": {
            "issues_complete": False,
            "pull_requests_complete": False,
            "next_start_page": 2,
        },
    }


def test_paginated_gh_command_is_slurped_and_non_paginated_command_is_not(monkeypatch):
    module = load_audit_module()
    commands = []
    environments = []

    def fake_check_output(command, **kwargs):
        commands.append(command)
        environments.append(kwargs["env"])
        return "[]" if "--slurp" in command else '{"ok": true}'

    monkeypatch.setattr(module.subprocess, "check_output", fake_check_output)

    assert module.run_gh("api", "repos/example/comments", paginate=True) == []
    assert module.run_gh("pr", "view", "1") == {"ok": True}
    assert commands[0][-2:] == ["--paginate", "--slurp"]
    assert "--paginate" not in commands[1]
    assert "--slurp" not in commands[1]
    assert environments[0]["NO_COLOR"] == "1"
    assert environments[0]["CLICOLOR"] == "0"
    assert environments[0]["GH_PAGER"] == "cat"
    assert "CLICOLOR_FORCE" not in environments[0]
    assert "GH_FORCE_TTY" not in environments[0]


def test_audit_normalizes_paginated_comments_and_check_runs_and_embeds_matrix(tmp_path, monkeypatch):
    module = load_audit_module()
    output = tmp_path / "audit.json"
    summary_path = tmp_path / "build-summary.json"
    summary_path.write_text(json.dumps(graph_summary()))

    def fake_run_gh(*args, paginate=False):
        assert paginate
        endpoint = args[-1]
        if endpoint.endswith("/comments"):
            return [[{
                "id": 401,
                "created_at": "2026-08-25T00:00:00Z",
                "updated_at": "2026-08-25T00:00:00Z",
                "user": {"login": "trusted-bot"},
            }], []]
        assert endpoint.endswith("/check-runs")
        return [
            {"check_runs": [{
                "id": 902,
                "name": "unit",
                "status": "completed",
                "conclusion": "success",
                "started_at": "2026-08-25T00:01:00Z",
                "completed_at": "2026-08-25T00:02:00Z",
            }]},
            {"check_runs": [{
                "id": 903,
                "name": "lint",
                "status": "completed",
                "conclusion": "success",
                "started_at": "2026-08-25T00:03:00Z",
                "completed_at": "2026-08-25T00:04:00Z",
            }]},
        ]

    monkeypatch.setattr(module, "run_gh", fake_run_gh)
    monkeypatch.setattr(module, "now", lambda: "2026-08-25T00:00:00Z")
    monkeypatch.setenv("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
    monkeypatch.setenv("GITHUB_RUN_ID", "32800046732")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "issue_comment")

    assert module.main([
        "--issue", "192",
        "--head-sha", "a" * 40,
        "--graph-summary", str(summary_path),
        "--output", str(output),
    ]) == 0

    payload = json.loads(output.read_text())
    checks = [event for event in payload["lag_events"] if event["kind"] == "check"]
    assert checks == [{
        "kind": "check", "name": "unit", "status": "completed", "conclusion": "success",
        "started_at": "2026-08-25T00:01:00Z", "completed_at": "2026-08-25T00:02:00Z", "run_id": 902,
    }, {
        "kind": "check", "name": "lint", "status": "completed", "conclusion": "success",
        "started_at": "2026-08-25T00:03:00Z", "completed_at": "2026-08-25T00:04:00Z", "run_id": 903,
    }]
    matrix = payload["evidence_matrix"]
    assert matrix["schema"] == "context-relationship-evidence-matrix/v1"
    assert matrix["scope"] == {
        "repository": "timerloggedout-spec/termux-monorepo", "roots": ["issue:192"], "fuzzy_fallback": False,
    }
    assert matrix["verified_records"]
    assert matrix["candidate_records"] == []
    assert matrix["authority_distribution"]["github_checks_api"] == 2
    assert matrix["coverage"]["graph"]["state"] == "partial"
    assert any("historical GitHub coverage is incomplete" in gap["reason"] for gap in matrix["coverage"]["gaps"])
    outcomes = sorted(
        (record["outcome"] for record in matrix["records"] if record["relationship"]["type"] == "CHECKS_CONTEXT"),
        key=lambda item: item["binding"]["check_run_id"],
    )
    assert outcomes == [{"independently_verified": True, "binding": {
        "source_sha": "a" * 40, "check_run_id": 902, "completed_at": "2026-08-25T00:02:00Z",
    }}, {"independently_verified": True, "binding": {
        "source_sha": "a" * 40, "check_run_id": 903, "completed_at": "2026-08-25T00:04:00Z",
    }}]


def test_malformed_paginated_check_payload_is_warning_not_successful_temporal_or_matrix_evidence(tmp_path, monkeypatch):
    module = load_audit_module()
    output = tmp_path / "audit.json"

    def fake_run_gh(*args, paginate=False):
        assert paginate
        return [] if args[-1].endswith("/comments") else {"check_runs": []}

    monkeypatch.setattr(module, "run_gh", fake_run_gh)
    monkeypatch.setattr(module, "now", lambda: "2026-08-25T00:00:00Z")
    monkeypatch.setenv("GITHUB_REPOSITORY", "timerloggedout-spec/termux-monorepo")
    monkeypatch.setenv("GITHUB_RUN_ID", "1")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")

    assert module.main(["--issue", "192", "--head-sha", "b" * 40, "--output", str(output)]) == 0

    payload = json.loads(output.read_text())
    warnings = [event for event in payload["lag_events"] if event["kind"] == "check_query_warning"]
    assert len(warnings) == 1
    assert warnings[0]["classification"] == "WARNING"
    assert warnings[0]["outcome"] == "UNKNOWN"
    assert warnings[0]["error_class"] == "ValueError"
    assert "error_digest" in warnings[0]
    assert "message" not in warnings[0]
    assert not payload["lead_lag_pairs"]
    assert not [record for record in payload["evidence_matrix"]["records"] if record["relationship"]["type"] == "CHECKS_CONTEXT"]
    assert any(gap["subject"] == "check_query_warning" for gap in payload["evidence_matrix"]["coverage"]["gaps"])


def test_matrix_rejects_raw_body_and_keeps_unbound_checks_quarantined():
    audit = {
        "schema": "context-relationship-index/v1",
        "observed_at": "2026-08-25T00:00:00Z",
        "repository": "timerloggedout-spec/termux-monorepo",
        "source_sha": "c" * 40,
        "event_name": "workflow_dispatch",
        "workflow_run_id": "7",
        "workflow_run_attempt": "1",
        "correlation": {"pr_number": 11, "issue_number": None},
        "lead_events": [{"kind": "github_event", "observed_at": "2026-08-25T00:00:00Z"}],
        "lag_events": [{"kind": "check", "name": "unbound", "status": "queued", "conclusion": None, "run_id": 8}],
        "lead_lag_pairs": [],
        "limitations": [],
    }
    matrix = project_evidence_matrix(audit)
    checks = [record for record in matrix["records"] if record["relationship"]["type"] == "CHECKS_CONTEXT"]
    assert checks[0]["classification"] == "candidate"
    assert checks[0]["disposition"] == "quarantined"
    assert checks[0]["risk"]["state"] == "missing_binding"
    assert matrix["scope"]["roots"] == ["pr:11"]
    assert matrix["scope"]["fuzzy_fallback"] is False

    unbound_audit = {**audit, "workflow_run_id": None, "workflow_run_attempt": None}
    unbound_matrix = project_evidence_matrix(unbound_audit)
    audit_record = next(record for record in unbound_matrix["records"] if record["relationship"]["type"] == "AUDITS_CONTEXT")
    assert audit_record["classification"] == "candidate"
    assert audit_record["disposition"] == "quarantined"
    assert audit_record["evidence"]["authority"] == "local_read_only_probe"

    audit["lead_events"][0]["body"] = "must never be indexed"
    with pytest.raises(EvidenceMatrixError, match="prohibited field"):
        project_evidence_matrix(audit)
