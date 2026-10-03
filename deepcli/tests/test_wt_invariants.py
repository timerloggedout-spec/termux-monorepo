"""Guards the gh_worktree PR-open invariants in deepagent.py.

Regression class: iterations 2/7/30 chased a TypeError
(`cannot use 'dict' as a set element`) caused by an `except ...: return {{}}`
set-literal in `_wt_bases_load`, plus a `NameError: _wt_default_repo_branch`
for an undefined helper. Both broke every `gh_worktree commit_push_pr`.

This test parses the source (no import side effects) and asserts the shape
that keeps `commit_push_pr` reaching `gh pr create`.
"""
import ast
import pathlib
import unittest

SRC = pathlib.Path.home() / "deepcli" / "deepagent.py"


class TestWorktreeInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SRC.read_text()
        cls.tree = ast.parse(cls.text)
        cls.funcs = {
            n.name: n for n in ast.walk(cls.tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    def test_source_compiles(self):
        """AST parses cleanly."""
        self.assertTrue(self.tree is not None)

    def test_no_set_literal_dict_return(self):
        """No `return {{}}` set-literal-containing-a-dict anywhere."""
        for fn in self.funcs.values():
            for node in ast.walk(fn):
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Set):
                    for elt in node.value.elts:
                        self.assertNotIsInstance(
                            elt, (ast.Dict, ast.DictComp),
                            f"{fn.name}: return of set containing dict raises TypeError",
                        )

    def test_gh_worktree_has_no_undefined_base_helpers(self):
        """`_gh_worktree` must not call helpers that are not defined."""
        gw = self.funcs.get("_gh_worktree")
        self.assertIsNotNone(gw, "_gh_worktree missing")
        called = {
            n.func.id for n in ast.walk(gw)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        for helper in ("_wt_bases_load", "_wt_default_repo_branch"):
            if helper in called:
                self.assertIn(
                    helper, self.funcs,
                    f"_gh_worktree calls {helper} but it is never defined",
                )

    def test_wt_default_repo_defined_and_used(self):
        """The repo-resolver helper exists and is referenced by _gh_worktree."""
        self.assertIn("_wt_default_repo", self.funcs)
        gw = self.funcs["_gh_worktree"]
        used = {
            n.func.id for n in ast.walk(gw)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
        }
        self.assertIn("_wt_default_repo", used)

    def test_pr_base_never_empty(self):
        """The --base argument expression falls back to a literal default."""
        gw = self.funcs["_gh_worktree"]
        ok = False
        for node in ast.walk(gw):
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                for v in node.values:
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        ok = True
        self.assertTrue(ok, "no `a.get('base') or '<default>'` fallback found")


if __name__ == "__main__":
    unittest.main()
