"""Tests for project-task intake and QUE scientific/psychology lane profiling."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from admission_receipt import classify_receipt, has_intake_receipt
from project_task import (
    incomplete_comment, parse_issue_body, profile_lanes,
    receipt_comment, validate, validate_siglary_data_record,
)

VALID_BODY = """### Entry

D1

### Task / spec

Establish scientific validation, statistics, DO Statements and performance psychology experiments.

### Scope

scripts/dispatch/**

### Done-evidence

PR merged; tests green; receipts posted.

### Target repo

timerloggedout-spec/termux-monorepo

### Instance stamps (post-hoc)

_No response_
"""
MISSING_BODY = """### Entry

D1

### Task / spec

Build the thing.

### Done-evidence

PR merged.
"""


def test_valid_body_parses_and_profiles_all_requested_lanes():
    fields = parse_issue_body(VALID_BODY)
    assert fields["entry"] == "D1"
    assert fields["task"].startswith("Establish scientific validation")
    assert fields["scope"] == "scripts/dispatch/**"
    assert validate(fields) == []
    profile = profile_lanes(fields)
    assert "scientific-quantitative" in profile["capability_lanes"]
    assert "do-statements" in profile["capability_lanes"]
    assert "performance-psychology" in profile["capability_lanes"]
    assert "do-statements-performance-psychology" in profile["capability_lanes"]
    assert all(x["state"] == "candidate_not_preregistered"
               for x in profile["experiment_lanes"])
    assert profile["provider_selection"] == "existing_dispatch_policy"
    assert profile["specialist_roles_are_assignments"] is False
    assert "doe-expert" in profile["candidate_specialist_roles"]
    assert "experiment-designer" in profile["candidate_specialist_roles"]
    assert "performance-psychologist" in profile["candidate_specialist_roles"]
    assert profile["specialist_registry_ref"] == "ops/roles/scientific-specialists.json"


def test_default_target_repo_applies():
    body = VALID_BODY.replace(
        "### Target repo\n\ntimerloggedout-spec/termux-monorepo\n", "")
    assert parse_issue_body(body)["target-repo"] == "timerloggedout-spec/termux-monorepo"


def test_missing_required_field_named():
    fields = parse_issue_body(MISSING_BODY)
    assert validate(fields) == ["scope"]
    comment = incomplete_comment(3577, ["scope"])
    assert chr(96) + "Scope" + chr(96) in comment
    assert "#3577" in comment


def test_receipt_includes_siglary_and_experiment_lanes():
    fields = parse_issue_body(VALID_BODY)
    profile = profile_lanes(fields)
    comment = receipt_comment(3577, fields, profile)
    assert "ROUTING RECEIPT" in comment
    assert "capability lanes:" in comment
    assert "do-statements-performance-psychology" in comment
    assert "candidate_not_preregistered" in comment
    assert "SIGLARY-STANDARD.md" in comment
    assert "dispatch-queued" in comment


def test_siglary_rejects_epistemic_sentinels_in_data_records():
    assert validate_siglary_data_record({"state": None}) == []
    assert validate_siglary_data_record({"state": "NOT_ESTABLISHED"}) == ["NOT_ESTABLISHED"]
    assert validate_siglary_data_record({"state": "N∅"}) == ["N∅"]


def test_empty_body_is_incomplete_not_a_crash():
    assert validate(parse_issue_body("")) == ["entry", "task", "scope", "done-evidence"]


def test_form_has_no_provider_field():
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "project-task.yml").read_text().lower()
    assert "id: provider" not in form
    assert "id: model" not in form
    assert "label: provider" not in form
    assert "label: model" not in form
    for field_id in ("entry", "task", "scope", "done-evidence",
                     "target-repo", "instance-stamps"):
        assert f"id: {field_id}" in form


ADMISSION_STAMP = "[MUSEai]@{role:{swarm-admission}} DISPATCH **ADMITTED**\\n\\ntemplate `project-task.yml` · lane swarm-dispatch"


def test_admission_receipt_accepts_matching_post_event_stamp():
    comments = [{
        "created_at": "2026-11-11T10:01:00Z",
        "body": ADMISSION_STAMP,
    }]
    assert classify_receipt(
        comments, "project-task.yml", "2026-11-11T10:00:00Z"
    ) == "admitted"


def test_admission_receipt_ignores_stale_prior_filing_stamp():
    comments = [{
        "created_at": "2026-11-11T09:59:59Z",
        "body": ADMISSION_STAMP,
    }]
    assert classify_receipt(
        comments, "project-task.yml", "2026-11-11T10:00:00Z"
    ) is None


def test_admission_receipt_defers_without_dispatch():
    comments = [{
        "created_at": "2026-11-11T10:01:00Z",
        "body": ADMISSION_STAMP.replace("ADMITTED", "DEFERRED"),
    }]
    assert classify_receipt(
        comments, "project-task.yml", "2026-11-11T10:00:00Z"
    ) == "deferred"


def test_admission_receipt_rejects_wrong_template():
    comments = [{
        "created_at": "2026-11-11T10:01:00Z",
        "body": ADMISSION_STAMP.replace("project-task.yml", "game-development-task.yml"),
    }]
    assert classify_receipt(
        comments, "project-task.yml", "2026-11-11T10:00:00Z"
    ) == "unmatched"


def test_admission_receipt_uses_latest_post_event_decision():
    comments = [
        {"created_at": "2026-11-11T10:01:00Z", "body": ADMISSION_STAMP},
        {"created_at": "2026-11-11T10:02:00Z",
         "body": ADMISSION_STAMP.replace("ADMITTED", "DEFERRED")},
    ]
    assert classify_receipt(
        comments, "project-task.yml", "2026-11-11T10:00:00Z"
    ) == "deferred"


def test_admission_receipt_supports_all_registered_project_task_routes():
    comments = [{
        "created_at": "2026-11-11T10:01:00Z",
        "body": ADMISSION_STAMP.replace("project-task.yml", "scientific-research-task.yml"),
    }]
    assert classify_receipt(
        comments,
        "project-task.yml,scientific-research-task.yml,behavioral-experiment-task.yml",
        "2026-11-11T10:00:00Z",
    ) == "admitted"


def test_specialist_forms_are_admission_triggerable_and_share_intake_contract():
    for filename, label, lane in (
        ("scientific-research-task.yml", "scientific-task", "scientific-quantitative"),
        ("behavioral-experiment-task.yml", "behavioral-experiment",
         "do-statements-performance-psychology"),
    ):
        form = (ROOT / ".github" / "ISSUE_TEMPLATE" / filename).read_text()
        assert "SWARM-DISPATCH-BEGIN" in form
        assert "schema: issue-dispatch/v1" in form
        assert f"labels: [\"{label}\"]" in form
        assert f"lane: {lane}" in form
        for heading in ("label: Entry", "label: Task / spec",
                        "label: Scope", "label: Done-evidence"):
            assert heading in form


def test_project_task_workflow_preserves_issue_event_dependencies():
    workflow = (ROOT / ".github" / "workflows" / "project-task-dispatch.yml").read_text()
    assert "issues:" in workflow
    assert "types: [opened, reopened]" in workflow
    assert "workflow_run:" not in workflow
    assert "admission_receipt.py" in workflow
    assert "startsWith(github.event.issue.title, '[task] ')" in workflow
    assert "startsWith(github.event.issue.title, '[science] ')" in workflow
    assert "startsWith(github.event.issue.title, '[experiment] ')" in workflow


def test_specialist_registry_is_machine_readable_and_non_provider_identity():
    import json
    registry = json.loads((ROOT / "ops" / "roles" / "scientific-specialists.json").read_text())
    assert registry["schema"] == "scientific-specialist-registry/v1"
    assert registry["canonical_doe_seats"] == list((
        "builder", "operator", "steward", "observer",
        "reviewer", "scout", "gambler", "participant",
    ))
    schema = json.loads((ROOT / "ops" / "roles" / "scientific-specialists.schema.json").read_text())
    required = set(schema["properties"]["roles"]["items"]["required"])
    ids = {role["id"] for role in registry["roles"]}
    assert len(ids) == len(registry["roles"])
    assert all(required.issubset(role) for role in registry["roles"])
    assert all(role["qualification_status"] == "unqualified_until_benchmarked"
               for role in registry["roles"])
    profile = profile_lanes(parse_issue_body(VALID_BODY))
    assert set(profile["candidate_specialist_roles"]).issubset(ids)
    assert all(role["provider_identity"] is False for role in registry["roles"])
    assert all(role["independent_reviewer_role"] in ids or "distinct instance_key" in role["independent_reviewer_role"] for role in registry["roles"])
    assert all(role["canonical_seat_ids_created"] is False for role in registry["roles"])


def test_intake_receipt_idempotency_is_scoped_to_exact_issue_event():
    comments = [{
        "body": "ROUTING RECEIPT\\n\\n<!-- que-intake-event:2026-11-11T10:00:00Z -->",
    }]
    assert has_intake_receipt(comments, "2026-11-11T10:00:00Z")
    assert not has_intake_receipt(comments, "2026-11-11T10:05:00Z")
