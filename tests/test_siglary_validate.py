import os
import sys
import json
import subprocess
import tempfile
import unittest

# Add scripts/siglary to path to import validator functions if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts/siglary")))
import siglary_validate

class TestSiglaryValidate(unittest.TestCase):

    def test_load_issued_data(self):
        data = siglary_validate.load_issued_data()
        self.assertIn("issued_glyphs", data)
        self.assertIn("operators", data)
        self.assertIn("👁", data["issued_glyphs"])
        self.assertIn("∧", data["operators"])

    def test_check_claude_reference(self):
        # Missing reference
        v = siglary_validate.check_claude_reference("CLAUDE.md", "Some content without s-word")
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]["rule"], "claude_reference_missing")

        # Present reference
        v2 = siglary_validate.check_claude_reference("CLAUDE.md", "Refers to Siglary standard and SIGLARY-STANDARD.md")
        self.assertEqual(len(v2), 0)

    def test_check_n_null_in_data(self):
        # Data file with N∅
        v = siglary_validate.check_n_null_in_data("data.json", '{"status": "N∅"}')
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]["rule"], "n_null_in_data")

        # Data file without N∅
        v2 = siglary_validate.check_n_null_in_data("data.json", '{"status": "ACTIVE"}')
        self.assertEqual(len(v2), 0)

    def test_check_glyph_inflation(self):
        issued = {"👁"}
        operators = {"∧"}
        # Unissued emoji 🚀
        v = siglary_validate.check_glyph_inflation("skill.md", "Doing great 🚀", issued, operators)
        self.assertTrue(any("glyph_inflation_🚀" in item["rule"] for item in v))

        # Issued emoji 👁
        v2 = siglary_validate.check_glyph_inflation("skill.md", "Verified 👁", issued, operators)
        self.assertEqual(len(v2), 0)

    def test_check_class_misuse(self):
        v = siglary_validate.check_class_misuse("skill.md", "Use glyph ∧ for logic.")
        self.assertEqual(len(v), 1)
        self.assertEqual(v[0]["rule"], "operator_referred_to_as_glyph")

    def test_empty_census_inconclusive(self):
        # Test that running validator with 0 surfaces scanned exits non-zero
        # We can test by mocking find_surfaces to return []
        original_find = siglary_validate.find_surfaces
        siglary_validate.find_surfaces = lambda: []
        try:
            with self.assertRaises(SystemExit) as cm:
                siglary_validate.main()
            self.assertNotEqual(cm.exception.code, 0)
        finally:
            siglary_validate.find_surfaces = original_find

if __name__ == "__main__":
    unittest.main()
