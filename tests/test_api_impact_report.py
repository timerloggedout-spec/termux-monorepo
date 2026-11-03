import json
import tempfile
import unittest
from pathlib import Path

from scripts.integrations.api_impact.cli import main, render_markdown
from scripts.integrations.api_impact.report import build_report, classify_changed_paths, normalize_mapper_input

REPO = "timerloggedout-spec/termux-monorepo"
BASE, HEAD = "a" * 40, "b" * 40
PATHS = ["llm_api_hub/server/app.py", "README.md"]


def mapper_input(**overrides):
    evidence = [{"evidence_id": "E-1", "quote": "GET /v1/models", "source": "llm_api_hub/server/app.py:10"}]
    value = {
        "repository": REPO, "pull_request": 42, "base_sha": BASE, "head_sha": HEAD,
        "privacy": {"contains_raw_prompt": False, "contains_secret": False},
        "results": {
            "extraction": {"status": "success", "api_changes_items": [{
                "change_id": "C-1", "change_type": "changed_response_field",
                "location": "GET /v1/models", "before": "id", "after": "id,name",
                "description": "Adds a model name field.", "evidence_ids": ["E-1"]
            }], "missing_fields": [], "evidence": evidence, "errors": []},
            "classification": {"status": "success", "classifications": [{
                "change_id": "C-1", "category": "non_breaking_change", "confidence": "confirmed",
                "rationale": "An optional response field is added.", "evidence_ids": ["E-1"]
            }], "unclassified_items": [], "missing_fields": [], "evidence": evidence, "errors": []},
            "impact_map": {"status": "success", "deliverable": {"impact_items": [{
                "impact_id": "I-1", "change_id": "C-1", "affected_object": "GET /v1/models clients",
                "impact_type": "consumer_compatibility", "recommended_action": "Add a response contract test.",
                "priority": "medium", "status": "confirmed", "evidence_ids": ["E-1"]
            }]}, "included_items": [], "missing_fields": [], "limitations": [], "evidence": evidence, "errors": []}
        }
    }
    value.update(overrides)
    return value


