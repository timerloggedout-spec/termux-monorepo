"""Offline tests for the Operator Matrix generator.

Classification follows the #175 vocabulary and is evidence-first:
a PR is only EXTRACT/CANDIDATE when BOTH dual gates are green on its
head; SUPERSEDE is never auto-emitted.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "issue_lifecycle"))

from operator_matrix import build_matrix, classify_pr, lane_family, render_md  # noqa: E402

GREEN = {"hygiene": "success", "smoke": "success"}


def pr(**kw):
    base = {"number": 1, "title": "t", "labels": [], "gates": dict(GREEN), "mergeable": True, "mergeable_state": "clean", "draft": False, "head_sha": "a" * 40, "updated_at": "2026-10-28T00:00:00Z"}
    base.update(kw)
    return base


def test_extract_requires_both_gates_and_mergeable():
    assert classify_pr(pr()) == "EXTRACT"


def test_candidate_when_gates_green_but_not_mergeable():
    assert classify_pr(pr(mergeable=False, mergeable_state="dirty")) == "CANDIDATE"
    assert classify_pr(pr(draft=True)) == "CANDIDATE"
    assert classify_pr(pr(mergeable=None, mergeable_state="unknown")) == "CANDIDATE"


def test_need_evidence_when_any_gate_not_green():
    assert classify_pr(pr(gates={"hygiene": "failure", "smoke": "success"})) == "NEED_EVIDENCE"
    assert classify_pr(pr(gates={"hygiene": "success"})) == "NEED_EVIDENCE"  # smoke not reported
    assert classify_pr(pr(gates={})) == "NEED_EVIDENCE"


def test_lane_family_rules():
    assert lane_family([]) == "unlabelled"
    assert lane_family(["delphi:rfp", "delphi:parked"]) == "delphi"
    assert lane_family(["security"]) == "security"
    assert lane_family(["proposal"]) == "proposal"
    assert lane_family(["whatever"]) == "other"


def test_build_matrix_counts_and_no_supersede():
    snap = {
        "master": {"sha": "b" * 40, "gates": dict(GREEN)},
        "issues": [
            {"number": 7, "title": "x", "labels": [], "created_at": "", "updated_at": ""},
            {"number": 8, "title": "y", "labels": ["delphi:rfp"], "created_at": "", "updated_at": ""},
        ],
        "prs": [pr(number=1), pr(number=2, gates={})],
    }
    m = build_matrix(snap, "2026-10-28T00:00:00Z")
    assert m["counts"]["pr_classes"] == {"EXTRACT": 1, "CANDIDATE": 0, "NEED_EVIDENCE": 1, "SUPERSEDE": 0}
    assert m["master"]["functional_gate"] == "GREEN"
    assert m["issues_unlabelled"] == [7]
    md = render_md(m)
    assert "#1" in md and "EXTRACT" in md and "NEED_EVIDENCE" in md


def test_master_gate_not_established_without_both_gates():
    m = build_matrix({"master": {"sha": "b" * 40, "gates": {"hygiene": "success"}}, "issues": [], "prs": []}, "t")
    assert m["master"]["functional_gate"] == "NOT ESTABLISHED"
