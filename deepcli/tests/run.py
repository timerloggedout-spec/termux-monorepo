#!/usr/bin/env python3
"""Discover and run unittest modules in this directory.

Hardened discovery contract (regression guard):

* Every ``test_*.py`` file (except ``__init__.py``/``run.py``) MUST
  contribute at least one test to the suite.
* A module that imports cleanly but declares no ``unittest.TestCase``
  (e.g. a plain script with bare ``test_*`` functions) silently
  contributes zero tests under ``loadTestsFromName``. Previously that
  module was invisible and the harness exited 0 -- a green run that
  proved nothing about the module. Now it is reported as a failure.

Exit code is nonzero when either the suite fails OR any ``test_*.py``
module contributes zero tests.
"""

import sys, pathlib, unittest

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))


def count(suite):
    """Number of leaf tests in a (possibly nested) suite."""
    return suite.countTestCases()


def discover(pattern):
    """Load every test_*.py module, returning (suite, per-module counts, errors)."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    counts = {}
    errors = {}
    for f in sorted(HERE.glob(pattern)):
        if f.name in ("__init__.py", "run.py"):
            continue
        try:
            mod_suite = loader.loadTestsFromName(f.stem)
        except Exception as e:  # import error / collection error
            errors[f.stem] = f"{type(e).__name__}: {e}"
            counts[f.stem] = 0
            continue
        counts[f.stem] = count(mod_suite)
        suite.addTests(mod_suite)
    return suite, counts, errors


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "test_*.py"
    suite, counts, errors = discover(pattern)

    empty = sorted(name for name, n in counts.items() if n == 0 and name not in errors)
    for name, msg in sorted(errors.items()):
        print(f"  ERROR collecting {name}: {msg}")
    for name in empty:
        print(
            f"  ERROR {name}.py contributes 0 tests "
            f"(no unittest.TestCase -- is it a bare script?)"
        )

    result = unittest.TextTestRunner(verbosity=1).run(suite)
    ok = result.wasSuccessful() and not empty and not errors
    if not ok:
        print(
            f"  harness: {count(suite)} tests ran, "
            f"{len(empty)} empty module(s), {len(errors)} import error(s)"
        )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
