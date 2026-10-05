"""_v1_skills — frontmatter parsing + skill discovery (offline coverage)."""

import sys, pathlib, tempfile, unittest


def _repo_root():
    """Return the checkout that owns this test file's ``_v1_skills.py``.

    Walk up from __file__ to the directory that directly contains
    ``_v1_skills.py`` (the repo root; ``tests/`` sits one level below it).
    A ``$HOME/deepcli`` fallback preserves the old behaviour when no
    checkout root is found.
    """
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "_v1_skills.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_repo_root()))
import _v1_skills as skills


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _repo_root()
        self.assertTrue((root / "_v1_skills.py").is_file())
        self.assertIn(root, pathlib.Path(__file__).resolve().parents)


class TestParseFrontmatter(unittest.TestCase):
    def test_no_frontmatter_returns_empty_dict_and_whole_text(self):
        fm, body = skills._parse_frontmatter("just a body\n")
        self.assertEqual(fm, {})
        self.assertEqual(body, "just a body\n")

    def test_basic_key_values(self):
        text = "---\nname: my-skill\ndescription: does things\n---\nbody here\n"
        fm, body = skills._parse_frontmatter(text)
        self.assertEqual(fm["name"], "my-skill")
        self.assertEqual(fm["description"], "does things")
        self.assertEqual(body, "body here\n")

    def test_quotes_stripped_from_values(self):
        text = "---\nname: \"quoted\"\ndescription: 'single'\n---\nx\n"
        fm, _ = skills._parse_frontmatter(text)
        self.assertEqual(fm["name"], "quoted")
        self.assertEqual(fm["description"], "single")

    def test_lines_without_colon_ignored(self):
        text = "---\nname: a\nno-colon-here\n---\nz\n"
        fm, _ = skills._parse_frontmatter(text)
        self.assertEqual(fm, {"name": "a"})

    def test_value_with_inner_colon_kept(self):
        text = "---\ndescription: a: b: c\n---\nz\n"
        fm, _ = skills._parse_frontmatter(text)
        self.assertEqual(fm["description"], "a: b: c")


class TestSkillsDiscovery(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self._orig_roots = skills.SKILL_ROOTS
        skills.SKILL_ROOTS = [self.tmp]

    def tearDown(self):
        skills.SKILL_ROOTS = self._orig_roots

    def _mk(self, dirname, filename="SKILL.md", text=None):
        d = self.tmp / dirname
        d.mkdir(parents=True, exist_ok=True)
        (d / filename).write_text(
            text if text is not None else f"---\nname: {dirname}\n---\nbody\n"
        )
        return d

    def test_empty_root_yields_no_skills(self):
        self.assertEqual(skills._skills(), [])

    def test_discovers_skill_and_reports_fields(self):
        self._mk("alpha", text="---\nname: alpha\ndescription: first\n---\nBODY\n")
        out = skills._skills()
        self.assertEqual(len(out), 1)
        s = out[0]
        self.assertEqual(s["name"], "alpha")
        self.assertEqual(s["description"], "first")
        self.assertEqual(s["body_size"], len("BODY\n"))
        self.assertFalse(s["has_assets"])
        self.assertFalse(s["has_references"])

    def test_name_falls_back_to_dirname(self):
        self._mk("noname", text="body only, no frontmatter\n")
        self.assertEqual(skills._skills()[0]["name"], "noname")

    def test_lowercase_skill_md_supported(self):
        self._mk("lower", filename="skill.md", text="---\nname: lower\n---\nx\n")
        self.assertEqual(skills._skills()[0]["name"], "lower")

    def test_dir_without_skill_md_skipped(self):
        (self.tmp / "empty").mkdir()
        self.assertEqual(skills._skills(), [])

    def test_duplicate_names_first_wins(self):
        self._mk("a1", text="---\nname: dup\n---\n1\n")
        self._mk("a2", text="---\nname: dup\n---\n2\n")
        out = skills._skills()
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["name"], "dup")

    def test_sorted_by_name(self):
        self._mk("zzz", text="---\nname: zzz\n---\nx\n")
        self._mk("aaa", text="---\nname: aaa\n---\nx\n")
        self.assertEqual([s["name"] for s in skills._skills()], ["aaa", "zzz"])

    def test_has_assets_and_references_flags(self):
        d = self._mk("flagged", text="---\nname: flagged\n---\nx\n")
        (d / "assets").mkdir()
        (d / "references").mkdir()
        s = skills._skills()[0]
        self.assertTrue(s["has_assets"])
        self.assertTrue(s["has_references"])


if __name__ == "__main__":
    unittest.main()
