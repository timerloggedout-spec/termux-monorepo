"""Regression tests for the Help-Wanted stake-to-solution gate."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("gate", Path(__file__).with_name("help_wanted_diff_gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def pr(body=""):
    return {
        "number": 3,
        "html_url": "https://github.com/o/r/pull/3",
        "body": body,
        "base": {"sha": "base", "repo": {"full_name": "o/r"}},
        "head": {"sha": "head"},
    }


def file(name, additions=1, deletions=0, patch="+a meaningful implementation line"):
    return {"filename": name, "additions": additions, "deletions": deletions, "patch": patch}


def solution_body(diff="docs/checklist.md — documents the deployment steps and verification path",
                  validation="python -m pytest tests/test_docs.py — passed"):
    return (
        "### Help-Given Tribute\n"
        "- Stage: solution\n"
        f"- Diff proof: {diff}\n"
        f"- Validation: {validation}\n"
    )


def test_stake_is_not_solution():
    r = gate.classify(pr("stake only"), [file(gate.STAKE_PATH, 8, patch="+Replace this file with a real fix")], "solution")
    assert r["stage"] == "STAKE" and not r["gate_pass"]


def test_stake_is_valid_stake():
    r = gate.classify(pr("stake only"), [file(gate.STAKE_PATH, 8, patch="+Stake note")], "stake")
    assert r["stage"] == "STAKE" and r["gate_pass"]


def test_solution_requires_specific_proof_and_substantive_patch():
    r = gate.classify(pr(solution_body()), [file("docs/checklist.md", 20, patch="+Documented the deployment steps and DNS validation.")], "solution")
    assert r["stage"] == "SOLUTION" and r["gate_pass"]
    assert r["substantive_implementation_files"] == ["docs/checklist.md"]


def test_placeholder_plus_solution_requires_proof():
    r = gate.classify(pr("### Help-Given Tribute\n- Stage: solution"), [
        file(gate.STAKE_PATH, 8, patch="+Replace this file with a real fix"),
        file("docs/checklist.md", 20, patch="+Real implementation"),
    ], "solution")
    assert not r["gate_pass"]


def test_empty_diff_cannot_pass_on_proof_markers():
    r = gate.classify(pr(solution_body()), [file("docs/checklist.md", 0, 0, patch="")], "solution")
    assert not r["gate_pass"]
    assert "no substantive implementation diff verified" in r["reason"]


def test_non_stake_placeholder_file_cannot_pass():
    r = gate.classify(pr(solution_body()), [
        file("docs/checklist.md", 3, patch="+TODO: implementation goes here\n+Replace this file with a real fix")
    ], "solution")
    assert not r["gate_pass"]
    assert r["substantive_implementation_files"] == []


def test_meaningful_deletion_cannot_launder_placeholder_additions():
    r = gate.classify(pr(solution_body()), [
        file("docs/checklist.md", 2, 4,
             patch="-Previously documented deployment behavior.\n-Troubleshooting details.\n+TODO: implementation goes here\n+Replace this file with a real fix")
    ], "solution")
    assert not r["gate_pass"]
    assert r["substantive_implementation_files"] == []


def test_diff_proof_must_name_exact_changed_path():
    body = solution_body(diff="docs/checklist.md.backup describes an unrelated change")
    r = gate.classify(pr(body), [file("docs/checklist.md", 20)], "solution")
    assert not r["gate_pass"]
    assert not r["diff_proof_specific"]


def test_generic_diff_proof_and_validation_are_rejected():
    body = solution_body(diff="docs checklist", validation="CI")
    r = gate.classify(pr(body), [file("docs/checklist.md", 20)], "solution")
    assert not r["gate_pass"]
    assert not r["diff_proof_specific"]
    assert not r["validation_evidence_specific"]


def test_missing_or_truncated_patch_fails_closed():
    r = gate.classify(pr(solution_body()), [{"filename": "docs/checklist.md", "additions": 20, "deletions": 0}], "solution")
    assert not r["gate_pass"]
    assert r["implementation_diff_gaps"]


def test_pending_or_failed_validation_cannot_pass():
    for result in ("python -m pytest tests/test_docs.py — pending CI",
                   "python -m pytest tests/test_docs.py — failed"):
        r = gate.classify(pr(solution_body(validation=result)), [file("docs/checklist.md", 20)], "solution")
        assert not r["gate_pass"]
        assert not r["validation_evidence_specific"]


def test_success_claim_without_recognized_check_is_rejected():
    r = gate.classify(pr(solution_body(validation="Everything checked and passed successfully")),
                      [file("docs/checklist.md", 20)], "solution")
    assert not r["gate_pass"]
    assert not r["validation_evidence_specific"]


def test_recognized_check_with_successful_result_passes():
    r = gate.classify(pr(solution_body(validation="python -m pytest tests/test_docs.py — passed")),
                      [file("docs/checklist.md", 20)], "solution")
    assert r["gate_pass"]
    assert r["validation_evidence_specific"]


def test_regression_sendam_pr_492_stake_only():
    # Historical upstream PR #492 only added the lane-stake placeholder for issue #465.
    body = "Stake only for https://github.com/EF-CHAIN/SendAm/issues/465"
    r = gate.classify(pr(body), [
        file(gate.STAKE_PATH, 8, patch="+Replace this file with a real fix; do not merge stake-only as complete.")
    ], "solution")
    assert r["stage"] == "STAKE" and not r["gate_pass"]


def test_regression_sendam_pr_607_stake_only():
    # Historical upstream PR #607 only added the lane-stake placeholder for issue #538.
    body = "Stake only for https://github.com/EF-CHAIN/SendAm/issues/538"
    r = gate.classify(pr(body), [
        file(gate.STAKE_PATH, 8, patch="+Replace this file with a real fix; do not merge stake-only as complete.")
    ], "solution")
    assert r["stage"] == "STAKE" and not r["gate_pass"]
