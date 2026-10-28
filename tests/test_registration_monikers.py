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

FIXTURE_PROFILES = """# Profile Registry - Fleet Public Identities

## 2. Profiles

### Challenge entries lane

#### AWS Builder Center - @fixturehandle

- Status: exists.

#### Devpost - not created

#### Kiro - not created
"""


def empty_registry():
    return {"schema": reg.SCHEMA, "entries": []}


def test_derive_moniker_basic():
    assert reg.derive_moniker("aws-builder-center", {}) == "n0nAwsBuilder"
    assert reg.derive_moniker("devpost", {}) == "n0nDevpost"
    assert reg.derive_moniker("uno-router", {}) == "n0nUnoRouter"
    assert reg.derive_moniker("llm7", {}) == "n0nLlm7"


def test_derive_moniker_drops_filler_words_but_never_the_first():
    assert reg.derive_moniker("lablab-ai", {}) == "n0nLablab"
    assert reg.derive_moniker("builder-io", {}) == "n0nBuilder"
    assert reg.derive_moniker("ai", {}) == "n0nAi"
    assert reg.derive_moniker("io", {}) == "n0nIo"


def test_derive_moniker_collision_appends_smallest_free_integer():
    taken = {"n0ndevpost": "devpost"}
    assert reg.derive_moniker("devpost", taken) == "n0nDevpost"  # same owner
    taken = {"n0ndevpost": "other-platform"}
    assert reg.derive_moniker("devpost", taken) == "n0nDevpost2"


def test_canonical_form():
    e = {"role": "entrant", "moniker": "n0nKiro", "platform_id": "kiro"}
    assert reg.canonical(e) == "entrant{n0nKiro}[platform:kiro]"
    e = {"role": "account", "moniker": "n0nCohere", "platform_id": "cohere"}
    assert reg.canonical(e) == "account{n0nCohere}[platform:cohere]"


def test_activation_ignores_candidate_section():
    active = reg.activated_platforms(FIXTURE_LOG)
    assert "aws-builder-center" in active          # section 1
    assert "devpost" in active and "kiro" in active  # section 4 (D4)
    assert "paypal" not in active                  # section 3 only
    assert "lexsi" not in active and "hugging-face" not in active


def test_assign_adds_activated_platforms_with_profile_refs_only():
    registry = empty_registry()
    added = reg.assign(registry, FIXTURE_LOG)
    assert added == ["aws-builder-center", "devpost", "kiro"]
    by_id = {e["platform_id"]: e for e in registry["entries"]}
    assert by_id["devpost"]["moniker"] == "n0nDevpost"
    for e in registry["entries"]:
        # No profile data is carried here - only a pointer (one home per fact).
        assert "public_handle" not in e and "handle_state" not in e
        assert e["profile_ref"] == e["platform"]
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
    problems = reg.check(registry, FIXTURE_LOG, FIXTURE_PROFILES)
    # D9 names no known platform: a curation item, reported not invented.
    assert problems == ["unclaimed-packet:D9"]


def test_check_rejects_duplicated_profile_data():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    registry["entries"][0]["public_handle"] = "@guessed"
    problems = reg.check(registry, FIXTURE_LOG, FIXTURE_PROFILES)
    assert any("profile data" in p for p in problems)


def test_check_rejects_unresolvable_profile_ref():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    for e in registry["entries"]:
        if e["platform_id"] == "kiro":
            e["profile_ref"] = "Kiro Prime"
    problems = reg.check(registry, FIXTURE_LOG, FIXTURE_PROFILES)
    assert any("does not resolve" in p for p in problems)


def test_check_rejects_moniker_rule_drift():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    for e in registry["entries"]:
        if e["platform_id"] == "kiro":
            e["moniker"] = "n0nKiroPrime"
    problems = reg.check(registry, FIXTURE_LOG, FIXTURE_PROFILES)
    assert any("rule-derived" in p for p in problems)


def test_render_table_carries_canonical_forms():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    table = reg.render_table(registry)
    assert "`entrant{n0nDevpost}[platform:devpost]`" in table
    assert "| Devpost |" in table  # profile_ref column names the heading


def fleet_entry(**overrides):
    e = {"platform_id": "cohere", "platform": "Cohere", "kind": "provider",
         "role": "account", "moniker": "n0nCohere", "profile_ref": None,
         "profile_pending": "account-creation", "status": "pending",
         "registrations": [],
         "handling": json.loads(json.dumps(reg.DEFAULT_HANDLING))}
    e.update(overrides)
    return e


def test_fleet_entry_null_profile_ref_with_pending_lane_is_valid():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    registry["entries"].append(fleet_entry())
    problems = reg.check(registry, FIXTURE_LOG, FIXTURE_PROFILES)
    # Only the known unclaimed-packet item remains; the fleet entry is
    # neither stale-checked against the log nor required to resolve a ref.
    assert problems == ["unclaimed-packet:D9"]


def test_fleet_entry_null_profile_ref_without_pending_lane_fails():
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    registry["entries"].append(fleet_entry(profile_pending=""))
    problems = reg.check(registry, FIXTURE_LOG, FIXTURE_PROFILES)
    assert any("profile_pending" in p for p in problems)


def test_derive_mode_registered_and_unregistered(capsys, tmp_path):
    registry = empty_registry()
    reg.assign(registry, FIXTURE_LOG)
    rp = tmp_path / "r.json"
    rp.write_text(json.dumps(registry))
    assert reg.main(["derive", "--registry", str(rp),
                     "--platform-id", "devpost"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["moniker"] == "n0nDevpost" and out["source"] == "registry"
    assert reg.main(["derive", "--registry", str(rp),
                     "--platform-id", "cohere"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["canonical"] == "account{n0nCohere}[platform:cohere]"


def test_shipped_registry_is_consistent_with_shipped_log():
    registry = json.loads((ROOT / "config" / "registration_monikers.json").read_text())
    log_text = (ROOT / "docs" / "ops" / "CHALLENGE-ENTRIES-LOG.md").read_text()
    profiles_text = (ROOT / "docs" / "ops" / "PROFILE-REGISTRY.md").read_text()
    assert reg.check(registry, log_text, profiles_text) == []


def test_shipped_doc_table_is_in_sync():
    registry = json.loads((ROOT / "config" / "registration_monikers.json").read_text())
    doc = (ROOT / "docs" / "ops" / "4N0N-REGISTRATION-PROTOCOL.md").read_text()
    assert reg.render_doc(doc, registry) == doc
