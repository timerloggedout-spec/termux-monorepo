"""_v1_files: path-allowlist gate (_safe) + Python syntax gate (_ruff_check).

First coverage for deepcli/_v1_files.py. Both units under test are pure and
offline: no HTTP, no network, no writes.

Invariant under test:
  * `_safe(path, allow_list=...)` returns a resolved Path iff that path is
    equal to, or nested under, exactly one of the resolved allow-roots;
    otherwise it raises HTTPException(403). Traversal (`..`) is neutralised
    by `.resolve()`, so an escaping path is rejected.
  * `_ruff_check(path, text)` returns None when `text` compiles as Python
    (and unconditionally for non-`.py` paths), and a non-empty error string
    when it does not.
"""

import pathlib
import sys
import tempfile
import unittest


# Checkout-relative bootstrap: walk up from this file to the directory that
# directly contains _v1_files.py (the repo's deepcli/ dir), then put that on
# sys.path. $HOME/deepcli is only a last-resort fallback.
def _checkout_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "_v1_files.py").is_file():
            return parent
    return pathlib.Path.home() / "deepcli"


sys.path.insert(0, str(_checkout_root()))

from fastapi import HTTPException  # noqa: E402
from _v1_files import (  # noqa: E402
    _safe,
    _ruff_check,
    WRITE_ALLOW,
    READ_ALLOW,
    MAX_READ_BYTES,
    MAX_WRITE_BYTES,
)


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        root = _checkout_root()
        self.assertTrue((root / "_v1_files.py").is_file())
        self.assertEqual(root, pathlib.Path(__file__).resolve().parent.parent)


class TestSafeAllowlist(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        self.root = self.tmp / "root"
        self.root.mkdir()

    def test_path_equal_to_root_allowed(self):
        got = _safe(str(self.root), allow_list=[self.root])
        self.assertEqual(got, self.root.resolve())

    def test_nested_path_allowed(self):
        nested = self.root / "a" / "b.txt"
        got = _safe(str(nested), allow_list=[self.root])
        self.assertEqual(got, nested.resolve())

    def test_path_outside_roots_rejected(self):
        outside = self.tmp / "other" / "x.txt"
        with self.assertRaises(HTTPException) as ctx:
            _safe(str(outside), allow_list=[self.root])
        self.assertEqual(ctx.exception.status_code, 403)

    def test_traversal_escape_rejected(self):
        # root/../other resolves out of root and must be refused.
        escape = self.root / ".." / "other" / "x.txt"
        with self.assertRaises(HTTPException) as ctx:
            _safe(str(escape), allow_list=[self.root])
        self.assertEqual(ctx.exception.status_code, 403)

    def test_second_root_matches(self):
        other_root = self.tmp / "second"
        other_root.mkdir()
        target = other_root / "f.txt"
        got = _safe(str(target), allow_list=[self.root, other_root])
        self.assertEqual(got, target.resolve())

    def test_result_is_resolved(self):
        # A non-normalised input still comes back fully resolved.
        nested = self.root / "sub" / ".." / "f.txt"
        got = _safe(str(nested), allow_list=[self.root])
        self.assertEqual(got, (self.root / "f.txt").resolve())
        self.assertTrue(got.is_absolute())


class TestRuffCheck(unittest.TestCase):
    def test_non_python_path_is_skipped(self):
        self.assertIsNone(_ruff_check("notes.txt", "this is not python )("))

    def test_valid_python_returns_none(self):
        self.assertIsNone(_ruff_check("ok.py", "x = 1\n"))

    def test_syntax_error_returns_message(self):
        err = _ruff_check("bad.py", "def f(:\n")
        self.assertIsInstance(err, str)
        self.assertTrue(err)
        self.assertIn("Syntax", err)

    def test_valid_python_no_trailing_newline(self):
        self.assertIsNone(_ruff_check("ok.py", "x = 1"))


class TestConstants(unittest.TestCase):
    def test_read_write_limits_equal(self):
        self.assertEqual(MAX_READ_BYTES, 512 * 1024)
        self.assertEqual(MAX_WRITE_BYTES, 512 * 1024)

    def test_write_allow_is_subset_of_read_allow(self):
        # Every writable root must also be a readable root (home covers all).
        home = pathlib.Path.home().resolve()
        for root in WRITE_ALLOW:
            resolved = root.resolve()
            self.assertTrue(
                resolved == home or home in resolved.parents,
                f"write root {resolved} escapes home",
            )
        self.assertTrue(any(r.resolve() == home for r in READ_ALLOW))


if __name__ == "__main__":
    unittest.main()
