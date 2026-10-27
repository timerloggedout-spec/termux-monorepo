"""Tests for the tribute participation classifier.

Fixtures are modeled on the real batch-1 threads documented in
docs/ops/TRIBUTE-LANE-EFFICACY-AUDIT-2026-10-27.md (SendAm zombies,
cognee yield, sorolens prior wave claims, ROCm held question, Sail-CLI
convert/active pair). The classifier is pure: no network.
"""

import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "tribute_participation", ROOT / "scripts" / "ci" / "tribute_participation.py"
)
tp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tp)

STAKE = [".github/help-wanted-lane-stake.md"]


def comment(login, body, ts):
    return {"user": {"login": login}, "body": body, "created_at": ts}


def pr(state="open", merged_at=None, title="help-wanted: stake + contribute for #1"):
    return {"state": state, "merged_at": merged_at, "title": title, "body": ""}


def issue(state="open", assignees=()):
    return {"state": state, "assignees": [{"login": a} for a in assignees]}


def test_zombie_issue_closed_withdraws_nonconversion():
    d, _ = tp.decide_disposition(pr(), issue(state="closed"), [], STAKE)
    assert d == "withdraw_nonconversion"


def test_yield_when_assigned_to_someone_else():
    d, _ = tp.decide_disposition(pr(), issue(assignees=["cicada0007"]), [], STAKE)
    assert d == "withdraw_yield"


def test_yield_when_human_claim_predates_ours():
    comments = [
        comment("wave-dev", "@wave-dev has applied to work on this issue as part of the **Stellar Wave Program**", "2026-10-18T00:00:00Z"),
        comment(tp.US, tp.CLAIM_MARKER, "2026-10-19T00:00:00Z"),
    ]
    d, _ = tp.decide_disposition(pr(), issue(), comments, STAKE)
    assert d == "withdraw_yield"


def test_held_when_maintainer_question_is_open():
    # ROCm shape: maintainer asks what the PR is for; nobody answered.
    # Held wins over every other class — automation posts nothing.
    comments = [
        comment(tp.US, "### Help-wanted follow-up — stale_nudge", "2026-10-21T00:00:00Z"),
        comment("dysu-amd", "Hi @timerloggedout-spec, what is the purpose of this PR?", "2026-10-22T00:00:00Z"),
    ]
    d, _ = tp.decide_disposition(pr(), issue(assignees=["NikharAsthana"]), comments, STAKE)
    assert d == "held_surface"


def test_not_held_after_we_reply():
    comments = [
        comment("maintainer", "What is the purpose of this PR?", "2026-10-22T00:00:00Z"),
        comment(tp.US, "It was a claim marker; converting it now.", "2026-10-23T00:00:00Z"),
    ]
    d, _ = tp.decide_disposition(pr(), issue(state="closed"), comments, STAKE)
    assert d == "withdraw_nonconversion"


def test_convert_candidate_for_stake_on_open_unclaimed_issue():
    d, _ = tp.decide_disposition(pr(), issue(assignees=[tp.US]), [], STAKE)
    assert d == "convert_candidate"


def test_active_ok_for_substantive_diff():
    d, _ = tp.decide_disposition(pr(), issue(assignees=[tp.US]), [], ["internal/domain/types_test.go"])
    assert d == "active_ok"


def test_accepted_record_for_merged():
    d, _ = tp.decide_disposition(pr(state="closed", merged_at="2026-10-01T00:00:00Z"), None, [], STAKE)
    assert d == "accepted_record"


def test_nonconversion_when_maintainer_flagged_noise():
    comments = [comment("maintainer", "This is a placeholder, not a real contribution.", "2026-10-02T00:00:00Z")]
    d, _ = tp.decide_disposition(pr(state="closed"), issue(), comments, STAKE)
    assert d == "nonconversion_record"


def test_reopen_candidate_when_issue_open_and_unclaimed():
    d, _ = tp.decide_disposition(pr(state="closed"), issue(), [], STAKE)
    assert d == "reopen_candidate"


def test_plan_actions_caps_and_only_withdraws():
    items = (
        [{"disposition": "withdraw_yield", "pr_url": f"u{i}"} for i in range(5)]
        + [{"disposition": "convert_candidate", "pr_url": "c0"},
           {"disposition": "held_surface", "pr_url": "h0"}]
    )
    planned, deferred = tp.plan_actions(items, 3)
    assert [p["pr_url"] for p in planned] == ["u0", "u1", "u2"]
    assert deferred == 2


def test_parse_issue_ref_from_title_and_body():
    assert tp.parse_issue_ref({"title": "help-wanted: stake + contribute for #465", "body": ""}) == 465
    assert tp.parse_issue_ref({"title": "fix", "body": "see https://github.com/a/b/issues/77"}) == 77
    assert tp.parse_issue_ref({"title": "fix", "body": ""}) is None
