"""Tests for scripts/ci/skill_clobber.py (SHE known repair: clobbered SKILL.md).

Fixtures in tests/fixtures/skill_clobber/ are the exact stub bodies that were
committed to master between 2026-10-14 and 2026-10-18.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "ci"))

import skill_clobber as sc  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "skill_clobber"

HEADER = "---\nname: demo\ndescription: demo skill\n---\n# Demo\n## Control objective\n"


def body(n: int, start: int = 0) -> str:
    return HEADER + "".join(f"Session 2026-10-{(i % 28) + 1:02d} line {i}\n" for i in range(start, start + n))


class RealClobberCorpus(unittest.TestCase):
    def test_every_observed_stub_is_flagged(self) -> None:
        files = sorted(FIXTURES.glob("*.txt"))
        self.assertGreaterEqual(len(files), 6)
        parent = body(400)
        for f in files:
            with self.subTest(fixture=f.name):
                v = sc.evaluate("x/SKILL.md", f.read_text(encoding="utf-8"), parent)
                self.assertTrue(v.clobbered, f.name)

    def test_placeholder_too_large_underscore_variant(self) -> None:
        self.assertTrue(sc.placeholder_hits("PLACEHOLDER_TOO_LARGE"))


class ContentEvaluation(unittest.TestCase):
    def test_reorder_with_all_content_kept_passes(self) -> None:
        parent = body(300)
        lines = parent.splitlines(keepends=True)
        head, tail = lines[:6], lines[6:]
        v = sc.evaluate("x/SKILL.md", "".join(head + tail[::-1]), parent)
        self.assertFalse(v.clobbered)
        self.assertEqual(v.delta["lost"], 0)
        self.assertTrue(v.delta["reordered"])

    def test_same_size_replacement_fails(self) -> None:
        parent = body(300)
        junk = HEADER + "".join(f"filler {i}\n" for i in range(300))
        self.assertTrue(sc.evaluate("x/SKILL.md", junk, parent).clobbered)

    def test_append_passes(self) -> None:
        parent = body(300)
        v = sc.evaluate("x/SKILL.md", parent + "\nSession 2026-10-19 new stamp\n", parent)
        self.assertFalse(v.clobbered)
        self.assertEqual(v.delta["lost"], 0)

    def test_partial_restore_fails(self) -> None:
        parent = body(600)
        self.assertTrue(sc.evaluate("x/SKILL.md", body(100), parent).clobbered)

    def test_override_turns_loss_into_warning(self) -> None:
        parent = body(600)
        v = sc.evaluate("x/SKILL.md", body(100), parent, override=True)
        self.assertFalse(v.clobbered)
        self.assertTrue(v.warnings)

    def test_small_new_file_is_not_flagged(self) -> None:
        self.assertFalse(sc.evaluate("x/SKILL.md", HEADER, None).clobbered)


class Repair(unittest.TestCase):
    def _repo(self) -> pathlib.Path:
        d = pathlib.Path(tempfile.mkdtemp())
        for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *a], cwd=d, check=True)
        return d

    def _commit(self, d: pathlib.Path, text: str, msg: str) -> None:
        p = d / "s" / "SKILL.md"
        p.parent.mkdir(exist_ok=True)
        p.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=d, check=True)
        subprocess.run(["git", "commit", "-qm", msg], cwd=d, check=True)

    def test_restores_last_good_and_keeps_new_stamp(self) -> None:
        d = self._repo()
        good = body(500)
        self._commit(d, good, "good")
        self._commit(d, "$(cat /tmp/skill.md)", "clobber")
        partial = body(80) + "\n[NOTE: Full historical sessions preserved in prior commits]\n\nSession 2026-10-19 brand new stamp\n"
        self._commit(d, partial, "partial restore")
        found = sc.last_good("s/SKILL.md", "HEAD", cwd=d)
        self.assertIsNotNone(found)
        sha, text = found
        self.assertEqual(text, good)
        fixed = sc.repair_text(text, partial)
        self.assertTrue(fixed.startswith(good.rstrip("\n")))
        self.assertIn("brand new stamp", fixed)
        self.assertNotIn("preserved in prior commits", fixed)
        self.assertFalse(sc.evaluate("s/SKILL.md", fixed, good).clobbered)

    def test_partial_restore_after_stub_parent_is_judged_against_last_good(self) -> None:
        d = self._repo()
        self._commit(d, body(500), "good")
        self._commit(d, "PLACEHOLDER", "clobber")
        self._commit(d, body(80), "partial restore")
        ref, label = sc.reference_text("s/SKILL.md", "HEAD~1", cwd=d)
        self.assertIn("last-good", label)
        self.assertTrue(sc.evaluate("s/SKILL.md", body(80), ref).clobbered)


if __name__ == "__main__":
    unittest.main()
