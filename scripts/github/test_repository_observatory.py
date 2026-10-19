#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from repository_observatory import (
    API,
    GitHubHttpError,
    RateLimitDeferred,
    build_records,
    build_payload,
    classify,
    page_budget,
    probe_rate_limit,
    resolve_login,
    snapshot_hash,
    main,
)


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
    def test_api_host_is_bound(self):
        # Run 36896271590 on 63635bd9 failed with NameError: name 'API' is not defined.
        self.assertEqual(API, "https://api.github.com")

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

    def test_actions_token_403_falls_back_to_declared_owner(self):
        def fetch(path, token, params=None):
            if path == "/user":
                raise GitHubHttpError(403, path)
            if path == "/users/timerloggedout-spec":
                return {"login": "timerloggedout-spec"}
            raise AssertionError(path)

        self.assertEqual(resolve_login(fetch, "ghs_test", "timerloggedout-spec"), "timerloggedout-spec")

    def test_user_mismatch_still_fails(self):
        def fetch(path, token, params=None):
            return {"login": "other"}

        with self.assertRaises(RuntimeError):
            resolve_login(fetch, "ghs_test", "timerloggedout-spec")

    def test_page_budget_applies_safety_and_reserve(self):
        # remaining 100, reserve 20, safety 0.8 -> floor(80*0.8)=64
        self.assertEqual(page_budget(100, 5000), 64)
        self.assertEqual(page_budget(10, 5000), 0)  # after reserve headroom 0
        self.assertLessEqual(page_budget(None, None), 20)

    def test_probe_rate_limit_reads_core(self):
        def fetch(path, token, params=None):
            self.assertEqual(path, "/rate_limit")
            return {"resources": {"core": {"remaining": 4000, "limit": 5000, "reset": 9999999999}}}

        rl = probe_rate_limit(fetch, "tok")
        self.assertEqual(rl["remaining"], 4000)
        self.assertEqual(rl["limit"], 5000)

    def test_main_defers_when_remaining_below_floor(self):
        def fetch(path, token, params=None):
            if path == "/rate_limit":
                return {"resources": {"core": {"remaining": 5, "limit": 5000, "reset": 1}}}
            raise AssertionError(path)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "index.json"
            md = Path(tmp) / "matrix.md"
            code = main(
                ["--owner", "timerloggedout-spec", "--output", str(out), "--markdown", str(md)],
                fetch=fetch,
            )
            self.assertEqual(code, 0)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
