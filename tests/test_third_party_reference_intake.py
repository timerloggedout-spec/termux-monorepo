from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci.verify_third_party_reference_intake import validate


class ThirdPartyReferenceIntakeTests(unittest.TestCase):
    def make_document(self, root: Path, status: str = "research_only") -> dict:
        source = root / "refTemplates/13_Third_Party_Refs/radar"
        source.mkdir(parents=True, exist_ok=True)
        (source / "README.md").write_text("source", encoding="utf-8")
        (source / "SOURCE.txt").write_text("https://example.org", encoding="utf-8")
        return {
            "schema": "third-party-ref-disposition/v1",
            "source_record": "refTemplates/13_Third_Party_Refs/radar",
            "canonical_smods_registry": "refTemplates/smods/INTEGRATIONS.json",
            "entries": [{
                "id": "sample",
                "upstream": "https://github.com/example/sample",
                "status": status,
                "fork_required": False,
                "live_gitlink": False,
            }],
        }

    def test_research_only_is_valid_without_global_smods_registry(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = self.make_document(root)
            self.assertEqual(validate(document, root, {}, set()), [])

    def test_research_only_cannot_claim_a_fork_or_gitlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = self.make_document(root)
            document["entries"][0]["fork_required"] = True
            errors = validate(document, root, {}, set())
            self.assertTrue(any("must explicitly keep fork_required=false" in e for e in errors))

    def test_fork_required_must_be_registered_but_not_pinned(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = self.make_document(root, "fork_required")
            entry = document["entries"][0]
            entry.update({
                "fork_required": True,
                "smods_path": "refTemplates/smods/sample_fork",
                "fork_url": "https://github.com/example/sample_fork.git",
                "pinned_sha": None,
            })
            registry = {"entries": [{
                "id": "sample",
                "path": entry["smods_path"],
                "fork_url": entry["fork_url"],
                "status": "fork_required",
            }]}
            self.assertEqual(validate(document, root, {}, set(), registry), [])

    def test_pinned_requires_registry_gitmodules_gitlink_and_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            document = self.make_document(root, "pinned")
            entry = document["entries"][0]
            path = "refTemplates/smods/sample_fork"
            url = "https://github.com/example/sample_fork.git"
            entry.update({
                "fork_required": True,
                "live_gitlink": True,
                "smods_path": path,
                "fork_url": url,
                "pinned_sha": "a" * 40,
            })
            registry = {"entries": [{
                "id": "sample", "path": path, "fork_url": url, "status": "pinned"
            }]}
            self.assertEqual(validate(document, root, {path: url}, {path}, registry), [])


if __name__ == "__main__":
    unittest.main()
