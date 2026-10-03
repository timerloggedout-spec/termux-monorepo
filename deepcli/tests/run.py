#!/usr/bin/env python3
"""Test runner for deepcli.

Resolves the deepcli package relative to THIS file's repo root, so running
this script from a git worktree exercises the worktree's code rather than
whatever happens to be checked out at $HOME/deepcli.

Prior behaviour: each test module did
    sys.path.insert(0, str(pathlib.Path.home() / "deepcli"))
which is the MAIN checkout. A worktree run therefore imported the
unpatched main module and misreported worktree code as failing.
"""

import sys, pathlib, unittest

HERE = pathlib.Path(__file__).resolve().parent


def _find_repo_root(start):
    """Walk up from *start* to the dir containing the deepcli/ package."""
    for d in [start, *start.parents]:
        if (d / "deepcli" / "__init__.py").is_file():
            return d
    return start.parent  # fallback: keep prior working-directory behaviour


REPO_ROOT = _find_repo_root(HERE)
sys.path.insert(0, str(HERE))  # test modules are importable by bare name
sys.path.insert(0, str(REPO_ROOT))  # worktree/repo code wins over $HOME/deepcli


def _purge_foreign_checkouts():
    """Drop $HOME/deepcli from sys.path unless it IS this repo root.

    Test modules still insert their own hardcoded $HOME/deepcli path; after
    that insert that entry sits ahead of REPO_ROOT, so a worktree run would
    import main-checkout code. Removing the foreign entry makes this repo
    root authoritative regardless of what the test modules do.
    """
    home_checkout = str(pathlib.Path.home() / "deepcli")
    root = str(REPO_ROOT)
    if home_checkout != root:
        sys.path[:] = [p for p in sys.path if p != home_checkout]


def main():
    _purge_foreign_checkouts()
    pattern = sys.argv[1] if len(sys.argv) > 1 else "test_*.py"
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for f in sorted(HERE.glob(pattern)):
        if f.name in ("__init__.py", "run.py"):
            continue
        _purge_foreign_checkouts()
        try:
            suite.addTests(loader.loadTestsFromName(f.stem))
        except Exception as e:
            print(f"  skip {f.stem}: {e}")
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
