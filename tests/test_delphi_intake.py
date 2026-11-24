"""Contract tests for the separate Delphi Oracle general-intake path."""
from pathlib import Path

import pytest

from scripts.delphi import intake

ROOT = Path(__file__).resolve().parents[1]
ISSUE = {
    "number": 60001,
    "title": "[delphi:intake] test",
    "html_url": "https://github.com/timerloggedout-spec/termux-monorepo/issues/60001",
    "user": {"login": "test-operator"},
    "created_at": "2026-11-24T00:00:00Z",
    "updated_at": "2026-11-24T00:00:00Z",
}


def body(sections=None):
    sections = sections or {}
    defaults = {
        "Request category": "Conduct research or evidence review",
        "Delphi methodology": "Oracle recommends",
        "Round profile": "Adaptive with declared stopping criteria",
        "Question Matrix strategy": "Shared matrix across all rounds",
        "Selection disposition": "Deliberation only",
        "Research question / objectives": "Which research capabilities improve validated outcomes?",
    }
    defaults.update(sections)
    return "\n\n".join(f"### {key}\n\n{value}" for key, value in defaults.items())


def checked(*values):
    return "\n".join(f"- [x] {value}" for value in values)


def test_prior_default_is_all_twelve_baseline_participants_only():
    record = intake.normalize_intake(ISSUE, body(), ROOT)
    cohort = record["research_selection"]
    assert cohort["mode"] == "Prior default"
    assert len(cohort["participants"]) == 12
    assert cohort["arms"] == ["baseline"]
    assert cohort["doe_components"] == []
    assert cohort["methodology_rfps"] == []
    assert cohort["projects"] == []
    assert record["execution"] is False


def test_all_selects_full_registered_research_catalogue_and_all_arms():
    record = intake.normalize_intake(
        ISSUE, body({"Research selection mode": checked("All")}), ROOT
    )
    cohort = record["research_selection"]
    assert len(cohort["participants"]) == 12
    assert len(cohort["doe_components"]) == 4
    assert len(cohort["methodology_rfps"]) == 5
    assert len(cohort["projects"]) == 3
    assert cohort["arms"] == ["baseline", "rnd", "selected", "control"]
    assert cohort["comparison_policy"] == "within_segment_only; no cross-silo score aggregation"


def test_doe_decides_records_candidates_without_making_a_selection():
    record = intake.normalize_intake(
        ISSUE,
        body({
            "Research selection mode": checked("DoE Decides"),
            "DoE components": checked("bayesian.routing — Bayesian routing and uncertainty"),
        }),
        ROOT,
    )
    cohort = record["research_selection"]
    assert cohort["status"] == "pending_doe_decision"
    assert cohort["authority"] == "DoE"
    assert [item["id"] for item in cohort["doe_components"]] == ["bayesian.routing"]
    assert record["execution"] is False


def test_specific_selection_uses_only_checked_items_and_baseline_arm_default():
    record = intake.normalize_intake(
        ISSUE,
        body({
            "Research selection mode": checked("Specific selection"),
            "Research participants": checked("research.jogyo-research-lab — Primary exemplar"),
            "Related methodology RFPs": checked("#1959 — doe-criteria-loop"),
        }),
        ROOT,
    )
    cohort = record["research_selection"]
    assert [item["id"] for item in cohort["participants"]] == ["research.jogyo-research-lab"]
    assert cohort["doe_components"] == []
    assert cohort["methodology_rfps"] == [
        {"issue_number": 1959, "surface_id": "doe-criteria-loop"}
    ]
    assert cohort["arms"] == ["baseline"]


def test_specific_selection_requires_at_least_one_catalogue_item():
    with pytest.raises(ValueError, match="requires at least one"):
        intake.normalize_intake(
            ISSUE,
            body({"Research selection mode": checked("Specific selection")}),
            ROOT,
        )


def test_multiple_selection_modes_fail_closed():
    with pytest.raises(ValueError, match="select exactly one"):
        intake.normalize_intake(
            ISSUE,
            body({"Research selection mode": checked("All", "Prior default — 12 baseline research participants")}),
            ROOT,
        )


