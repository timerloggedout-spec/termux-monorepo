from __future__ import annotations

import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from scripts.capabilities.discover import cached_skills_sh_search, connect, import_session_json, load_taxonomy, scan_repository, search, search_skills_sh, upsert, validate_classification


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

    def test_explicit_workspace_root_is_unverified_and_symlink_free(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "workspace"
            path = root / "project" / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(
                "---\nname: external-skill\ndescription: External workspace capability\n---\n# Workflow\n",
                encoding="utf-8",
            )
            rows = scan_repository(root, external=True)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["source_id"], "workspace-external")
            self.assertEqual(rows[0]["trust"], "unverified")
            self.assertTrue(rows[0]["locator"].startswith("external:workspace/"))

    def test_plugin_and_mcp_manifests_index_metadata_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugins" / "demo" / ".codex-plugin" / "plugin.json"
            plugin.parent.mkdir(parents=True)
            plugin.write_text(json.dumps({
                "name": "demo-plugin",
                "description": "Database helper plugin",
                "version": "1.2.0",
                "skills": ["skills/db/SKILL.md"],
                "mcpServers": {"db": {"command": "db-server"}},
            }), encoding="utf-8")
            tools_file = root / "plugins" / "demo" / "tools.json"
            tools_file.write_text(json.dumps([{"name": "query-db", "description": "Query database"}]), encoding="utf-8")
            vendor_manifest = root / "vendor" / "external-plugin" / "plugin.json"
            vendor_manifest.parent.mkdir(parents=True)
            vendor_manifest.write_text(json.dumps({"name": "external-plugin"}), encoding="utf-8")
            secret_value = "supersecretvalue123"
            secret_manifest = root / "plugins" / "private" / "plugin.json"
            secret_manifest.parent.mkdir(parents=True)
            secret_manifest.write_text(json.dumps({
                "name": "private-plugin",
                "description": "Private integration",
                "api_key": secret_value,
            }), encoding="utf-8")
            rows = scan_repository(root)
            self.assertEqual(len(rows), 4)
            plugin_row = next(row for row in rows if row["locator"].endswith("plugin.json") and row["trust"] == "repository-canonical")
            tools_row = next(row for row in rows if row["locator"].endswith("tools.json"))
            vendor_row = next(row for row in rows if "vendor/" in row["locator"])
            secret_row = next(row for row in rows if row["name"] == "private-plugin")
            self.assertEqual(plugin_row["kind"], "manifest")
            self.assertEqual(plugin_row["source_id"], "repo-plugin-manifests")
            self.assertIn("MCP servers=1", plugin_row["description"])
            self.assertNotIn("db-server", plugin_row["description"])
            self.assertEqual(plugin_row["version_ref"], "1.2.0")
            self.assertEqual(tools_row["kind"], "manifest")
            self.assertIn("tool entries=1", tools_row["description"])
            self.assertEqual(vendor_row["trust"], "unverified")
            self.assertEqual(secret_row["trust"], "quarantined")
            self.assertNotIn(secret_value, json.dumps(secret_row))

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
            changed_taxonomy = {**rows[0], "taxonomy_sha256": "a" * 64}
            reclassified = upsert(con, [changed_taxonomy])
            self.assertEqual(reclassified["changed"], 1)
            event = con.execute("SELECT event FROM discovery_event ORDER BY recorded_at DESC LIMIT 1").fetchone()
            self.assertEqual(event[0], "reclassified")

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

    def test_skills_sh_search_uses_sqlite_cache(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return json.dumps({"data": [{
                    "id": "vendor/repo/search",
                    "name": "Search Skill",
                    "source": "vendor/repo",
                    "installs": 12,
                    "url": "https://skills.sh/vendor/repo/search",
                }], "searchType": "fuzzy"}).encode()

        with tempfile.TemporaryDirectory() as tmp:
            con = connect(Path(tmp) / "index.sqlite")
            with patch.dict("os.environ", {"VERCEL_OIDC_TOKEN": "test-token"}):
                with patch("urllib.request.urlopen", return_value=Response()) as request:
                    first, first_status = cached_skills_sh_search(con, "search skill")
                    second, second_status = cached_skills_sh_search(con, "search skill")
        self.assertEqual(first_status, "ok")
        self.assertEqual(second_status, "cached")
        self.assertEqual(first, second)
        request.assert_called_once()

    def test_skills_sh_curated_catalog_flattens_publishers_and_filters_query(self):
        with patch.dict("os.environ", {"VERCEL_OIDC_TOKEN": "test-token"}):
            class Response:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    return False
                def read(self):
                    return json.dumps({"data": [{
                        "owner": "microsoft",
                        "skills": [{
                            "id": "microsoft/skills/azure-sdk",
                            "name": "Azure SDK",
                            "source": "microsoft/skills",
                            "installs": 77,
                            "url": "https://skills.sh/microsoft/skills/azure-sdk",
                        }],
                    }]}).encode()
            with patch("urllib.request.urlopen", return_value=Response()):
                rows, status = search_skills_sh("azure sdk", curated=True)
        self.assertEqual(status, "ok")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "skills-sh:microsoft/skills/azure-sdk")
        self.assertIn("searchType=curated", rows[0]["description"])

    def test_skills_sh_rejects_short_query_before_network(self):
        with patch.dict("os.environ", {"VERCEL_OIDC_TOKEN": "test-token"}):
            with patch("urllib.request.urlopen") as request:
                rows, status = search_skills_sh("x")
        self.assertEqual(rows, [])
        self.assertEqual(status, "query_too_short")
        request.assert_not_called()

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