class ApiImpactReportTests(unittest.TestCase):
    def test_configured_paths_detect_api_files_without_false_positive(self):
        self.assertEqual(classify_changed_paths(["llm_api_hub/server/app.py", "README.md", "docs/schemas/unrelated.json"]), ["llm_api_hub/server/app.py"])

    def test_path_traversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe changed path"):
            classify_changed_paths(["../secrets.env"])

    def test_no_api_surface_change_is_not_applicable(self):
        report = build_report(REPO, BASE, HEAD, 42, ["README.md"])
        self.assertEqual((report["state"], report["api_surface_files"]), ("not_applicable", []))

    def test_api_surface_change_without_mapper_requires_analysis(self):
        report = build_report(REPO, BASE, HEAD, 42, PATHS)
        self.assertEqual(report["state"], "analysis_required")
        self.assertEqual(report["api_surface_files"], ["llm_api_hub/server/app.py"])

    def test_valid_mapper_results_are_normalized_and_bound_to_exact_head(self):
        report = build_report(REPO, BASE, HEAD, 42, PATHS, mapper_input())
        self.assertEqual(report["state"], "validated")
        self.assertEqual(report["changes"][0]["change_id"], "C-1")
        self.assertEqual(report["classifications"][0]["category"], "non_breaking_change")
        self.assertEqual(report["impacts"][0]["impact_id"], "I-1")
        self.assertEqual(report["head_sha"], HEAD)

    def test_cannot_determine_remains_partial(self):
        payload = mapper_input()
        payload["results"]["classification"]["classifications"][0].update(category="cannot_determine", confidence="insufficient")
        self.assertEqual(build_report(REPO, BASE, HEAD, 42, PATHS, payload)["state"], "partial")

    def test_stale_mapper_head_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "head SHA mismatch"):
            build_report(REPO, BASE, HEAD, 42, PATHS, mapper_input(head_sha="c" * 40))

    def test_duplicate_change_ids_are_rejected(self):
        payload = mapper_input()
        duplicate = dict(payload["results"]["extraction"]["api_changes_items"][0], location="POST /v1/chat/completions")
        payload["results"]["extraction"]["api_changes_items"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate change_id"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_impact_must_reference_extracted_change(self):
        payload = mapper_input()
        payload["results"]["impact_map"]["deliverable"]["impact_items"][0]["change_id"] = "C-404"
        with self.assertRaisesRegex(ValueError, "unknown change_id"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_evidence_references_must_resolve(self):
        payload = mapper_input()
        payload["results"]["classification"]["classifications"][0]["evidence_ids"] = ["E-404"]
        with self.assertRaisesRegex(ValueError, "unknown evidence_id"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_raw_prompt_or_secret_attestation_is_rejected(self):
        payload = mapper_input()
        payload["privacy"]["contains_raw_prompt"] = True
        with self.assertRaisesRegex(ValueError, "privacy"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_prompt_and_credential_fields_are_rejected(self):
        payload = mapper_input()
        payload["raw_prompt"] = "private"
        with self.assertRaisesRegex(ValueError, "prohibited field"):
            normalize_mapper_input(payload, REPO, BASE, HEAD, 42)

    def test_partial_stage_is_not_promoted_to_validated(self):
        payload = mapper_input()
        payload["results"]["extraction"]["status"] = "partial"
        self.assertEqual(build_report(REPO, BASE, HEAD, 42, PATHS, payload)["state"], "partial")

    def test_report_is_deterministic(self):
        self.assertEqual(
            build_report(REPO, BASE, HEAD, 42, list(reversed(PATHS))),
            build_report(REPO, BASE, HEAD, 42, PATHS),
        )

    def test_change_without_evidence_is_rejected(self):
        payload = mapper_input()
        payload["results"]["extraction"]["api_changes_items"][0]["evidence_ids"] = []
        with self.assertRaisesRegex(ValueError, "must cite evidence"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_conflicting_evidence_ids_are_rejected(self):
        payload = mapper_input()
        payload["results"]["classification"]["evidence"] = [{"evidence_id": "E-1", "quote": "different quote", "source": "llm_api_hub/server/app.py:10"}]
        with self.assertRaisesRegex(ValueError, "conflicting evidence_id"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_mapper_report_must_match_pr_number(self):
        with self.assertRaisesRegex(ValueError, "pull request mismatch"):
            build_report(REPO, BASE, HEAD, 42, PATHS, mapper_input(pull_request=41))

    def test_cli_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path, md_path = Path(directory) / "report.json", Path(directory) / "report.md"
            result = main(["--repository", REPO, "--base", BASE, "--head", HEAD, "--pr-number", "42",
                           "--changed-path", "README.md", "--output-json", str(json_path), "--output-markdown", str(md_path)])
            self.assertEqual(result, 0)
            self.assertEqual(json.loads(json_path.read_text())["state"], "not_applicable")
            self.assertIn("not_applicable", md_path.read_text())

    def test_markdown_preserves_breaking_classification(self):
        payload = mapper_input()
        payload["results"]["classification"]["classifications"][0]["category"] = "changed_response_field"
        rendered = render_markdown(build_report(REPO, BASE, HEAD, 42, PATHS, payload))
        self.assertIn("changed_response_field", rendered)
        self.assertIn("GET /v1/models clients", rendered)

    def test_cli_rejects_stale_mapper_report(self):
        with tempfile.TemporaryDirectory() as directory:
            mapper_path = Path(directory) / "mapper.json"
            mapper_path.write_text(json.dumps(mapper_input(head_sha="c" * 40)))
            result = main(["--repository", REPO, "--base", BASE, "--head", HEAD, "--pr-number", "42",
                           "--changed-path", PATHS[0], "--mapper-input", str(mapper_path),
                           "--output-json", str(Path(directory) / "report.json")])
            self.assertEqual(result, 2)


    def test_control_characters_in_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe changed path"):
            classify_changed_paths(["README.md" + chr(10) + "heading"])

    def test_backslash_paths_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe changed path"):
            classify_changed_paths(["llm_api_hub\\server\\app.py"])

    def test_unsupported_mapper_envelope_fields_are_rejected(self):
        payload = mapper_input()
        payload["extra"] = "not allowed"
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_unsupported_privacy_fields_are_rejected(self):
        payload = mapper_input()
        payload["privacy"]["note"] = "not allowed"
        with self.assertRaisesRegex(ValueError, "privacy contains unsupported fields"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)

    def test_credential_shaped_evidence_is_rejected(self):
        payload = mapper_input()
        payload["results"]["extraction"]["evidence"] = [{
            "evidence_id": "E-SECRET", "quote": "ghp_123456789012345678901234567890", "source": "fixture"
        }]
        with self.assertRaisesRegex(ValueError, "credential-shaped value"):
            build_report(REPO, BASE, HEAD, 42, PATHS, payload)


if __name__ == "__main__":
    unittest.main()
