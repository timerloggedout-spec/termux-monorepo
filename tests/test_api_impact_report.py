import unittest

from scripts.integrations.api_impact.report import (
    build_report,
    classify_changed_paths,
    normalize_mapper_input,
)


REPOSITORY = "timerloggedout-spec/termux-monorepo"
BASE = "a" * 40
HEAD = "b" * 40
PATHS = ["llm_api_hub/server/app.py", "README.md"]


def mapper_input(**overrides):
    evidence = [{"evidence_id": "E-1", "quote": "GET /v1/models", "source": "llm_api_hub/server/app.py:10"}]
    value = {
        "repository": REPOSITORY,
        "pull_request": 42,
        "base_sha": BASE,
        "head_sha": HEAD,
        "privacy": {"contains_raw_prompt": False, "contains_secret": False},
        "results": {
            "extraction": {
                "status": "success",
                "api_changes_items": [{
                    "change_id": "C-1", "change_type": "changed_response_field",
                    "location": "GET /v1/models", "before": "id", "after": "id,name",
                    "description": "Adds a model name field.", "evidence_ids": ["E-1"]
                }],
                "missing_fields": [], "evidence": evidence, "errors": []
            },
            "classification": {
                "status": "success",
                "classifications": [{
                    "change_id": "C-1", "category": "non_breaking_change",
                    "confidence": "confirmed", "rationale": "An optional response field is added.",
                    "evidence_ids": ["E-1"]
                }],
                "unclassified_items": [], "missing_fields": [], "evidence": evidence, "errors": []
            },
            "impact_map": {
                "status": "success",
                "deliverable": {"impact_items": [{
                    "impact_id": "I-1", "change_id": "C-1",
                    "affected_object": "GET /v1/models clients",
                    "impact_type": "consumer_compatibility",
                    "recommended_action": "Add a response contract test.",
                    "priority": "medium", "status": "confirmed", "evidence_ids": ["E-1"]
                }]},
                "included_items": [], "missing_fields": [], "limitations": [],
                "evidence": evidence, "errors": []
            }
        }
    }
    value.update(overrides)
    return value


class ApiImpactReportTests(unittest.TestCase):
    def test_configured_api_surface_paths_are_detected_without_false_positive(self):
        found = classify_changed_paths([
            "llm_api_hub/server/app.py",
            "README.md",
            "docs/schemas/unrelated.json"
        ])
        self.assertEqual(found, ["llm_api_hub/server/app.py"])

    def test_path_traversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsafe changed path"):
            classify_changed_paths(["../secrets.env"])

    def test_no_api_surface_change_is_not_applicable(self):
        report = build_report(REPOSITORY, BASE, HEAD, 42, ["README.md"])
        self.assertEqual(report["state"], "not_applicable")
        self.assertEqual(report["api_surface_files"], [])

    def test_api_surface_change_without_mapper_output_requires_analysis(self):
        report = build_report(REPOSITORY, BASE, HEAD, 42, PATHS)
        self.assertEqual(report["state"], "analysis_required")
        self.assertEqual(report["api_surface_files"], ["llm_api_hub/server/app.py"])

    def test_valid_mapper_results_are_normalized_and_bound_to_exact_head(self):
        report = build_report(REPOSITORY, BASE, HEAD, 42, PATHS, mapper_input())
        self.assertEqual(report["state"], "validated")
        self.assertEqual(report["changes"][0]["change_id"], "C-1")
        self.assertEqual(report["classifications"][0]["category"], "non_breaking_change")
        self.assertEqual(report["impacts"][0]["impact_id"], "I-1")
        self.assertEqual(report["head_sha"], HEAD)

    def test_cannot_determine_classification_keeps_report_partial(self):
        payload = mapper_input()
        payload["results"]["classification"]["classifications"][0].update({
            "category": "cannot_determine", "confidence": "insufficient"
        })
        report = build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)
        self.assertEqual(report["state"], "partial")

    def test_stale_mapper_head_is_rejected(self):
        payload = mapper_input(head_sha="c" * 40)
        with self.assertRaisesRegex(ValueError, "head SHA mismatch"):
            build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)

    def test_mapper_change_ids_must_be_unique(self):
        payload = mapper_input()
        duplicate = dict(payload["results"]["extraction"]["api_changes_items"][0])
        duplicate["location"] = "POST /v1/chat/completions"
        payload["results"]["extraction"]["api_changes_items"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate change_id"):
            build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)

    def test_impact_must_reference_an_extracted_change(self):
        payload = mapper_input()
        payload["results"]["impact_map"]["deliverable"]["impact_items"][0]["change_id"] = "C-404"
        with self.assertRaisesRegex(ValueError, "unknown change_id"):
            build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)

    def test_all_evidence_references_must_resolve(self):
        payload = mapper_input()
        payload["results"]["classification"]["classifications"][0]["evidence_ids"] = ["E-404"]
        with self.assertRaisesRegex(ValueError, "unknown evidence_id"):
            build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)

    def test_raw_prompt_or_secret_attestation_is_rejected(self):
        payload = mapper_input()
        payload["privacy"]["contains_raw_prompt"] = True
        with self.assertRaisesRegex(ValueError, "privacy"):
            build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)

    def test_prompt_and_credential_fields_are_rejected(self):
        payload = mapper_input()
        payload["raw_prompt"] = "private"
        with self.assertRaisesRegex(ValueError, "prohibited field"):
            normalize_mapper_input(payload, REPOSITORY, BASE, HEAD, 42)

    def test_partial_mapper_status_is_not_promoted_to_validated(self):
        payload = mapper_input()
        payload["results"]["extraction"]["status"] = "partial"
        report = build_report(REPOSITORY, BASE, HEAD, 42, PATHS, payload)
        self.assertEqual(report["state"], "partial")

    def test_report_is_deterministic_for_same_inputs(self):
        first = build_report(REPOSITORY, BASE, HEAD, 42, list(reversed(PATHS)))
        second = build_report(REPOSITORY, BASE, HEAD, 42, PATHS)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
