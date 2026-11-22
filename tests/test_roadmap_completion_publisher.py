import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "roadmap-completions/scripts/publish-completion.py"


class RoadmapCompletionPublisherTests(unittest.TestCase):
    def make_fixture(self, root: Path) -> None:
        config = root / "roadmap-completions/config"
        config.mkdir(parents=True)
        (config / "verification-rules.yaml").write_text(
            "badge_levels:\n"
            "  bronze: {min_score: 60, max_score: 69, label: BRONZE, color: '#CD7F32'}\n"
            "  platinum: {min_score: 95, max_score: 100, label: PLATINUM, color: '#000000'}\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("# Repository\n", encoding="utf-8")

    def test_publishes_badge_and_readme_row_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            command = [
                sys.executable, str(SCRIPT), "--root", str(root),
                "--roadmap", "mlops", "--exercise", "implement-ml-pipeline", "--score", "100",
            ]
            first = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            result = json.loads(first.stdout)
            self.assertEqual(result["level"], "platinum")
            badge = root / result["badge"]
            self.assertTrue(badge.is_file())
            self.assertIn("PLATINUM", badge.read_text(encoding="utf-8"))

            second = subprocess.run(command, check=False, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertEqual(readme.count("| mlops | implement-ml-pipeline |"), 1)

    def test_rejects_invalid_slug(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture(root)
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "--root", str(root),
                    "--roadmap", "../escape", "--exercise", "intro", "--score", "100",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
