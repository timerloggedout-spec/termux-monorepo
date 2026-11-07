import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

from orchestration_contract_validator import validate_contracts, validate_issue_comment_router_contracts


class OrchestrationContractValidatorTests(unittest.TestCase):
    def test_repository_contracts_pass(self):
        self.assertEqual(validate_contracts(), [])

    def test_missing_receipt_schema_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schema_dir = root / "docs" / "ops"
            schema_dir.mkdir(parents=True)
            treatment = ROOT / "docs" / "ops" / "ORCHESTRATION-TREATMENT.schema.json"
            (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(treatment.read_text())
            errors = validate_contracts(root)
            self.assertTrue(any("ORCHESTRATION-RECEIPT.schema.json" in error for error in errors))

    def test_malformed_nested_property_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schema_dir = root / "docs" / "ops"
            schema_dir.mkdir(parents=True)
            treatment = json.loads((ROOT / "docs" / "ops" / "ORCHESTRATION-TREATMENT.schema.json").read_text())
            treatment["properties"]["status"] = None
            (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(json.dumps(treatment))
            (schema_dir / "ORCHESTRATION-RECEIPT.schema.json").write_text("not json")
            skill_dir = root / ".agents" / "skills" / "orchestration-treatment-registry"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("references")

            errors = validate_contracts(root)
            self.assertTrue(any("status lifecycle enum drifted" in error for error in errors))
            self.assertTrue(any("cannot read valid JSON" in error for error in errors))

    def test_malformed_top_level_schema_structures_are_reported_without_crashing(self):
        cases = (
            ("properties", None, "properties must be an object"),
            ("properties", [], "properties must be an object"),
            ("properties", "bad", "properties must be an object"),
            ("required", None, "required must be a string array"),
            ("required", "bad", "required must be a string array"),
            ("required", [{}], "required must be a string array"),
        )
        for key, value, diagnostic in cases:
            with self.subTest(key=key, value=value):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    schema_dir = root / "docs" / "ops"
                    schema_dir.mkdir(parents=True)
                    treatment = json.loads((ROOT / "docs/ops/ORCHESTRATION-TREATMENT.schema.json").read_text())
                    treatment[key] = value
                    (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(json.dumps(treatment))
                    receipt = ROOT / "docs/ops/ORCHESTRATION-RECEIPT.schema.json"
                    (schema_dir / "ORCHESTRATION-RECEIPT.schema.json").write_text(receipt.read_text())
                    skill_dir = root / ".agents/skills/orchestration-treatment-registry"
                    skill_dir.mkdir(parents=True)
                    (skill_dir / "SKILL.md").write_text((ROOT / ".agents/skills/orchestration-treatment-registry/SKILL.md").read_text())
                    errors = validate_contracts(root)
                    self.assertTrue(any(diagnostic in error for error in errors), errors)

    def test_unhashable_enum_entries_and_nested_values_are_reported_without_crashing(self):
        for invalid in ([{}], [[], "TASK_PASS"], {"enum": [None]}):
            with self.subTest(invalid=invalid):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    schema_dir = root / "docs" / "ops"
                    schema_dir.mkdir(parents=True)
                    treatment = json.loads((ROOT / "docs/ops/ORCHESTRATION-TREATMENT.schema.json").read_text())
                    receipt = json.loads((ROOT / "docs/ops/ORCHESTRATION-RECEIPT.schema.json").read_text())
                    treatment["properties"]["status"]["enum"] = invalid if not isinstance(invalid, dict) else invalid["enum"]
                    receipt["properties"]["outcome"]["enum"] = invalid if not isinstance(invalid, dict) else invalid["enum"]
                    (schema_dir / "ORCHESTRATION-TREATMENT.schema.json").write_text(json.dumps(treatment))
                    (schema_dir / "ORCHESTRATION-RECEIPT.schema.json").write_text(json.dumps(receipt))
                    skill_dir = root / ".agents/skills/orchestration-treatment-registry"
                    skill_dir.mkdir(parents=True)
                    (skill_dir / "SKILL.md").write_text((ROOT / ".agents/skills/orchestration-treatment-registry/SKILL.md").read_text())
                    errors = validate_contracts(root)
                    self.assertTrue(any("status lifecycle enum drifted" in error for error in errors), errors)
                    self.assertTrue(any("outcome enum drifted" in error for error in errors), errors)

    def test_receipt_schema_rejects_state_outcome_conflation(self):
        receipt_path = ROOT / "docs" / "ops" / "ORCHESTRATION-RECEIPT.schema.json"
        schema = json.loads(receipt_path.read_text())
        schema["properties"]["outcome"]["enum"] = ["COMPLETED", "FAILED"]
        with tempfile.TemporaryDirectory() as tmp:
            fixture_root = Path(tmp)
            (fixture_root / "docs" / "ops").mkdir(parents=True)
            skill_dir = fixture_root / ".agents" / "skills" / "orchestration-treatment-registry"
            skill_dir.mkdir(parents=True)
            for name in ("ORCHESTRATION-TREATMENT.schema.json",):
                source = ROOT / "docs" / "ops" / name
                (fixture_root / "docs" / "ops" / name).write_text(source.read_text())
            (fixture_root / "docs" / "ops" / "ORCHESTRATION-RECEIPT.schema.json").write_text(json.dumps(schema))
            skill_source = ROOT / ".agents" / "skills" / "orchestration-treatment-registry" / "SKILL.md"
            (skill_dir / "SKILL.md").write_text(skill_source.read_text())
            errors = validate_contracts(fixture_root)
            self.assertTrue(any("outcome enum drifted" in error for error in errors))


ROUTER_WORKFLOW_PATHS = (
    ".github/workflows/issue-comment-router.yml",
    ".github/workflows/agent-review-auto-jules.yml",
    ".github/workflows/gemini-dispatch.yml",
    ".github/workflows/agent-jules-on-issues.yml",
)


class IssueCommentRouterContractTests(unittest.TestCase):
    def _fixture(self, root):
        for relative in ROUTER_WORKFLOW_PATHS:
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        return root

    def test_repository_router_contracts_pass(self):
        self.assertEqual(validate_issue_comment_router_contracts(ROOT), [])

    def test_target_direct_issue_comment_subscription_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            target = root / ".github/workflows/gemini-dispatch.yml"
            text = target.read_text(encoding="utf-8")
            text = text.replace(
                "  workflow_call:\n",
                "  issue_comment:\n    types: [created]\n  workflow_call:\n",
                1,
            )
            target.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("must not directly subscribe to issue_comment" in error for error in errors), errors)

    def test_missing_reusable_route_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            router = root / ".github/workflows/issue-comment-router.yml"
            text = router.read_text(encoding="utf-8").replace(
                "uses: ./.github/workflows/gemini-dispatch.yml",
                "uses: ./.github/workflows/missing-gemini-route.yml",
                1,
            )
            router.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("missing reusable route: gemini-dispatch" in error for error in errors), errors)

    def test_stale_comment_revision_guard_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            target = root / ".github/workflows/gemini-dispatch.yml"
            text = target.read_text(encoding="utf-8").replace(
                "comment.updated_at === expectedUpdatedAt",
                "false",
                1,
            )
            target.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("must reject stale comment revisions" in error for error in errors), errors)

    def test_jules_route_must_remain_non_pr_and_exact_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            router = root / ".github/workflows/issue-comment-router.yml"
            text = router.read_text(encoding="utf-8").replace("!isPullRequest", "isPullRequest", 1)
            router.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("Jules route must remain" in error for error in errors), errors)

    def test_gemini_route_must_preserve_all_exact_prefixes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            router = root / ".github/workflows/issue-comment-router.yml"
            text = router.read_text(encoding="utf-8").replace("body.startsWith('@sparkFlux') || ", "", 1)
            router.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("Gemini route must remain" in error for error in errors), errors)

    def test_agent_review_route_must_remain_provider_bot_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            router = root / ".github/workflows/issue-comment-router.yml"
            text = router.read_text(encoding="utf-8").replace("actor.type === 'Bot'", "actor.type === 'User'", 1)
            router.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("Agent review route must remain" in error for error in errors), errors)

    def test_reusable_target_rejects_expression_interpolation_in_shell_run_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            target = root / ".github/workflows/agent-jules-on-issues.yml"
            text = target.read_text(encoding="utf-8").replace(
                "          mkdir -p .agent-context",
                "          echo \" ${{ github.event.comment.body }}\"\n          mkdir -p .agent-context",
                1,
            )
            target.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("never inline script/run source" in error for error in errors), errors)

    def test_reusable_target_rejects_expression_interpolation_in_script_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            target = root / ".github/workflows/agent-review-auto-jules.yml"
            text = target.read_text(encoding="utf-8").replace(
                "            const event = context.eventName;",
                "            const unsafe = '${{ inputs.source_event }}';\n            const event = context.eventName;",
                1,
            )
            target.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("never inline script/run source" in error for error in errors), errors)

    def test_target_execution_must_depend_on_comment_revision_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            target = root / ".github/workflows/gemini-dispatch.yml"
            text = target.read_text(encoding="utf-8").replace(
                "    needs: validate-source-comment\n",
                "",
                1,
            )
            target.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("execution job must depend on source-comment validation" in error for error in errors), errors)

    def test_router_must_not_inherit_all_repository_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            router = root / ".github/workflows/issue-comment-router.yml"
            text = router.read_text(encoding="utf-8").replace(
                "GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}",
                "secrets: inherit",
                1,
            )
            router.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("must not inherit the entire repository secret set" in error for error in errors), errors)

    def test_router_must_not_cancel_distinct_comment_revisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._fixture(Path(tmp))
            router = root / ".github/workflows/issue-comment-router.yml"
            text = router.read_text(encoding="utf-8").replace(
                "cancel-in-progress: false",
                "cancel-in-progress: true",
                1,
            )
            router.write_text(text, encoding="utf-8")
            errors = validate_issue_comment_router_contracts(root)
            self.assertTrue(any("must not cancel a distinct comment event" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
