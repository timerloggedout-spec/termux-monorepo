import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "ci"))
from validate_context_relationship_backfill import ValidationError, validate_backfill
from archwiz.context_relationships.temporal import content_hash, snapshot_id


class ContextBackfillValidationTests(unittest.TestCase):
    def _fixture(self, root: Path):
        nodes = [
            {"id": "node:a", "kind": "issue", "external_id": "1", "attributes": {}},
            {"id": "node:b", "kind": "issue", "external_id": "2", "attributes": {}},
        ]
        edges = [{
            "id": "edge:a-b", "source": "node:a", "target": "node:b",
            "type": "REFERENCES", "classification": "verified",
            "observed_at": "2026-10-22T00:00:00Z",
            "evidence": [{"kind": "github_api", "source": "https://example.test/1", "collector": "test"}],
            "attributes": {},
        }]
        observed = "2026-10-22T00:00:00Z"
        nodes_hash, edges_hash = content_hash(nodes), content_hash(edges)
        sid = snapshot_id("owner/repo", "master", "a" * 40, observed, 1, 2, nodes_hash, edges_hash)
        temporal = {
            "schema": "context-relationship-temporal/v1",
            "snapshot_id": sid,
            "repository": "owner/repo",
            "source_ref": "master",
            "source_sha": "a" * 40,
            "observed_at": observed,
            "history_window": {"start_page": 1, "next_start_page": 2},
            "coverage": "PARTIAL_CONTINUATION_REQUIRED",
            "node_count": 2, "edge_count": 1,
            "verified_edge_count": 1, "candidate_edge_count": 0,
            "nodes_hash": nodes_hash, "edges_hash": edges_hash,
        }
        manifest = {
            "schema_version": "1.0", "repository": "owner/repo", "default_branch": "master",
            "input_sha256": "b" * 64, "schema_sha256": "c" * 64,
            "scope_registry_sha256": "d" * 64, "latest_observed_at": observed,
            "node_count": 2, "edge_count": 1, "verified_edge_count": 1,
            "candidate_edge_count": 0,
            "history_window": {"start_page": 1, "next_start_page": 2},
            "history_coverage": {
                "schema_version": "1.0", "status": "PARTIAL_CONTINUATION_REQUIRED",
                "next_start_page": 2,
                "windows": [{
                    "start_page": 1, "next_start_page": 2, "limit_per_family": 100,
                    "issue_count": 100, "pull_request_count": 100,
                    "issues_complete": False, "pull_requests_complete": False,
                    "source_sha": "a" * 40, "observed_at": observed,
                }],
            },
        }
        (root / "nodes.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in nodes), encoding="utf-8")
        (root / "edges.jsonl").write_text("".join(json.dumps(x, sort_keys=True) + "\n" for x in edges), encoding="utf-8")
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (root / "temporal-current.json").write_text(json.dumps(temporal), encoding="utf-8")

    def test_valid_partial_window_returns_provenance_receipt(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            receipt = validate_backfill(root, "owner/repo", "master", "a" * 40)
            self.assertEqual(receipt["validation_status"], "VALIDATED")
            self.assertEqual(receipt["history_window"], {"start_page": 1, "next_start_page": 2})
            self.assertEqual(receipt["coverage"], "PARTIAL_CONTINUATION_REQUIRED")
            self.assertEqual(receipt["counts"]["node_count"], 2)
            self.assertFalse(receipt["corpus_promoted"])
            self.assertEqual(receipt["history_coverage"]["next_start_page"], 2)

    def test_detects_tampered_edges_hash(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            with (root / "edges.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"id": "edge:bad", "source": "node:missing", "target": "node:b", "classification": "verified"}) + "\n")
            with self.assertRaisesRegex(ValidationError, "missing source or target"):
                validate_backfill(root, "owner/repo", "master", "a" * 40)

    def test_rejects_coverage_that_hides_continuation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            temporal = json.loads((root / "temporal-current.json").read_text(encoding="utf-8"))
            temporal["coverage"] = "COMPLETE"
            (root / "temporal-current.json").write_text(json.dumps(temporal), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "temporal coverage differs"):
                validate_backfill(root, "owner/repo", "master", "a" * 40)

    def test_rejects_self_consistent_stale_source_sha_for_same_repo_and_ref(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            temporal = json.loads((root / "temporal-current.json").read_text(encoding="utf-8"))
            temporal["source_sha"] = "e" * 40
            temporal["snapshot_id"] = snapshot_id(
                "owner/repo",
                "master",
                temporal["source_sha"],
                temporal["observed_at"],
                4,
                5,
                temporal["nodes_hash"],
                temporal["edges_hash"],
            )
            (root / "temporal-current.json").write_text(json.dumps(temporal), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "independently captured expected source SHA"):
                validate_backfill(root, "owner/repo", "master", "a" * 40)

    def test_unproven_page_thirteen_cannot_claim_complete_history(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            temporal = json.loads((root / "temporal-current.json").read_text(encoding="utf-8"))
            manifest["history_window"] = {"start_page": 13, "next_start_page": None}
            manifest["history_coverage"] = {
                "schema_version": "1.0", "status": "COMPLETE", "next_start_page": None,
                "windows": [{
                    "start_page": 13, "next_start_page": None, "limit_per_family": 100,
                    "issue_count": 0, "pull_request_count": 0,
                    "issues_complete": True, "pull_requests_complete": True,
                    "source_sha": "a" * 40, "observed_at": temporal["observed_at"],
                }],
            }
            temporal["history_window"] = {"start_page": 13, "next_start_page": None}
            temporal["coverage"] = "COMPLETE"
            temporal["snapshot_id"] = snapshot_id(
                "owner/repo", "master", "a" * 40, temporal["observed_at"], 13, None,
                temporal["nodes_hash"], temporal["edges_hash"],
            )
            (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "temporal-current.json").write_text(json.dumps(temporal), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "starting at page one"):
                validate_backfill(root, "owner/repo", "master", "a" * 40)

    def test_rejects_stale_or_wrong_ref(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            with self.assertRaisesRegex(ValidationError, "source ref"):
                validate_backfill(root, "owner/repo", "master-staging", "a" * 40)


if __name__ == "__main__":
    unittest.main()
