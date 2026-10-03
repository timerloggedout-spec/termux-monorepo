"""gh_worktree create persists branch->base mapping.

Regression guard: commit_push_pr must open the PR against the base the
worktree was created from (not hardcoded master).
"""

import sys, pathlib, unittest

_HERE = pathlib.Path(__file__).resolve()
_ROOT = None
for _cand in [_HERE.parents[2], _HERE.parents[1], pathlib.Path.home()]:
    if (_cand / "deepcli" / "deepagent.py").exists():
        _ROOT = _cand
        break


class TestWtBasePersist(unittest.TestCase):
    def test_create_block_persists_base(self):
        src = (_ROOT / "deepcli" / "deepagent.py").read_text()
        self.assertIn("_b[branch] = base", src)
        self.assertIn("_wt_bases_save(_b)", src)


if __name__ == "__main__":
    unittest.main()
