import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.ci.evaluate_skills import changed_skill_paths, evaluate_inventory, evaluate_package, evaluate_text

GOOD = '''---
name: example-skill
description: "Evaluate an example skill safely."
---

# Example Skill

## Operating workflow

1. Inspect the target.
2. Validate the result.
3. Record evidence and close out.

## Safety

Never expose credentials or mutate external systems without authorization.

## References

Keep related documentation current.
'''


class SkillEvaluationTests(unittest.TestCase):
    def test_valid_skill_scores_and_passes(self):
        result = evaluate_text(GOOD, ".agents/skills/example/SKILL.md", "SKILL.md")
        self.assertTrue(result["valid"])
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["dimensions"]["verification_evidence"], 5)

    def test_missing_frontmatter_is_hard_failure(self):
        result = evaluate_text("# no frontmatter\n", "SKILL.md", "SKILL.md")
        self.assertFalse(result["valid"])
        self.assertIn("frontmatter", result["hard_failures"])

    def test_secret_pattern_is_hard_failure(self):
        result = evaluate_text(GOOD + "\napi_key='sk-abcdefghijklmnopqrstuvwxyz'\n", "SKILL.md", "SKILL.md")
        self.assertFalse(result["valid"])
        self.assertIn("secret_pattern", result["hard_failures"])

    def test_skill_archive_requires_one_skill_file_and_safe_paths(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "example.skill"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("SKILL.md", GOOD)
            result = evaluate_package(path)
            self.assertTrue(result["valid"])

    def test_skill_archive_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "unsafe.skill"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("../SKILL.md", GOOD)
            result = evaluate_package(path)
            self.assertFalse(result["valid"])
            self.assertIn("archive_path", result["hard_failures"])

    def test_changed_skill_paths_are_narrowly_gated(self):
        fake = type("Completed", (), {"stdout": ".agents/skills/new/SKILL.md\nREADME.md\nfixture.skill\n"})()
        with patch("scripts.ci.evaluate_skills.subprocess.run", return_value=fake) as run:
            paths = changed_skill_paths("base", "head", Path("."))
        self.assertEqual(paths, {".agents/skills/new/SKILL.md", "fixture.skill"})
        run.assert_called_once()



    def test_docs_ops_session_mirror_without_frontmatter_is_not_a_definition(self):
        result = evaluate_inventory("# session note\n", "docs/ops/skills/adaptive-wait/SKILL.md")
        self.assertTrue(result["valid"])
        self.assertEqual(result["source_kind"], "session_mirror")
        self.assertEqual(result["hard_failures"], [])
        canonical = evaluate_inventory("# no frontmatter\n", ".agents/skills/adaptive-wait/SKILL.md")
        self.assertFalse(canonical["valid"])
        self.assertIn("frontmatter", canonical["hard_failures"])


if __name__ == "__main__":
    unittest.main()