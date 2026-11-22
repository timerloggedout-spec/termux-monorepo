import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "roadmap-completions/scripts/verify-completion.py"
SPEC = importlib.util.spec_from_file_location("roadmap_verifier", SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class RoadmapCompletionVerifierTests(unittest.TestCase):
    def make_fixture(self, root: Path, *, coverage: int = 85) -> None:
        (root / "roadmap-completions/config").mkdir(parents=True)
        exercise = root / "roadmap-completions/roadmaps/demo/exercises/intro"
        exercise.mkdir(parents=True)
        (root / "roadmap-completions/config/verification-rules.yaml").write_text(
            "defaults:\n"
            "  code: {required: true, min_size: 10, patterns: ['def run'], extensions: ['.py']}\n"
            "  test: {required: true, min_coverage: 80, passing: true}\n"
            "  documentation: {required: true, min_words: 3, sections: ['Overview']}\n"
            "  portfolio: {required: false}\n"
            "roadmaps:\n"
            "  demo:\n"
            "    exercises:\n"
            "      intro:\n"
            "        rules: {}\n",
            encoding="utf-8",
        )
        (exercise / "solution.py").write_text("def run():\n    return 1\n", encoding="utf-8")
        (exercise / "test_solution.py").write_text("def test_run():\n    assert True\n", encoding="utf-8")
        (exercise / "README.md").write_text("# Overview\nThis is useful documentation.", encoding="utf-8")
        (exercise / "evidence.json").write_text(
            json.dumps(
                {
                    "roadmap": "demo",
                    "exercise": "intro",
                    "status": "completed",
                    "evidence": [
                        {"type": "code", "path": "roadmap-completions/roadmaps/demo/exercises/intro/solution.py"},
                        {"type": "test", "path": "roadmap-completions/roadmaps/demo/exercises/intro/test_solution.py", "coverage": coverage, "passing": True},
                        {"type": "documentation", "path": "roadmap-completions/roadmaps/demo/exercises/intro/README.md"},
                    ],
                }
            ),
            encoding="utf-8",
        )

    def run_verifier(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root), "--roadmap", "demo", "--exercise", "intro"],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_evidence_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            result = self.run_verifier(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_insufficient_coverage_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root, coverage=20)
            result = self.run_verifier(root)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["ok"])

    def test_path_traversal_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            evidence = root / "roadmap-completions/roadmaps/demo/exercises/intro/evidence.json"
            data = json.loads(evidence.read_text(encoding="utf-8"))
            data["evidence"][0]["path"] = "../../outside.py"
            evidence.write_text(json.dumps(data), encoding="utf-8")
            result = self.run_verifier(root)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["ok"])

    def test_github_portfolio_checks_required_remote_files(self):
        required = ["README.md", "LICENSE", "requirements.txt", "Dockerfile"]
        files = required + [f"src/module_{index}.py" for index in range(6)]
        responses = [
            io.BytesIO(json.dumps({"default_branch": "main"}).encode("utf-8")),
            io.BytesIO(json.dumps({
                "truncated": False,
                "tree": [{"path": path, "type": "blob"} for path in files],
            }).encode("utf-8")),
        ]
        with patch.object(VERIFIER.urllib.request, "urlopen", side_effect=responses):
            ok, detail = VERIFIER.validate_github_portfolio(
                "https://github.com/example/portfolio",
                {"required_files": required, "min_files": 10},
            )
        self.assertTrue(ok, detail)
        self.assertIn("files=10", detail)

    def test_github_portfolio_rejects_non_repository_urls(self):
        ok, detail = VERIFIER.validate_github_portfolio(
            "https://example.com/portfolio",
            {"required_files": [], "min_files": 0},
        )
        self.assertFalse(ok)
        self.assertIn("GitHub repository", detail)


if __name__ == "__main__":
    unittest.main()
