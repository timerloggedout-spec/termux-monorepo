"""_v1_mergeable classification.

Revision 3: sys.path bootstrap is checkout-relative. The package root is
located by walking up from this file to the directory that contains
``deepcli/_v1_mergeable.py``; ``$HOME/deepcli`` is only a last-resort
fallback. This keeps a worktree run importing *that* worktree's
``_v1_mergeable`` rather than the main checkout's copy.
"""

import sys, pathlib, unittest

_HERE = pathlib.Path(__file__).resolve()


def _repo_root():
    """Directory that contains deepcli/_v1_mergeable.py, else $HOME/deepcli."""
    for base in _HERE.parents:
        if (base / "deepcli" / "_v1_mergeable.py").exists():
            return base
    return pathlib.Path.home() / "deepcli"


_ROOT = _repo_root()
sys.path.insert(0, str(_ROOT))
from deepcli._v1_mergeable import (
    is_merge_ready,
    merge_blockers,
    IGNORED_CONTEXTS,
)


def _run(name, conclusion=None, state=None):
    """Build a CheckRun-shaped rollup entry."""
    e = {"name": name}
    if conclusion is not None:
        e["conclusion"] = conclusion
    if state is not None:
        e["state"] = state
    return e


def _ctx(context, state):
    """Build a StatusContext-shaped rollup entry."""
    return {"context": context, "state": state}


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_resolves_to_this_checkout(self):
        # The resolved root must contain the module and be an ancestor of
        # this test file (i.e. the checkout we are running from).
        self.assertTrue((_ROOT / "deepcli" / "_v1_mergeable.py").exists())
        self.assertIn(_ROOT, _HERE.parents)


class TestMergeable(unittest.TestCase):
    def test_all_green_is_ready(self):
        rollup = [
            _run("guard", "SUCCESS"),
            _run("gitleaks", "SUCCESS"),
            _run("evaluate", "SUCCESS"),
        ]
        self.assertTrue(is_merge_ready(rollup))
        self.assertEqual(merge_blockers(rollup), [])

    def test_vercel_failures_are_ignored(self):
        rollup = [
            _run("guard", "SUCCESS"),
            _run("gitleaks", "SUCCESS"),
            _run("evaluate", "SUCCESS"),
            _ctx("Vercel - help-wanted-dash", "FAILURE"),
            _ctx("Vercel - termux-monorepo", "FAILURE"),
            _ctx("Vercel - mcp-hub", "FAILURE"),
            _ctx("Vercel - help-wanted-oversight", "FAILURE"),
        ]
        self.assertTrue(is_merge_ready(rollup))
        self.assertEqual(merge_blockers(rollup), [])

    def test_real_failure_blocks(self):
        rollup = [_run("guard", "SUCCESS"), _run("gitleaks", "FAILURE")]
        self.assertFalse(is_merge_ready(rollup))
        self.assertEqual(merge_blockers(rollup), ["gitleaks"])

    def test_pending_check_blocks(self):
        rollup = [_run("guard", "SUCCESS"), _run("evaluate")]
        self.assertFalse(is_merge_ready(rollup))
        self.assertEqual(merge_blockers(rollup), ["evaluate"])

    def test_status_pending_state_blocks(self):
        rollup = [_ctx("CodeRabbit", "PENDING")]
        self.assertFalse(is_merge_ready(rollup))
        self.assertEqual(merge_blockers(rollup), ["CodeRabbit"])

    def test_skipped_and_neutral_are_not_blockers(self):
        rollup = [
            _run("jules-on-label", "SKIPPED"),
            _run("review", "NEUTRAL"),
            _run("guard", "SUCCESS"),
        ]
        self.assertTrue(is_merge_ready(rollup))

    def test_timed_out_and_cancelled_block(self):
        rollup = [_run("a", "TIMED_OUT"), _run("b", "CANCELLED")]
        self.assertFalse(is_merge_ready(rollup))
        self.assertEqual(sorted(merge_blockers(rollup)), ["a", "b"])

    def test_status_success_passes(self):
        rollup = [
            _ctx("CodeRabbit", "SUCCESS"),
            _ctx("Devin Review", "SUCCESS"),
            _ctx("Gitar", "SUCCESS"),
        ]
        self.assertTrue(is_merge_ready(rollup))

    def test_custom_ignore_list(self):
        rollup = [_run("flaky-optional", "FAILURE")]
        self.assertFalse(is_merge_ready(rollup))
        self.assertTrue(is_merge_ready(rollup, ignore={"flaky-optional"}))

    def test_malformed_entries_do_not_raise(self):
        rollup = [None, 42, "string", {}, _run("guard", "SUCCESS")]
        self.assertFalse(is_merge_ready(rollup))

    def test_non_list_rollup_blocks(self):
        self.assertFalse(is_merge_ready(None))
        self.assertFalse(is_merge_ready("not-a-list"))
        self.assertEqual(merge_blockers(None), ["<malformed rollup>"])

    def test_empty_rollup_is_ready(self):
        self.assertTrue(is_merge_ready([]))

    def test_ignored_prefix_is_case_insensitive(self):
        rollup = [_ctx("VERCEL - thing", "FAILURE"), _run("guard", "SUCCESS")]
        self.assertTrue(is_merge_ready(rollup))

    def test_ignored_contexts_frozen(self):
        self.assertIn("vercel", IGNORED_CONTEXTS)
        with self.assertRaises(AttributeError):
            IGNORED_CONTEXTS.add("x")


if __name__ == "__main__":
    unittest.main()
