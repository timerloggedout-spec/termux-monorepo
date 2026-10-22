"""Contract tests for the native AGY pilot agents and handoff skill."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / ".agents" / "agents"
SKILL = ROOT / ".agents" / "skills" / "agy-native-pilot" / "SKILL.md"


class AgyNativeContractTests(unittest.TestCase):
    def read_manifest(self, name):
        text = (AGENTS / f"agy-{name}.md").read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
        self.assertIsNotNone(match, f"agy-{name}.md must have YAML frontmatter")
        frontmatter, body = match.groups()
        return frontmatter, body

    def test_implementer_native_contract_and_boundaries(self):
        fm, body = self.read_manifest("implementer")
        self.assertRegex(fm, r"(?m)^name: agy-implementer$")
        self.assertRegex(fm, r"(?m)^description: .+")
        self.assertIn("  - view_file", fm)
        self.assertIn("  - replace_file_content", fm)
        self.assertIn("  - run_command", fm)
        self.assertRegex(fm, r"(?m)^mainAgent: true$")
        self.assertRegex(fm, r"(?m)^subagent: true$")
        self.assertRegex(fm, r"(?m)^model: inherit$")
        for prohibited in ("Origin", "global settings", "credentials", "publish", "push", "commit", "background", "network"):
            self.assertIn(prohibited, body)
        self.assertIn("not a permission sandbox", body)

    def test_verifier_native_contract_and_boundaries(self):
        fm, body = self.read_manifest("verifier")
        self.assertRegex(fm, r"(?m)^name: agy-verifier$")
        self.assertRegex(fm, r"(?m)^description: .+")
        self.assertIn("  - view_file", fm)
        self.assertIn("  - run_command", fm)
        self.assertNotIn("replace_file_content", fm)
        self.assertRegex(fm, r"(?m)^mainAgent: true$")
        self.assertRegex(fm, r"(?m)^subagent: true$")
        self.assertRegex(fm, r"(?m)^model: inherit$")
        for prohibited in ("Origin", "global settings", "credentials", "publish", "push", "commit", "background", "network"):
            self.assertIn(prohibited, body)
        self.assertIn("without editing files", body)
        self.assertIn("not a permission sandbox", body)

    def test_pilot_skill_contract(self):
        text = SKILL.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
        self.assertIsNotNone(match, "pilot skill must have YAML frontmatter")
        fm, body = match.groups()
        self.assertRegex(fm, r"(?m)^name: agy-native-pilot$")
        self.assertRegex(fm, r"(?m)^description: .+")
        for phrase in ("agy-implementer", "agy-verifier", "sequentially", "source-only", "quota", "not treat these prose instructions as a permission sandbox"):
            self.assertIn(phrase, body)
        self.assertFalse((SKILL.parent / "scripts").exists())
        self.assertFalse((SKILL.parent / "references").exists())
        self.assertFalse((SKILL.parent / "templates").exists())


if __name__ == "__main__":
    unittest.main()