def test_unknown_checkbox_values_fail_closed():
    with pytest.raises(ValueError, match="unknown research participant"):
        intake.normalize_intake(
            ISSUE,
            body({
                "Research selection mode": checked("Specific selection"),
                "Research participants": checked("research.not-registered — invented participant"),
            }),
            ROOT,
        )


def test_question_matrix_schedule_and_optional_webview_are_preserved():
    record = intake.normalize_intake(
        ISSUE,
        body({
            "Question Matrix strategy": "Alternating-round expansion",
            "Per-round Question Matrix schedule": "Round 1: QM-001\nRound 2: add evidence gaps",
            "Human WebView oversight": checked("Request optional human WebView oversight"),
            "Request category": "Harmoniously reconcile multiple projects",
            "Harmonious Reconciliation dimensions": checked(
                "Dependencies and integration points", "Existing decisions and unresolved dissent"
            ),
        }),
        ROOT,
    )
    assert record["delphi"]["question_matrix"]["strategy"] == "Alternating-round expansion"
    assert record["delphi"]["question_matrix"]["per_round_schedule"] == "Round 1: QM-001\nRound 2: add evidence gaps"
    assert record["panel"]["context"] == "Termux-monorepo"
    assert record["panel"]["human_webview_oversight"] is True
    assert record["reconciliation"]["mode"] == "harmonious_reconciliation"
    assert len(record["reconciliation"]["dimensions"]) == 2
    assert record["execution"] is False


def test_selection_review_and_catalogue_dispositions_are_independent():
    review = intake.normalize_intake(
        ISSUE, body({"Selection disposition": "Selection review"}), ROOT
    )
    catalogue = intake.normalize_intake(
        ISSUE, body({"Selection disposition": "Registry catalogue"}), ROOT
    )
    both = intake.normalize_intake(
        ISSUE, body({"Selection disposition": "Both"}), ROOT
    )
    assert review["disposition"]["selection_review"] is True
    assert review["disposition"]["catalogue_write"] is False
    assert catalogue["disposition"]["selection_review"] is False
    assert catalogue["disposition"]["catalogue_write"] is True
    assert both["disposition"]["selection_review"] is True
    assert both["disposition"]["catalogue_write"] is True


def test_missing_baseline_issue_is_preserved_as_null():
    record = intake.normalize_intake(
        ISSUE,
        body({
            "Research selection mode": checked("Specific selection"),
            "Research participants": checked(
                "research.3rdcore-research-project-template — Lightning and Hydra"
            ),
        }),
        ROOT,
    )
    participant = record["research_selection"]["participants"][0]
    assert participant["baseline_issue"] is None


def test_issue_revision_changes_record_hash_but_keeps_selection_identity():
    first = intake.normalize_intake(ISSUE, body(), ROOT)
    revised_issue = dict(ISSUE, updated_at="2026-11-24T01:00:00Z")
    second = intake.normalize_intake(revised_issue, body({"Research question / objectives": "A revised research question"}), ROOT)
    assert first["selection_id"] == second["selection_id"]
    assert first["record_sha256"] != second["record_sha256"]


def test_form_exposes_all_source_catalogue_checkbox_options():
    form = (ROOT / ".github/ISSUE_TEMPLATE/delphi-oracle-intake.yml").read_text()
    catalogues = intake.load_catalogues(ROOT)
    for item_id in catalogues["participants"]:
        assert item_id in form
    for item_id in catalogues["components"]:
        assert item_id in form
    for issue_id, surface_id in catalogues["method_rfps"].items():
        assert f"#{issue_id} — {surface_id}" in form
    assert "DoE Decides" in form and "Prior default" in form and "Specific selection" in form


def test_catalogue_contract_keeps_execution_disabled():
    record = intake.normalize_intake(ISSUE, body(), ROOT)
    assert record["execution"] is False
    assert record["research_selection"]["comparison_policy"].startswith("within_segment_only")
