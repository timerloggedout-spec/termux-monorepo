"""Tests for scripts/registration_monikers/registry.py (4n0n protocol).

Covers the deterministic moniker rule, activation semantics (log
sections 1/4 activate a platform; section 3 candidates never do),
packet attribution, the never-invent-a-handle discipline, drift
detection, and the shipped registry's consistency with the shipped
challenge log + protocol doc.
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "registration_monikers_registry",
    ROOT / "scripts" / "registration_monikers" / "registry.py")
reg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reg)

FIXTURE_LOG = """# Challenge Entries Log

Builder identity used throughout: AWS Builder Center profile.

## 1. Verified registrations (platform joins)

| # | Event | Evidence |
|---|-------|----------|
| R1 | Agent Experience Hackathon: Strands Decider (AWS Builder Center) | Gmail msg `x` |

## 2. Submission status - none verified

## 3. Candidate opportunities

| # | Opportunity |
|---|-------------|
| C5 | PayPal AI Hackathon 2026 - Devpost |
| C7 | Lexsi AI Safety - Hugging Face |

## 4. Entry packets

### D4 - for C4, Kiroween 2026 - REGISTERING

Registration requires a Devpost account and a valid Kiro user ID.

### D9 - for C9, Mystery Conf - PLANNED

A packet naming no platform in the detection vocabulary.

## 5. Sweep sources

AWS Builder Center hackathons listing; Devpost; lablab.ai events.
"""


def empty_registry():
    return {"schema": reg.SCHEMA, "entries": []}


def test_derive_moniker_basic():
    assert reg.derive_moniker("aws-builder-center", {}) == "entrantAwsBuilderCenter"
    assert reg.derive_moniker("devpost", {}) == "entrantDevpost"
    assert reg.derive_moniker("lablab-ai", {}) == "entrantLablabAi"


def test_derive_moniker_collision_appends_smallest_free_integer():
    taken = {"entrantdevpost": "devpost"}
    assert reg.derive_moniker("devpost", taken) == "entrantDevpost"  # same owner
    taken = {"entrantdevpost": "other-platform"}
    assert reg.derive_moniker("devpost", taken) == "entrantDevpost2"


def test_canonical_form():
    e = {"role": "entrant", "moniker": "entrantKiro", "platform_id": "kiro"}
    assert reg.canonical(e) == "entrant{entrantKiro}[platform:kiro]"


def test_activation_ignores_candidate_section():
    active = reg.activated_platforms(FIXTURE_LOG)
    assert "aws-builder-center" in active          # section 1
    assert "devpost" in active and "kiro" in active  # section 4 (D4)
    assert "paypal" not in active                  # section 3 only
    assert "lexsi" not in active and "hugging-face" not in active


def test_assign_adds_activated_platforms_with_null_handles():
    registry = empty_registry()
    added = reg.assign(registry, FIXTURE_LOG)
    assert added == ["aws-builder-center", "devpost", "kiro"]
    by_id = {e["platform_id"]: e for e in registry["entries"]}
    assert by_id["devpost"]["moniker"] == "entrantDevpost"
    for e in registry["entries"]:
        assert e["public_handle"] is None
        assert e["handle_state"] == "unknown-verify"
    # D4 is attributed to both platforms its text names.
    assert [r["ref"] for r in by_id["devpost"]["registrations"]] == ["D4"]
    assert [r["ref"] for r in by_id["kiro"]["registrations"]] == ["D4"]


def test_assign_is_idempotent():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    assert reg.assign(registry, FIXTURE_LOG) == []


def test_check_flags_unclaimed_packet_only():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    problems = reg.check(registry, FIXTURE_LOG)
    # D9 names no known platform: a curation item, reported not invented.
    assert problems == ["unclaimed-packet:D9"]


def test_check_rejects_invented_handle():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    registry["entries"][0]["public_handle"] = "@guessed"
    problems = reg.check(registry, FIXTURE_LOG)
    assert any("handle present but state" in p for p in problems)


def test_check_rejects_moniker_rule_drift():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    for e in registry["entries"]:
        if e["platform_id"] == "kiro":
            e["moniker"] = "entrantKiroPrime"
    problems = reg.check(registry, FIXTURE_LOG)
    assert any("rule-derived" in p for p in problems)


def test_render_table_carries_canonical_forms():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    table = reg.render_table(registry)
    assert "`entrant{entrantDevpost}[platform:devpost]`" in table
    assert "unknown-verify" in table  # null handles render their state


def test_shipped_registry_is_consistent_with_shipped_log():
    registry = json.loads((ROOT / "config" / "registration_monikers.json").read_text())
    log_text = (ROOT / "docs" / "ops" / "CHALLENGE-ENTRIES-LOG.md").read_text()
    assert reg.check(registry, log_text) == []


def test_shipped_doc_table_is_in_sync():
    registry = json.loads((ROOT / "config" / "registration_monikers.json").read_text())
    doc = (ROOT / "docs" / "ops" / "4N0N-REGISTRATION-PROTOCOL.md").read_text()
    assert reg.render_doc(doc, registry) == doc
