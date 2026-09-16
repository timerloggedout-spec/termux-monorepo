#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from repository_observatory import build_records, build_payload, classify, snapshot_hash


BASE = {
    "full_name": "example/research-agent",
    "name": "research-agent",
    "html_url": "https://github.com/example/research-agent",
    "default_branch": "main",
    "description": "Research agent and knowledge graph workflow",
    "owner": {"login": "example"},
    "visibility": "public",
    "private": False,
    "fork": False,
    "archived": False,
    "is_template": False,
    "language": "Python",
    "topics": ["research", "knowledge-graph", "agents"],
    "stargazers_count": 12,
    "forks_count": 3,
    "updated_at": "2026-09-15T00:00:00Z",
    "pushed_at": "2026-09-15T00:00:00Z",
    "created_at": "2026-01-01T00:00:00Z",
}


class ObservatoryTests(unittest.TestCase):
    def test_classification_is_deterministic(self):
        self.assertEqual(classify(BASE, ["starred"]), classify(BASE, ["starred"]))
        self.assertIn("research", classify(BASE, ["starred"])["domains"])
        self.assertIn("context", classify(BASE, ["starred"])["domains"])

    def test_owned_and_starred_provenance_is_merged(self):
        records = build_records([BASE], [dict(BASE)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["provenance"], ["owned", "starred"])

    def test_snapshot_hash_is_stable(self):
        records = build_records([], [BASE])
        self.assertEqual(snapshot_hash(records), snapshot_hash(json.loads(json.dumps(records))))

    def test_payload_counts(self):
        records = build_records([BASE], [])
        payload = build_payload("example", "example", records, "2026-09-15T00:00:00Z")
        self.assertEqual(payload["counts"]["owned"], 1)
        self.assertEqual(payload["counts"]["starred"], 0)
        self.assertEqual(payload["counts"]["both"], 0)
        self.assertEqual(len(payload["snapshot_hash"]), 64)

    def test_previous_snapshot_timestamp_can_be_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.json"
            path.write_text(json.dumps({"snapshot_hash": snapshot_hash(build_records([], [BASE])), "observed_at": "old"}))
            self.assertEqual(json.loads(path.read_text())["observed_at"], "old")


if __name__ == "__main__":
    unittest.main()
