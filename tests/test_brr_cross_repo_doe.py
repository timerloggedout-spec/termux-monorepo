import json
import tempfile
import unittest
from pathlib import Path

import jsonschema

from scripts.doe import brr_cross_repo_doe as evaluator


SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_BASE = "c" * 40


def target_id(repository, branch, sha):
    return f"{repository}::{branch}@{sha}"


def make_dataset(coverage_state="COMPLETE"):
    repo_a = "timerloggedout-spec/parser-a"
    repo_b = "timerloggedout-spec/parser-b"
    repo_c = "timerloggedout-spec/parser-c"
    target_a = target_id(repo_a, "feature/parser-regression", SHA_A)
    target_b = target_id(repo_b, "feature/parser-regression", SHA_B)
    target_c = target_id(repo_c, "candidate/parser-regression", SHA_A)
    source_coverage = "COMPLETE" if coverage_state == "COMPLETE" else "PARTIAL"
    return {
        "schema": "brr-cross-repo-doe-dataset/v1",
        "observed_at": "2026-11-23T12:00:00Z",
        "baseline_sha": SHA_BASE,
        "candidate_sha": SHA_A,
        "coverage": {
            "state": coverage_state,
            "repositories": [repo_a, repo_b, repo_c],
            "next_page": None if coverage_state == "COMPLETE" else 2,
        },
        "sources": [
            {
                "kind": "brr",
                "repository": repo_a,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-a",
            },
            {
                "kind": "commits",
                "repository": repo_a,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-a/commits",
            },
            {
                "kind": "regressions",
                "repository": repo_a,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-a/actions",
            },
            {
                "kind": "gold_set",
                "adjudication_status": "human_adjudicated",
                "repository": repo_a,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-a/issues",
            },
            {
                "kind": "brr",
                "repository": repo_b,
                "sha": SHA_B,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-b",
            },
            {
                "kind": "commits",
                "repository": repo_b,
                "sha": SHA_B,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-b/commits",
            },
            {
                "kind": "brr",
                "repository": repo_c,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-c",
            },
            {
                "kind": "commits",
                "repository": repo_c,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-c/commits",
            },
            {
                "kind": "regressions",
                "repository": repo_b,
                "sha": SHA_B,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-b/actions",
            },
            {
                "kind": "gold_set",
                "repository": repo_b,
                "sha": SHA_B,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-b/issues",
            },
            {
                "kind": "context_graph",
                "repository": repo_a,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-a/network",
            },
            {
                "kind": "regressions",
                "repository": repo_c,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-c/actions",
            },
            {
                "kind": "gold_set",
                "repository": repo_c,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-c/issues",
            },
            {
                "kind": "context_graph",
                "repository": repo_b,
                "sha": SHA_B,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-b",
            },
            {
                "kind": "context_graph",
                "repository": repo_c,
                "sha": SHA_A,
                "observed_at": "2026-11-23T11:00:00Z",
                "coverage": source_coverage,
                "url": "https://github.com/timerloggedout-spec/parser-c",
            },
        ],
        "cases": [
            {
                "case_id": "case-001",
                "task_family": "regression_context",
                "query": "find parser regression branch",
                "gold_target_ids": [target_a],
                "candidates": [
                    {
                        "target_id": target_a,
                        "repository": repo_a,
                        "branch": "feature/parser-regression",
                        "sha": SHA_A,
                        "evidence_status": "verified",
                        "disposition": "diverged",
                        "ahead_of_default": 3,
                        "behind_default": 2,
                        "unique_commit_count": 1,
                        "pr_state": "open",
                        "regression_verdict": "regressed",
                        "title": "parser regression branch",
                        "commit_subjects": ["fix parser regression"],
                        "commit_shas": [SHA_A],
                        "pull_request_numbers": [12],
                        "issue_numbers": [13],
                        "regression_reason": None,
                        "graph_edges": [
                            {
                                "relationship": "CROSS_REFERENCES",
                                "confidence": "verified",
                                "evidence_ref": "https://github.com/timerloggedout-spec/parser-a/issues/12",
                            }
                        ],
                        "evidence_refs": [
                            "https://github.com/timerloggedout-spec/parser-a/tree/feature/parser-regression"
                        ],
                    },
                    {
                        "target_id": target_b,
                        "repository": repo_b,
                        "branch": "feature/parser-regression",
                        "sha": SHA_B,
                        "evidence_status": "verified",
                        "disposition": "behind-only",
                        "ahead_of_default": 0,
                        "behind_default": 5,
                        "unique_commit_count": 0,
                        "pr_state": "none",
                        "regression_verdict": "green",
                        "title": "documentation update",
                        "commit_subjects": ["update docs"],
                        "commit_shas": [],
                        "pull_request_numbers": [],
                        "issue_numbers": [],
                        "regression_reason": None,
                        "graph_edges": [],
                        "evidence_refs": [
                            "https://github.com/timerloggedout-spec/parser-b/tree/feature/parser-regression"
                        ],
                    },
                    {
                        "target_id": target_c,
                        "repository": repo_c,
                        "branch": "candidate/parser-regression",
                        "sha": SHA_A,
                        "evidence_status": "candidate",
                        "disposition": "ahead-only",
                        "ahead_of_default": 2,
                        "behind_default": 0,
                        "unique_commit_count": 1,
                        "pr_state": "open",
                        "regression_verdict": "untestable",
                        "title": "parser regression candidate",
                        "commit_subjects": ["parser regression experiment"],
                        "commit_shas": [SHA_A],
                        "pull_request_numbers": [8],
                        "issue_numbers": [8],
                        "regression_reason": "baseline check absent at branch tip",
                        "graph_edges": [
                            {
                                "relationship": "MENTIONS",
                                "confidence": "candidate",
                                "evidence_ref": "https://github.com/timerloggedout-spec/parser-c/issues/8",
                            }
                        ],
                        "evidence_refs": [
                            "https://github.com/timerloggedout-spec/parser-c/tree/candidate/parser-regression"
                        ],
                    },
                ],
            }
        ],
    }


