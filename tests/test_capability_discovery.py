from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.capabilities.discover import connect, import_session_json, load_taxonomy, scan_repository, search, search_skills_sh, upsert, validate_classification


class CapabilityDiscoveryTests(unittest.TestCase):
    def test_classifier_output_is_constrained_by_versioned_taxonomy(self):
        taxonomy = load_taxonomy()
        self.assertEqual(validate_classification("testing", "testing", taxonomy), ("testing", "testing"))
        self.assertEqual(
            validate_classification("unknown-domain", "unknown-function", taxonomy),
            ("agentic", "capability-discovery"),
        )

    def test_nested_vendor_skill_is_classified_as_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "workspace" / "vendor" / "mailer" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                "---\nname: mailer-skill\ndescription: Send transactional email with bounded API operations\n---\n"
                "# Procedure\nVerify permissions and evidence.\n",
                encoding="utf-8",
            )
            rows = scan_repository(root)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["trust"], "unverified")
            self.assertEqual(rows[0]["source_id"], "repo-vendor-skills")
            self.assertNotIn("Procedure", rows[0]["description"])

    def test_index_upsert_is_idempotent_and_searchable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / ".agents" / "skills" / "demo" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                "---\nname: demo\ndescription: Testing workflow\n---\n# Workflow\nVerify evidence.\n",
                encoding="utf-8",
            )
            rows = scan_repository(root)
            con = connect(root / "index.sqlite")
            first = upsert(con, rows)
            second = upsert(con, rows)
            self.assertEqual(first["changed"], 1)
            self.assertEqual(second["changed"], 0)
            self.assertEqual(con.execute("SELECT count(*) FROM discovery_event").fetchone()[0], 1)
            self.assertEqual(len(search(con, "testing workflow")), 1)

    def test_identical_content_creates_relationship_without_merging_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body = "---\nname: shared\ndescription: Shared workflow\n---\n# Workflow\nVerify evidence.\n"
            paths = [
                root / ".agents" / "skills" / "shared" / "SKILL.md",
                root / "vendor" / "sample" / "SKILL.md",
            ]
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
            con = connect(root / "index.sqlite")
            result = upsert(con, scan_repository(root))
            self.assertEqual(result["total"], 2)
            self.assertEqual(result["relationships"], 1)
            edge = con.execute("SELECT relation FROM capability_edge").fetchone()
            self.assertEqual(edge[0], "content_identical")

    def test_skills_sh_search_requires_token_and_returns_metadata_only(self):
        with patch.dict("os.environ", {}, clear=True):
            rows, status = search_skills_sh("database skills")
            self.assertEqual(rows, [])
            self.assertEqual(status, "auth_required")

        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"data": [{
                    "id": "vendor/repo/database",
                    "name": "Database Skill",
                    "source": "vendor/repo",
                    "installs": 123,
                    "isDuplicate": False,
                    "hash": "abc123",
                    "url": "https://skills.sh/vendor/repo/database",
                }]}).encode()

        with patch.dict("os.environ", {"VERCEL_OIDC_TOKEN": "test-token"}):
            with patch("urllib.request.urlopen", return_value=Response()):
                rows, status = search_skills_sh("database skills", 5)
        self.assertEqual(status, "ok")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["trust"], "community-reference")
        self.assertEqual(rows[0]["lifecycle"], "discovered")
        self.assertNotIn("SKILL.md contents", rows[0]["description"])

    def test_session_catalog_import_preserves_session_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "skills.json"
            path.write_text(json.dumps({
                "snapshot": {"captured_at": "2026-11-19"},
                "plugin_skills": [{
                    "uri": "skills://plugins/demo/index/skill.md",
                    "activation_description": "Build agent workflows",
                }],
            }), encoding="utf-8")
            rows = import_session_json(path, "plugin-skill")
            self.assertEqual(rows[0]["trust"], "session-observed")
            self.assertEqual(rows[0]["version_ref"], "2026-11-19")
            self.assertEqual(rows[0]["kind"], "plugin-skill")


if __name__ == "__main__":
    unittest.main()
