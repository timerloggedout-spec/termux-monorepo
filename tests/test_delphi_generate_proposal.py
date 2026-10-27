"""Offline tests for the Oracle Method proposal generator.

Deterministic: a fabricated evidence set stands in for fetched
evidence. The contract pinned here: evidenced points are asserted with
citations, unresolvable points render UNVERIFIED (never asserted, never
dropped), the author is the system, and the provenance receipt is
complete and honest.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from generate_proposal import generate  # noqa: E402

EVIDENCE = [{
    "schema": "delphi-evidence-set/v1",
    "assembled_at": "2026-10-27T00:00:00Z",
    "items": [
        {"claim": "pr.merged", "value": True,
         "provenance": {"source": "github-api", "path": "/repos/x/pulls/1",
                        "observed_at": "2026-10-27T00:00:00Z"},
         "fresh_until": "2026-10-27T00:15:00Z", "sha256": "a" * 64},
        {"claim": "doc.blob_sha", "value": "deadbeef",
         "provenance": {"source": "github-api", "path": "/repos/x/contents/y",
                        "observed_at": "2026-10-27T00:00:00Z"},
         "fresh_until": "2026-10-27T00:15:00Z", "sha256": "b" * 64},
    ],
}]

BRIEF = {
    "id": "test-proposal",
    "title": "A test proposal",
    "kind": "competition",
    "surface": "Test Surface",
    "deadline": "2026-11-02 11:59 PM PT",
    "deadline_evidence_refs": ["doc.blob_sha"],
    "executive_request": "Do the thing, from evidence.",
    "summary_points": [
        {"text": "The machinery is merged.", "evidence_refs": ["pr.merged"]},
        {"text": "The moon is made of cheese.", "evidence_refs": ["moon.composition"]},
    ],
    "items": [{"item": "Build it", "state": "proposed", "evidence": "exit: done"}],
    "item_prefix": "TP",
}


def test_evidenced_points_asserted_unverified_marked():
    docs = generate(BRIEF, EVIDENCE, generated_at="2026-10-27T00:00:00Z")
    manifest = docs["MANIFEST.md"]
    assert "The machinery is merged." in manifest
    assert "UNVERIFIED: The moon is made of cheese." in manifest
    summary = manifest.split("## Current state")[0]
    assert "UNVERIFIED" not in summary.split("## Unverified")[0].replace(
        "The machinery is merged.", "")


def test_manifest_frontmatter_names_the_system_as_author():
    docs = generate(BRIEF, EVIDENCE, generated_at="2026-10-27T00:00:00Z")
    assert "author: oracle-method" in docs["MANIFEST.md"]
    assert "id: test-proposal" in docs["MANIFEST.md"]


def test_provenance_receipt_is_complete_and_honest():
    docs = generate(BRIEF, EVIDENCE, generated_at="2026-10-27T00:00:00Z")
    prov = json.loads(docs["PROVENANCE.json"])
    assert prov["author"] == "oracle-method"
    assert prov["human_ballots_received"] == 0
    assert prov["external_calls_by_generator"] == 0
    for name in ("MANIFEST.md", "ITEMS.md", "RFP.md"):
        assert prov["documents"][name] == hashlib.sha256(
            docs[name].encode()).hexdigest()


def test_deadline_renders_verified_only_with_resolved_ref():
    docs = generate(BRIEF, EVIDENCE, generated_at="2026-10-27T00:00:00Z")
    assert "**Deadline:** 2026-11-02 11:59 PM PT" in docs["RFP.md"]
    brief2 = dict(BRIEF, deadline_evidence_refs=["missing.claim"])
    docs2 = generate(brief2, EVIDENCE, generated_at="2026-10-27T00:00:00Z")
    assert "UNVERIFIED" in docs2["RFP.md"].split("## 1.")[0]


def test_items_table_rows():
    docs = generate(BRIEF, EVIDENCE, generated_at="2026-10-27T00:00:00Z")
    assert "| TP-001 | Build it | proposed | exit: done |" in docs["ITEMS.md"]


def test_require_plan_refuses_a_planless_proposal():
    brief = {"id": "planless", "title": "No plan", "kind": "research",
             "require_plan": True,
             "summary_points": [], "items": []}
    try:
        generate(brief, [], generated_at="2026-10-27T00:00:00Z")
    except ValueError as exc:
        assert "require_plan" in str(exc)
    else:
        raise AssertionError("a planless proposal under require_plan "
                             "must be refused")


def test_plan_renders_verbatim_in_the_rfp():
    brief = {"id": "planned", "title": "With plan", "kind": "research",
             "require_plan": True,
             "plan": {"steps": ["step one", "step two"],
                      "risks": ["risk one"],
                      "alternatives": ["alt one"]},
             "summary_points": [], "items": []}
    docs = generate(brief, [], generated_at="2026-10-27T00:00:00Z")
    rfp = docs["RFP.md"]
    assert "## 3. Plan" in rfp and "step one" in rfp
    assert "risk one" in rfp and "alt one" in rfp
