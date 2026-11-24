"""Contract tests for the separate Delphi Oracle general-intake path."""
from pathlib import Path
import json
import shutil
import tempfile
import unittest

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
        "Round maximum / custom count": "3",
        "Stopping criteria / stability definition": "Stop on predeclared stability or maximum rounds; preserve dissent.",
        "Question Matrix strategy": "Shared matrix across all rounds",
        "Selection disposition": "Deliberation only",
        "Research question / objectives": "Which research capabilities improve validated outcomes?",
    }
    defaults.update(sections)
    return "\n\n".join(f"### {key}\n\n{value}" for key, value in defaults.items())


def checked(*values):
    return "\n".join(f"- [x] {value}" for value in values)


class DelphiIntakeContractTests(unittest.TestCase):
    def normalize(self, sections=None, issue=None, root=ROOT):
        return intake.normalize_intake(issue or ISSUE, body(sections), root)

    def test_prior_default_is_all_twelve_baseline_participants_only(self):
        record = self.normalize()
        cohort = record["research_selection"]
        self.assertEqual(cohort["mode"], "Prior default")
        self.assertEqual(len(cohort["participants"]), 12)
        self.assertEqual(cohort["arms"], ["baseline"])
        self.assertEqual(cohort["doe_components"], [])
        self.assertEqual(cohort["methodology_rfps"], [])
        self.assertEqual(cohort["projects"], [])
        self.assertIs(record["execution"], False)

    def test_all_selects_full_registered_research_catalogue_and_all_arms(self):
        record = self.normalize({"Research selection mode": checked("All")})
        cohort = record["research_selection"]
        self.assertEqual(len(cohort["participants"]), 12)
        self.assertEqual(len(cohort["doe_components"]), 4)
        self.assertEqual(len(cohort["methodology_rfps"]), 5)
        self.assertEqual(len(cohort["projects"]), 3)
        self.assertEqual(cohort["arms"], ["baseline", "rnd", "selected", "control"])
        self.assertEqual(
            cohort["comparison_policy"],
            "within_segment_only; no cross-silo score aggregation",
        )

    def test_doe_decides_records_candidates_without_making_a_selection(self):
        record = self.normalize({
            "Research selection mode": checked("DoE Decides"),
            "DoE components": checked("bayesian.routing — Bayesian routing and uncertainty"),
        })
        cohort = record["research_selection"]
        self.assertEqual(cohort["status"], "pending_doe_decision")
        self.assertEqual(cohort["authority"], "DoE")
        self.assertEqual(
            [item["id"] for item in cohort["doe_components"]], ["bayesian.routing"]
        )
        self.assertIs(record["execution"], False)

    def test_specific_selection_uses_only_checked_items_and_baseline_arm_default(self):
        record = self.normalize({
            "Research selection mode": checked("Specific selection"),
            "Research participants": checked(
                "research.jogyo-research-lab — Primary exemplar"
            ),
            "Related methodology RFPs": checked("#1959 — doe-criteria-loop"),
        })
        cohort = record["research_selection"]
        self.assertEqual(
            [item["id"] for item in cohort["participants"]],
            ["research.jogyo-research-lab"],
        )
        self.assertEqual(cohort["doe_components"], [])
        self.assertEqual(cohort["methodology_rfps"], [
            {"issue_number": 1959, "surface_id": "doe-criteria-loop"}
        ])
        self.assertEqual(cohort["arms"], ["baseline"])

    def test_specific_selection_requires_at_least_one_catalogue_item(self):
        with self.assertRaisesRegex(ValueError, "requires at least one"):
            self.normalize({"Research selection mode": checked("Specific selection")})

    def test_multiple_selection_modes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "select exactly one"):
            self.normalize({
                "Research selection mode": checked("All", "Prior default")
            })

    def test_unknown_checkbox_values_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown research participant"):
            self.normalize({
                "Research selection mode": checked("Specific selection"),
                "Research participants": checked(
                    "research.not-registered — invented participant"
                ),
            })

    def test_question_matrix_schedule_and_optional_webview_are_preserved(self):
        record = self.normalize({
            "Question Matrix strategy": "Alternating-round expansion",
            "Per-round Question Matrix schedule": (
                "Round 1: QM-001\nRound 2: add evidence gaps"
            ),
            "Human WebView oversight": checked(
                "Request optional human WebView oversight"
            ),
            "Request category": "Harmoniously reconcile multiple projects",
            "Harmonious Reconciliation dimensions": checked(
                "Dependencies and integration points",
                "Existing decisions and unresolved dissent",
            ),
        })
        self.assertEqual(
            record["delphi"]["question_matrix"]["strategy"],
            "Alternating-round expansion",
        )
        self.assertEqual(
            record["delphi"]["question_matrix"]["per_round_schedule"],
            "Round 1: QM-001\nRound 2: add evidence gaps",
        )
        self.assertEqual(record["panel"]["context"], "Termux-monorepo")
        self.assertIs(record["panel"]["human_webview_oversight"], True)
        self.assertEqual(record["reconciliation"]["mode"], "harmonious_reconciliation")
        self.assertEqual(len(record["reconciliation"]["dimensions"]), 2)
        self.assertIs(record["execution"], False)

    def test_selection_review_and_catalogue_dispositions_are_independent(self):
        review = self.normalize({"Selection disposition": "Selection review"})
        catalogue = self.normalize({"Selection disposition": "Registry catalogue"})
        both = self.normalize({"Selection disposition": "Both"})
        self.assertIs(review["disposition"]["selection_review"], True)
        self.assertIs(review["disposition"]["catalogue_write"], False)
        self.assertIs(catalogue["disposition"]["selection_review"], False)
        self.assertIs(catalogue["disposition"]["catalogue_write"], True)
        self.assertIs(both["disposition"]["selection_review"], True)
        self.assertIs(both["disposition"]["catalogue_write"], True)

    def test_missing_baseline_issue_is_preserved_as_null(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "ops").mkdir()
            (root / "docs").mkdir()
            for relative in ("ops/delphi", "ops/doe", "docs/proposals"):
                shutil.copytree(ROOT / relative, root / relative)
            participants_path = root / "ops/delphi/research-participants.json"
            participants = json.loads(participants_path.read_text())
            participants["participants"][0]["filings"]["baseline"] = None
            participants_path.write_text(json.dumps(participants))
            record = self.normalize({
                "Research selection mode": checked("Specific selection"),
                "Research participants": checked(
                    "research.jogyo-research-lab — Primary exemplar"
                ),
            }, root=root)
            participant = record["research_selection"]["participants"][0]
            self.assertIsNone(participant["baseline_issue"])

    def test_issue_revision_changes_record_hash_but_keeps_selection_identity(self):
        first = self.normalize()
        revised_issue = dict(ISSUE, updated_at="2026-11-24T01:00:00Z")
        second = self.normalize(
            {"Research question / objectives": "A revised research question"},
            issue=revised_issue,
        )
        self.assertEqual(first["selection_id"], second["selection_id"])
        self.assertNotEqual(first["record_sha256"], second["record_sha256"])

    def test_one_pass_rubric_requires_single_pass_profile(self):
        record = self.normalize({
            "Delphi methodology": "One-pass rubric (not a multi-round Delphi study)",
            "Round profile": "Single-pass (one assessment)",
            "Stopping criteria / stability definition": "",
        })
        self.assertEqual(record["delphi"]["round_maximum"], 1)

    def test_adaptive_rounds_require_stopping_criteria(self):
        with self.assertRaisesRegex(ValueError, "require declared stopping criteria"):
            self.normalize({"Stopping criteria / stability definition": ""})

    def test_fixed_four_or_five_round_profile_requires_matching_maximum(self):
        with self.assertRaisesRegex(ValueError, "requires a round maximum of 4 or 5"):
            self.normalize({
                "Round profile": "Fixed 4–5 rounds",
                "Round maximum / custom count": "3",
            })

    def test_form_exposes_all_source_catalogue_checkbox_options(self):
        form = (ROOT / ".github/ISSUE_TEMPLATE/delphi-oracle-intake.yml").read_text()
        catalogues = intake.load_catalogues(ROOT)
        for item_id in catalogues["participants"]:
            self.assertIn(item_id, form)
        for item_id in catalogues["components"]:
            self.assertIn(item_id, form)
        for issue_id, surface_id in catalogues["method_rfps"].items():
            self.assertIn(f"#{issue_id} — {surface_id}", form)
        self.assertIn("DoE Decides", form)
        self.assertIn("Prior default", form)
        self.assertIn("Specific selection", form)

    def test_catalogue_contract_keeps_execution_disabled(self):
        record = self.normalize()
        self.assertIs(record["execution"], False)
        self.assertTrue(
            record["research_selection"]["comparison_policy"].startswith("within_segment_only")
        )

    def test_workflow_isolated_from_quota_gate_and_keeps_execution_disabled(self):
        workflow = (ROOT / ".github/workflows/delphi-oracle-intake.yml").read_text()
        form = (ROOT / ".github/ISSUE_TEMPLATE/delphi-oracle-intake.yml").read_text()
        self.assertIn("issues:", workflow)
        self.assertIn("opened, edited", workflow)
        self.assertNotIn("delphi:rfp", form)
        self.assertIn("delphi:selection-review", workflow)
        self.assertIn("heads/master", workflow)
        self.assertIn("execution", workflow)
        self.assertIn("false", workflow)
        self.assertIn("pulls.create", workflow)


if __name__ == "__main__":
    unittest.main()
