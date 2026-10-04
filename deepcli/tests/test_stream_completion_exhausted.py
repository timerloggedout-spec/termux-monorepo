"""stream_completion retry-exhaustion must not raise NameError."""
import ast, pathlib, unittest

CORE = pathlib.Path(__file__).resolve().parents[1] / "deepcli" / "core.py"


class TestStreamCompletionExhausted(unittest.TestCase):
    def test_no_unbound_final_text(self):
        src = CORE.read_text()
        # Bug: the all-retries-exhausted tail returned `final_text`,
        # an identifier never assigned in stream_completion (success
        # path returns early).  NameError fired only when every retry
        # was used up.  Invariant: `final_text` must not appear.
        self.assertNotIn("final_text", src)

    def test_exhausted_path_returns_empty_string(self):
        tree = ast.parse(CORE.read_text())
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "stream_completion")
        # Find the tail Return statement after the retry loop.
        returns = [n for n in ast.walk(fn) if isinstance(n, ast.Return)]
        # At least one return must yield a constant empty string.
        self.assertTrue(any(isinstance(r.value, ast.Constant) and r.value.value == ""
                            for r in returns))


if __name__ == "__main__":
    unittest.main()