class TestBRRCrossRepositoryDoE(unittest.TestCase):
    def test_repository_qualified_identity_distinguishes_same_branch_names(self):
        a = evaluator.target_identity("timerloggedout-spec/a", "feature/x", SHA_A)
        b = evaluator.target_identity("timerloggedout-spec/b", "feature/x", SHA_A)
        self.assertNotEqual(a, b)
        self.assertEqual(a, f"timerloggedout-spec/a::feature/x@{SHA_A}")

    def test_fused_ranking_prefers_verified_relevant_target_and_excludes_candidate(self):
        result = evaluator.evaluate_dataset(make_dataset())
        case = next(row for row in result["cases"] if row["arm"] == "fused")
        self.assertEqual(case["ranked_target_ids"][0], target_id(
            "timerloggedout-spec/parser-a", "feature/parser-regression", SHA_A
        ))
        self.assertNotIn(
            target_id("timerloggedout-spec/parser-c", "candidate/parser-regression", SHA_A),
            case["ranked_target_ids"],
        )
        self.assertEqual(len(case["candidate_only_ids"]), 1)
        self.assertAlmostEqual(case["metrics"]["f1_at_5"], 1.0 / 3.0)

    def test_candidate_graph_edges_do_not_score_as_verified_context(self):
        dataset = make_dataset()
        candidate = dataset["cases"][0]["candidates"][2]
        self.assertEqual(evaluator.score_candidate(candidate, "parser regression", "context_graph"), 0.0)
        self.assertEqual(evaluator.score_candidate(candidate, "parser regression", "fused"), 0.0)

    def test_verified_target_candidate_edges_remain_outside_graph_score(self):
        dataset = make_dataset()
        candidate = dataset["cases"][0]["candidates"][0]
        candidate["graph_edges"] = [
            {
                "relationship": "SIMILAR_TO",
                "confidence": "candidate",
                "evidence_ref": "https://github.com/timerloggedout-spec/parser-a/issues/13",
            }
        ]
        self.assertEqual(evaluator.score_candidate(candidate, "parser regression", "context_graph"), 0.0)
        dataset["cases"][0]["candidates"][0]["graph_edges"] = [
            {
                "relationship": "SIMILAR_TO",
                "confidence": "candidate",
                "evidence_ref": "https://github.com/timerloggedout-spec/parser-a/issues/13",
            }
        ]
        result = evaluator.evaluate_dataset(dataset)
        row = next(item for item in result["cases"] if item["arm"] == "context_graph")
        self.assertIn(dataset["cases"][0]["candidates"][0]["target_id"], row["candidate_edge_ids"])
        self.assertIn("https://github.com/timerloggedout-spec/parser-a/issues/13", row["evidence_refs"])

    def test_evaluation_is_deterministic_for_a_frozen_dataset(self):
        dataset = make_dataset()
        first = evaluator.evaluate_dataset(dataset)
        second = evaluator.evaluate_dataset(dataset)
        self.assertEqual(first, second)
        for case_id in {row["case_id"] for row in first["cases"]}:
            rows = [row for row in first["cases"] if row["case_id"] == case_id]
            self.assertEqual([row["arm"] for row in rows], rows[0]["assignment_order"])

    def test_ranked_scores_preserve_component_breakdown(self):
        result = evaluator.evaluate_dataset(make_dataset())
        row = next(item for item in result["cases"] if item["arm"] == "fused")
        self.assertEqual(row["ranked_scores"][0]["target_id"], row["ranked_target_ids"][0])
        self.assertEqual(
            set(row["ranked_scores"][0]["components"]),
            {"lexical", "branch_commit", "context_graph", "regression"},
        )
        self.assertEqual(len(result["dataset_sha256"]), 64)

    def test_immutable_artifacts_allow_identical_replay_and_reject_replacement(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "dataset.json"
            evaluator.write_immutable_json(path, {"snapshot": "same"})
            evaluator.write_immutable_json(path, {"snapshot": "same"})
            with self.assertRaises(ValueError):
                evaluator.write_immutable_json(path, {"snapshot": "changed"})

    def test_experiment_records_retain_source_and_target_evidence(self):
        dataset = make_dataset()
        result = evaluator.evaluate_dataset(dataset)
        records = evaluator.build_experiment_records(
            result, dataset["baseline_sha"], dataset["candidate_sha"], dataset["observed_at"]
        )
        self.assertEqual(len(records), 4)
        self.assertIn(result["dataset_sha256"][:12], records[0]["experiment_id"])
        required = {
            "schema_version", "experiment_id", "observed_at", "baseline_sha",
            "candidate_sha", "suite", "treatment", "status", "outcome",
            "metrics", "provenance", "confidence", "evidence_refs",
        }
        schema_path = Path(__file__).resolve().parents[1] / "docs/ops/corpus/EXPERIMENT.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        for record in records:
            jsonschema.validate(record, schema)
            self.assertEqual(set(record), required)
            self.assertTrue(any("feature/parser-regression" in ref for ref in record["evidence_refs"]))
            self.assertEqual(record["status"], "observed")

    def test_partial_source_coverage_blocks_experiment_records(self):
        dataset = make_dataset("PARTIAL")
        result = evaluator.evaluate_dataset(dataset)
        records = evaluator.build_experiment_records(
            result, dataset["baseline_sha"], dataset["candidate_sha"], dataset["observed_at"]
        )
        self.assertTrue(records)
        self.assertTrue(all(record["status"] == "blocked" for record in records))
        self.assertTrue(all(record["outcome"] == "partial_coverage" for record in records))

    def test_untestable_regression_is_explicit_and_scores_below_regressed(self):
        untestable = {
            "disposition": "identical",
            "ahead_of_default": 0,
            "unique_commit_count": 0,
            "pr_state": "none",
            "regression_verdict": "untestable",
            "graph_edges": [],
            "evidence_status": "verified",
            "repository": "timerloggedout-spec/a",
            "branch": "main",
            "sha": SHA_A,
            "target_id": target_id("timerloggedout-spec/a", "main", SHA_A),
            "title": "",
            "commit_subjects": [],
            "commit_shas": [],
            "pull_request_numbers": [],
            "issue_numbers": [],
            "regression_reason": "missing test evidence",
            "behind_default": 0,
            "evidence_refs": ["https://github.com/timerloggedout-spec/a"],
        }
        regressed = dict(untestable, regression_verdict="regressed")
        self.assertEqual(evaluator.regression_signal(untestable), 0.5)
        self.assertEqual(evaluator.regression_signal(regressed), 1.0)
        self.assertEqual(evaluator.regression_signal(dict(untestable, regression_verdict="green")), 0.0)

    def test_every_covered_repository_requires_brr_and_commit_receipts(self):
        dataset = make_dataset()
        dataset["sources"] = [
            source for source in dataset["sources"]
            if not (source["repository"] == "timerloggedout-spec/parser-c"
                    and source["kind"] == "commits")
        ]
        with self.assertRaises(ValueError):
            evaluator.validate_dataset(dataset)

    def test_gold_set_requires_human_adjudication_receipt(self):
        dataset = make_dataset()
        source = next(
            item for item in dataset["sources"]
            if item["kind"] == "gold_set" and item["repository"] == "timerloggedout-spec/parser-b"
        )
        source.pop("adjudication_status")
        with self.assertRaises(ValueError):
            evaluator.validate_dataset(dataset)

    def test_case_id_is_safe_for_record_output_paths(self):
        dataset = make_dataset()
        dataset["cases"][0]["case_id"] = "../escape"
        with self.assertRaises(ValueError):
            evaluator.validate_dataset(dataset)

    def test_invalid_identity_and_missing_evidence_fail_closed(self):
        dataset = make_dataset()
        dataset["cases"][0]["candidates"][0]["target_id"] = "same-name-branch"
        with self.assertRaises(ValueError):
            evaluator.validate_dataset(dataset)
        dataset = make_dataset()
        dataset["cases"][0]["candidates"][0]["evidence_refs"] = []
        with self.assertRaises(ValueError):
            evaluator.validate_dataset(dataset)


if __name__ == "__main__":
    unittest.main()
