"""Offline tests for the deterministic issue-lifecycle triage pass.

Pins the G1 fix contract (docs/ops/ISSUE-LIFECYCLE.md): the pass labels
only unlabelled issues, only from title-prefix rules, only with labels
that already exist in the repo taxonomy, and never touches a labelled
issue.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "issue_lifecycle"))

from triage_labels import KNOWN_LABELS, propose_labels  # noqa: E402


def test_proposal_investigate_gets_proposal_and_research():
    title = "Proposal: investigate TanStack AI 1.0 (stable provider adapters)"
    assert propose_labels(title, []) == ["proposal", "research"]


def test_plain_proposal_gets_proposal_only():
    assert propose_labels("Proposal: DOE pilot 1 - context routing", []) == ["proposal"]
    assert propose_labels("[proposal] mistral.workflows: dispatch overlay", []) == ["proposal"]


def test_target_brief_gets_target_label():
    assert propose_labels("[target] wolframalpha: api-extraction", []) == ["target-brief"]


def test_delphi_rfp_gets_delphi_label():
    assert propose_labels("[delphi:rfp] turso.free", []) == ["delphi:rfp"]


def test_bug_prefix_gets_bug():
    assert propose_labels("bug: gate fails on empty diff", []) == ["bug"]
    assert propose_labels("[bug] crash on startup", []) == ["bug"]


def test_labelled_issue_is_never_touched():
    assert propose_labels("Proposal: investigate X", ["proposal"]) == []
    assert propose_labels("[target] y: api-extraction", ["target-brief"]) == []


def test_unmatched_title_gets_nothing():
    assert propose_labels("BIUDL: Build the evidence-driven cockpit", []) == []
    assert propose_labels("[mesh] Integration mesh matrix - standing thread", []) == []
    assert propose_labels("", []) == []
    assert propose_labels(None, []) == []


def test_proposed_labels_always_exist_in_taxonomy():
    titles = [
        "Proposal: investigate A",
        "Proposal: build B",
        "[target] c: cli-adapter",
        "[delphi:rfp] d.free",
        "bug: e",
    ]
    for title in titles:
        for label in propose_labels(title, []):
            assert label in KNOWN_LABELS
