from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.capabilities.discover import connect, import_session_json, scan_repository, search, upsert


class CapabilityDiscoveryTests(unittest.TestCase):
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
