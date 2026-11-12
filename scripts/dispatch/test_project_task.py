"""Tests for project-task intake and QUE scientific/psychology lane profiling."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
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
