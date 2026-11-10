import unittest
from pathlib import Path
from scripts.ci.siglary_validator import validate_file_content, run_census


class SiglaryValidatorTests(unittest.TestCase):
    def test_detects_forbidden_data_values(self):
        path = Path("data/sample.json")
        content = '{"status": "NOT_ESTABLISHED", "metric": "N∅"}'
        errors = validate_file_content(path, content)
        self.assertTrue(any("hard violation" in e and "NOT_ESTABLISHED" in e for e in errors))
        self.assertTrue(any("hard violation" in e and "N∅" in e for e in errors))

    def test_accepts_clean_data_file(self):
        path = Path("data/sample.json")
        content = '{"status": "confirmed", "metric": 42}'
        errors = validate_file_content(path, content)
        self.assertEqual(errors, [])

    def test_detects_class_conflation(self):
        path = Path("skills/sample/SKILL.md")
        content = 'An operator is a glyph in this notation system.'
        errors = validate_file_content(path, content)
        self.assertTrue(any("class violation" in e for e in errors))

    def test_accepts_clean_skill_file(self):
        path = Path("skills/sample/SKILL.md")
        content = '# Siglary Skill\nClasses kept distinct: glyphs, chords, operators.'
        errors = validate_file_content(path, content)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
