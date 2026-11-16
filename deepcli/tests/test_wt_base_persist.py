"""gh_worktree create persists branch->base mapping.

Regression guard: commit_push_pr must open the PR against the base the
worktree was created from (not hardcoded master).

Adapted for the modular tree (CAB Phase B->A): the worktree machinery
lives in deepcli/deepcli/recapitulation/worktree.py, not the deepagent.py
monolith this test originally parsed.
"""

import pathlib
import unittest

_HERE = pathlib.Path(__file__).resolve()
_MODULE = None
for _cand in [_HERE.parents[1], _HERE.parents[2], pathlib.Path.home()]:
    _p = _cand / "deepcli" / "recapitulation" / "worktree.py"
    if _p.exists():
        _MODULE = _p
        break
    _p = _cand / "deepcli" / "deepcli" / "recapitulation" / "worktree.py"
    if _p.exists():
        _MODULE = _p
        break


class TestWtBasePersist(unittest.TestCase):
    def test_create_block_persists_base(self):
        self.assertIsNotNone(_MODULE, "recapitulation/worktree.py not found")
        src = _MODULE.read_text()
        self.assertIn("_b[branch] = base", src)
        self.assertIn("_wt_bases_save(_b)", src)


if __name__ == "__main__":
    unittest.main()
