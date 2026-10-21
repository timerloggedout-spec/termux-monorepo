"""Keep function-search patterns as data across the shell and jq boundaries."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shlex
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "archwiz" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FuncfindSafetyTests(unittest.TestCase):
    def test_pattern_is_a_separate_jq_argument_and_filter_is_static(self):
        for name in ("aether", "forge"):
            module = load(name)
            module.LLM_MAP = "/tmp/a path; $(touch path-marker)"
            filters = []
            for pattern in ("normal", "'; touch pattern-marker; #", '") or true or test("'):
                with self.subTest(module=name, pattern=pattern):
                    with patch.object(module, "run", return_value=("", "", 0)) as run:
                        with contextlib.redirect_stdout(io.StringIO()):
                            module.cmd_funcfind([pattern])
                    tokens = shlex.split(run.call_args.args[0])
                    self.assertEqual(tokens[:5], ["jq", "-r", "--arg", "pattern", pattern])
                    self.assertEqual(tokens[-1], module.LLM_MAP + "/func_index.jsonl")
                    self.assertEqual(len(tokens), 7)
                    filters.append(tokens[5])
            self.assertEqual(len(set(filters)), 1)
            self.assertIn("test($pattern)", filters[0])

    @unittest.skipUnless(shutil.which("jq"), "jq is optional on the host")
    def test_real_shell_and_jq_preserve_patterns_and_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index_dir = root / "map with spaces; $(touch path-marker)"
            index_dir.mkdir()
            records = [
                {"file": 'src/a"b.py', "name": "quoted", "line": 7, "sig": "quoted()"},
                {"file": "src/worker.py", "name": "worker", "line": 9, "sig": "w" * 70},
                {"file": "docs/worker.md", "name": "unrelated", "line": 11, "sig": "docs()"},
            ]
            (index_dir / "func_index.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records), encoding="utf-8"
            )
            marker = root / "pattern-marker"
            cases = [
                ('a"b', "quoted \t line 7 \t quoted()"),
                (r"src/.*\.py$", "quoted \t line 7 \t quoted()\nworker \t line 9 \t " + "w" * 60),
                (f"'; touch {shlex.quote(str(marker))}; #", ""),
                ('") or true or test("', ""),
            ]
            for name in ("aether", "forge"):
                module = load(name)
                module.LLM_MAP = str(index_dir)
                for pattern, expected in cases:
                    with self.subTest(module=name, pattern=pattern):
                        output = io.StringIO()
                        real_run = module.run
                        with patch.object(module, "run", side_effect=lambda command: real_run(command, cwd=root)):
                            with contextlib.redirect_stdout(output):
                                module.cmd_funcfind([pattern])
                        self.assertEqual(output.getvalue().strip(), expected)
                        self.assertFalse(marker.exists())
                        self.assertFalse((root / "path-marker").exists())

    def test_empty_arguments_do_not_run_a_command(self):
        for name in ("aether", "forge"):
            with self.subTest(module=name):
                module = load(name)
                with patch.object(module, "run") as run:
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        module.cmd_funcfind([])
                run.assert_not_called()
                self.assertIn("Usage:", output.getvalue())


if __name__ == "__main__":
    unittest.main()
