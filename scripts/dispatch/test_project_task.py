"""Tests for the project-task intake parser (issue #3577).

A valid form body parses to receipt fields; a body missing a required
field takes the intake-incomplete path and names the field. The form
file itself is verified to carry no provider/model field (hard rule).
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from project_task import (incomplete_comment, parse_issue_body,  # noqa: E402
                          receipt_comment, validate)

VALID_BODY = """### Entry

D1

### Task / spec

Build the thing, exactly this scope.

### Scope

apps/studysprint/**

### Done-evidence

PR merged; tests green; receipt posted.

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


def test_valid_body_parses_all_fields():
    fields = parse_issue_body(VALID_BODY)
    assert fields["entry"] == "D1"
    assert fields["task"] == "Build the thing, exactly this scope."
    assert fields["scope"] == "apps/studysprint/**"
    assert fields["done-evidence"] == "PR merged; tests green; receipt posted."
    assert fields["target-repo"] == "timerloggedout-spec/termux-monorepo"
    assert fields["instance-stamps"] == ""  # _No response_ -> empty
    assert validate(fields) == []


def test_default_target_repo_applies():
    body = VALID_BODY.replace(
        "### Target repo\n\ntimerloggedout-spec/termux-monorepo\n", "")
    fields = parse_issue_body(body)
    assert fields["target-repo"] == "timerloggedout-spec/termux-monorepo"


def test_missing_required_field_named():
    fields = parse_issue_body(MISSING_BODY)
    assert validate(fields) == ["scope"]
    comment = incomplete_comment(3577, ["scope"])
    assert "intake-incomplete" in comment
    assert "`Scope`" in comment
    assert "#3577" in comment


def test_receipt_comment_shape():
    fields = parse_issue_body(VALID_BODY)
    comment = receipt_comment(3577, fields)
    assert "ROUTING RECEIPT" in comment
    assert "intake id: issue #3577" in comment
    assert "entry: D1" in comment
    assert "dispatch-queued" in comment
    assert "stamps: pending" in comment


def test_empty_body_is_incomplete_not_a_crash():
    fields = parse_issue_body("")
    assert validate(fields) == ["entry", "task", "scope", "done-evidence"]


def test_form_has_no_provider_field():
    # HARD RULE (issue #3577): no provider/model FIELD at intake. The
    # form prose may *mention* providers (it explains that the system
    # selects); what is barred is a field asking the filer to name one.
    form = (ROOT / ".github" / "ISSUE_TEMPLATE" / "project-task.yml")
    text = form.read_text().lower()
    assert "id: provider" not in text
    assert "id: model" not in text
    assert "label: provider" not in text
    assert "label: model" not in text
    for field_id in ("entry", "task", "scope", "done-evidence",
                     "target-repo", "instance-stamps"):
        assert f"id: {field_id}" in text
