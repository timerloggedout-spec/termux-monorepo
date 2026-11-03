"""Tests for the EGM template trigger (intake + leg states)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from egm_review import (ATTESTATION, evaluate, parse_issue_body,
                        receipt_comment, validate)

FORM_PATH = (Path(__file__).resolve().parents[2]
             / ".github" / "ISSUE_TEMPLATE" / "egm-review.yml")

VALID_BODY = """### Trigger class

design-decision

### Subject under review

Whether the reader surface ships RSVP-only.

### Elephant seat

optimizations-assurance

### Artifacts of record

- apps/studysprint/web/** @ 46518482875c

### Referenced sources

_No response_

### Stakes

Public submission Nov 4.

### Claim window (hours)

24
"""

T0 = datetime(2026, 11, 3, 12, 0, tzinfo=timezone.utc)


def _c(body, at):
    return {"body": body,
            "created_at": at.strftime("%Y-%m-%dT%H:%M:%SZ")}


PACKET = _c("ELEPHANT PACKET\n- artifacts: web @ 46518482875c", T0)


def _claims(seat, ids=("F1",), attest=True):
    lines = ["GOLDFISH CLAIMS", f"reviewer seat: {seat}"]
    if attest:
        lines.append(ATTESTATION)
    lines += [f"- finding — claim id: {i}" for i in ids]
    return _c("\n".join(lines), T0 + timedelta(hours=1))


def test_form_has_no_provider_field():
    text = FORM_PATH.read_text(encoding="utf-8").lower()
    assert "provider" not in text
    assert "model" not in text


def test_parse_and_validate_ok():
    fields = parse_issue_body(VALID_BODY)
    assert fields["trigger-class"] == "design-decision"
    assert fields["sources"] == ""
    assert validate(fields) == []


def test_validate_flags_missing_and_bad_trigger():
    fields = parse_issue_body(VALID_BODY.replace(
        "### Stakes\n\nPublic submission Nov 4.\n", ""))
    assert "stakes" in validate(fields)
    bad = parse_issue_body(VALID_BODY.replace(
        "design-decision", "vibes"))
    assert "trigger-class" in validate(bad)


def test_receipt_stamps_legs_and_fail_closed():
    receipt = receipt_comment(42, parse_issue_body(VALID_BODY))
    assert "EGM INSTANCE" in receipt
    assert "DOE VERIFICATION — MANDATORY" in receipt
    assert "FAIL-CLOSED" in receipt
    assert "claim window: 24h" in receipt


def test_leg_states():
    assert evaluate([], T0)["state"] == "awaiting-packet"
    # packet, no goldfish yet, inside window
    assert evaluate([PACKET], T0 + timedelta(hours=2))["state"] \
        == "goldfish-open"
    # unattested claims do NOT count a seat
    ev = evaluate([PACKET, _claims("viz", attest=False)],
                  T0 + timedelta(hours=2))
    assert ev["goldfish_seats"] == 0
    # one attested seat: still open; two: DoE leg pending
    ev = evaluate([PACKET, _claims("viz")],
                  T0 + timedelta(hours=2))
    assert ev["state"] == "goldfish-open"
    ev = evaluate([PACKET, _claims("viz"), _claims("webdesign")],
                  T0 + timedelta(hours=2))
    assert ev["state"] == "doe-pending"
    assert ev["unverdicted"] == ["F1", "F1"] or \
        set(ev["unverdicted"]) == {"F1"}
    verdict = _c("DOE VERDICT\nclaim id: F1\nverdict: VERIFIED",
                 T0 + timedelta(hours=3))
    ev = evaluate([PACKET, _claims("viz", ("F1",)),
                   _claims("webdesign", ("F2",)), verdict],
                  T0 + timedelta(hours=3))
    assert ev["state"] == "doe-pending"  # F2 unverdicted
    verdict2 = _c("DOE VERDICT\nclaim id: F2\nverdict: REFUTED",
                  T0 + timedelta(hours=3))
    ev = evaluate([PACKET, _claims("viz", ("F1",)),
                   _claims("webdesign", ("F2",)), verdict,
                   verdict2], T0 + timedelta(hours=3))
    assert ev["state"] == "complete"


def test_fail_closed_after_window():
    ev = evaluate([PACKET, _claims("viz")],
                  T0 + timedelta(hours=25))
    assert ev["state"] == "blocked-no-fresh-context"
    # but never blocked once 2 seats attested, even late verdicts
    ev = evaluate([PACKET, _claims("viz"), _claims("webdesign")],
                  T0 + timedelta(hours=72))
    assert ev["state"] == "doe-pending"
