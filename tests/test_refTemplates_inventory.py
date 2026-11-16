from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.ci.refTemplates_inventory import validate, validate_smods_contract


class RefTemplatesEnforcementTests(unittest.TestCase):
    def test_all_template_categories_require_readme_and_source(self):
        entries = [{
            "slot": "06_Task_Tracking",
            "template_children": [{
                "name": "que-superagent",
                "path": "refTemplates/06_Task_Tracking/que-superagent",
                "is_symlink": False,
                "has_readme": True,
                "readme_nonempty": True,
                "has_source": False,
                "source_nonempty": False,
            }],
        }]
        errors = validate(entries)
        self.assertIn(
            "refTemplates/06_Task_Tracking/que-superagent: missing or empty regular SOURCE.txt",
            errors,
        )

    def test_runtime_templates_require_integration_manifest(self):
        entries = [{
            "slot": "01_Agent_Runtime",
            "template_children": [{
                "name": "sample",
                "path": "refTemplates/01_Agent_Runtime/sample",
                "is_symlink": False,
                "has_readme": True,
                "readme_nonempty": True,
                "has_source": True,
                "source_nonempty": True,
                "has_integration_manifest": False,
                "integration_manifest_valid": False,
            }],
        }]
        self.assertIn(
            "refTemplates/01_Agent_Runtime/sample: runtime integration template requires integration.json",
            validate(entries),
        )

    def test_runtime_integration_manifest_must_be_valid_json_object(self):
        entries = [{
            "slot": "01_Agent_Runtime",
            "template_children": [{
                "name": "sample",
                "path": "refTemplates/01_Agent_Runtime/sample",
                "is_symlink": False,
                "has_readme": True,
                "readme_nonempty": True,
                "has_source": True,
                "source_nonempty": True,
                "has_integration_manifest": True,
                "integration_manifest_valid": False,
            }],
        }]
        self.assertIn(
            "refTemplates/01_Agent_Runtime/sample: integration.json must be valid JSON with an object root",
            validate(entries),
        )

    def test_symlinked_template_directory_fails_closed(self):
        entries = [{
            "slot": "15_Research_Repo_Templates",
            "template_children": [{
                "name": "external",
                "path": "refTemplates/15_Research_Repo_Templates/external",
                "is_symlink": True,
            }],
        }]
        self.assertIn(
            "refTemplates/15_Research_Repo_Templates/external: template directory must not be a symlink",
            validate(entries),
        )

    def test_smods_pin_requires_matching_gitlink(self):
        modules = [{
            "path": "refTemplates/smods/example_fork",
            "url": "https://github.com/timerloggedout-spec/example_fork.git",
            "shallow": True,
        }]
        self.assertIn(
            "refTemplates/smods/example_fork: .gitmodules entry has no 160000 gitlink",
            validate_smods_contract(modules, {}),
        )

    def test_smods_gitlink_requires_module_entry(self):
        errors = validate_smods_contract([], {
            "refTemplates/smods/orphan_fork": "a" * 40,
        })
        self.assertIn(
            "refTemplates/smods/orphan_fork: 160000 gitlink has no .gitmodules entry",
            errors,
        )

    def test_smods_require_shallow_and_immutable_sha(self):
        modules = [{
            "path": "refTemplates/smods/example_fork",
            "url": "https://github.com/timerloggedout-spec/example_fork.git",
            "shallow": False,
        }]
        errors = validate_smods_contract(modules, {
            "refTemplates/smods/example_fork": "not-a-commit",
        })
        self.assertTrue(any("shallow = true" in error for error in errors))
        self.assertTrue(any("40-character lowercase commit SHA" in error for error in errors))

    def test_smods_reject_non_https_or_credentialed_urls(self):
        modules = [{
            "path": "refTemplates/smods/example_fork",
            "url": "https://user:token@github.com/example/fork.git",
            "shallow": True,
        }]
        errors = validate_smods_contract(modules, {
            "refTemplates/smods/example_fork": "b" * 40,
        })
        self.assertTrue(any("credential-free HTTPS GitHub URL" in error for error in errors))

    def test_smods_reject_duplicate_paths(self):
        entry = {
            "path": "refTemplates/smods/example_fork",
            "url": "https://github.com/timerloggedout-spec/example_fork.git",
            "shallow": True,
        }
        errors = validate_smods_contract([entry, dict(entry)], {
            "refTemplates/smods/example_fork": "c" * 40,
        })
        self.assertTrue(any("duplicate sMods path" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
