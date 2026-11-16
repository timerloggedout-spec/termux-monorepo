"""QUE #5286 — auto-claim decision logic (pure)."""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import auto_claim as ac  # noqa: E402

NOW = datetime(2026, 11, 13, 12, 0, 0, tzinfo=timezone.utc)
TS = "%Y-%m-%dT%H:%M:%SZ"


def issue(number=1, body="", labels=()):
    return {"number": number, "title": "t", "body": body,
            "labels": [{"name": n} for n in labels],
            "user": {"login": "seat"}}


def comment(body, minutes_ago=0):
    return {"body": body,
            "created_at": (NOW - timedelta(minutes=minutes_ago)).strftime(TS)}


def cand(number=1, body="", labels=(), comments=(), state="escalated",
         action=None, wall=None, score=100, claim=None):
    return {"issue": issue(number, body, labels),
            "comments": list(comments),
            "verdict": {"issue": number, "state": state, "action": action,
                        "age_min": 100.0},
            "score_row": {"score": score}, "wall_in_min": wall,
            "claim": claim}


SWARM_BUILD = ('<!-- SWARM-DISPATCH {"schema": "issue-dispatch/v1", '
               '"route": "build-dispatch", "entry": "x", "tier": 3} -->')
SWARM_TASK = ('<!-- SWARM-DISPATCH {"schema": "issue-dispatch/v1", '
              '"route": "project-task-dispatch", "entry": "x", "tier": 3} -->')


def test_claim_classes_from_stamps():
    assert ac.claim_class_of(issue(body=SWARM_BUILD), []) == \
        ("executor", "dispatch-executor")
    assert ac.claim_class_of(issue(body=SWARM_TASK), []) == \
        ("seat-queue", "qdesk-seat-queue")
    named = issue(body="Task.\n\nexecutor of record: quota-specialist (chat x)")
    assert ac.claim_class_of(named, []) == \
        ("named-executor", "quota-specialist (chat x)")
    override = issue(body=SWARM_BUILD + "\nclaim-class: seat-queue")
    assert ac.claim_class_of(override, [])[0] == "seat-queue"
    assert ac.claim_class_of(issue(body="no stamps at all"), []) == (None, None)


def test_gated_never_claimed():
    gated = cand(body=SWARM_BUILD, labels=("value-class",))
    plan = ac.plan([gated], NOW)
    assert not plan["claims"]
    assert plan["exceptions"][0]["kind"] == "gated"
    marker = cand(body=SWARM_BUILD + "\nrequires participation_set countersign")
    plan2 = ac.plan([marker], NOW)
    assert plan2["exceptions"][0]["kind"] == "gated"


def test_plan_claims_in_rank_order_and_unplaceable_exception():
    low = cand(number=2, body=SWARM_TASK, score=50)
    high = cand(number=3, body=SWARM_BUILD, score=900)
    bare = cand(number=4, body="unstamped filing")
    plan = ac.plan([low, high, bare], NOW)
    assert [c["issue"] for c in plan["claims"]] == [3, 2]
    assert [c["rank"] for c in plan["claims"]] == [1, 2]
    assert plan["exceptions"][0]["issue"] == 4
    assert plan["exceptions"][0]["kind"] == "unplaceable"


def test_wall_admission_claims_before_escalation():
    near = cand(number=5, body=SWARM_BUILD, state="watching", wall=600)
    far = cand(number=6, body=SWARM_BUILD, state="watching", wall=6000)
    plan = ac.plan([near, far], NOW)
    assert [c["issue"] for c in plan["claims"]] == [5]
    assert plan["claims"][0]["trigger"] == "wall-admission"


def test_rejected_twice_becomes_exception():
    fails = [comment("auto-claim-failed: boom"), comment("auto-claim-failed: boom")]
    plan = ac.plan([cand(body=SWARM_BUILD, comments=fails)], NOW)
    assert not plan["claims"]
    assert plan["exceptions"][0]["kind"] == "rejected"


def test_auto_claim_comment_parses_as_claim_with_lease():
    body = ac.auto_claim_comment(claim_class="executor",
                                 claimant="dispatch-executor", rank=1,
                                 score=1234, now=NOW, trigger="escalation")
    assert "PRODUCER CLAIM" in body and "claimed at:" in body
    lease = ac.lease_of([comment(body)])
    assert lease[0] == "executor" and lease[1] == "dispatch-executor"
    assert lease[2] == NOW + timedelta(minutes=120)
    assert "stall-resolved:" in body


def test_lease_release_only_when_expired_and_idle():
    claimed_at = NOW - timedelta(minutes=300)
    claim_body = ac.auto_claim_comment(
        claim_class="executor", claimant="dispatch-executor", rank=1,
        score=10, now=claimed_at, trigger="escalation")
    comments = [{"body": claim_body, "created_at": claimed_at.strftime(TS)}]
    c = cand(state="claimed", comments=comments,
             claim={"at_dt": claimed_at})
    plan = ac.plan([c], NOW)
    assert len(plan["releases"]) == 1  # lease 120m expired, no activity
    active = comments + [comment("PR opened", minutes_ago=30)]
    c2 = cand(state="claimed", comments=active, claim={"at_dt": claimed_at})
    assert not ac.plan([c2], NOW)["releases"]  # execution activity holds it
    fresh_at = NOW - timedelta(minutes=30)
    fresh_body = ac.auto_claim_comment(
        claim_class="executor", claimant="dispatch-executor", rank=1,
        score=10, now=fresh_at, trigger="escalation")
    fresh = cand(state="claimed",
                 comments=[{"body": fresh_body,
                            "created_at": fresh_at.strftime(TS)}],
                 claim={"at_dt": fresh_at})
    assert not ac.plan([fresh], NOW)["releases"]  # lease not yet expired
    manual = cand(state="claimed",
                  comments=[comment("PRODUCER CLAIM — pickup", minutes_ago=300)],
                  claim={"at_dt": claimed_at})
    assert not ac.plan([manual], NOW)["releases"]  # manual claims: no lease


def test_gap_records_and_feed_counts():
    plan = ac.plan([cand(number=7, body=SWARM_BUILD),
                    cand(number=8, body="unstamped")], NOW)
    records = ac.gap_records(plan, NOW)
    feed = ac.gap_feed(records, NOW)
    assert feed["gap_class"] == "escalation-stall"
    assert feed["counts_this_cycle"]["auto_claimed"] == 1
    assert feed["counts_this_cycle"]["placement_failed"] == 1
