"""Exercise the actual PR snapshot shell block without making live API calls."""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import textwrap
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/governed-pr-auto-merge-readiness.yml"


class SnapshotCollectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        workflow = WORKFLOW.read_text()
        marker = "      - name: Collect bounded PR and branch-protection snapshot\n"
        section = workflow.split(marker, 1)[1].split("      - name:", 1)[0]
        cls.script = textwrap.dedent(section.split("        run: |\n", 1)[1])
        cls.jq = shutil.which("jq")
        if not cls.jq:
            raise unittest.SkipTest("jq is required by the workflow collector")

    def run_collector(self, protection_mode):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            # A jq shim ensures the collector resolves the test-controlled executable.
            jq_shim = bin_dir / "jq"
            jq_shim.write_text("#!/bin/sh\nexec " + self.jq + " \"$@\"\n")
            jq_shim.chmod(0o755)
            gh = bin_dir / "gh"
            gh.write_text(r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
if args[:1] == ["api"]:
    endpoint = args[-1]
    if endpoint.endswith("/pulls/42"):
        print(json.dumps({"base":{"ref":"main"},"labels":[{"name":"automerge:eligible"}],"state":"open","draft":False,"user":{"login":"author"},"head":{"sha":"abc123"}}))
    elif endpoint.endswith("/branches/main/protection"):
        if os.environ["PROTECTION_MODE"] == "success":
            print(json.dumps({"required_pull_request_reviews":{"required_approving_review_count":1,"dismiss_stale_reviews":True,"require_last_push_approval":False},"required_status_checks":{"contexts":["repo-gate","workflow-surface-policy"]},"required_conversation_resolution":{"enabled":True}}))
        else:
            print(json.dumps({"message": "Branch not protected" if os.environ["PROTECTION_MODE"] == "404" else "Resource not accessible by integration", "status": os.environ["PROTECTION_MODE"]}))
            print("gh: protection lookup failed", file=sys.stderr)
            sys.exit(1)
    elif endpoint.endswith("/pulls/42/reviews"):
        print(json.dumps([{"user":{"login":"reviewer","type":"User"},"state":"APPROVED","submitted_at":"2026-10-19T12:00:00Z","commit_id":"abc123"}]))
    else: sys.exit("unexpected API endpoint: " + endpoint)
elif args[:2] == ["pr", "view"]:
    print("CLEAN")
else: sys.exit("unexpected gh call")
''')
            gh.chmod(0o755)
            temp = root / "temp"
            temp.mkdir()
            env = os.environ.copy()
            env.update({"PATH": str(bin_dir) + os.pathsep + env["PATH"], "REPOSITORY":"org/repo", "EVENT_PR":"42", "DISPATCH_PR":"", "AUTO_MERGE_ENABLED":"true", "RUNNER_TEMP":str(temp), "GITHUB_OUTPUT":str(root/"output"), "PROTECTION_MODE":protection_mode})
            subprocess.run(["bash", "-euo", "pipefail", "-c", self.script], cwd=ROOT, env=env, check=True, capture_output=True, text=True)
            raw = (temp / "pr-merge-snapshot.json").read_text()
            snapshot = json.loads(raw)
            self.assertEqual(len(raw.splitlines()), 1)
            evaluator = subprocess.run(["python3", str(ROOT / "scripts/ci/pr_merge_readiness.py"),], input=raw, text=True, capture_output=True, check=True)
            decision = json.loads(evaluator.stdout)
            return snapshot, decision

    def test_successful_protection_produces_valid_snapshot(self):
        snapshot, decision = self.run_collector("success")
        self.assertIn("required_pull_request_reviews", snapshot["protection"])
        self.assertEqual(decision["decision"], "enable_auto_merge")

    def test_failed_404_stdout_is_replaced_with_unavailable(self):
        snapshot, decision = self.run_collector("404")
        self.assertEqual(snapshot["protection"], {"unavailable": True})
        self.assertEqual(decision["decision"], "wait")

    def test_failed_403_stdout_is_replaced_with_unavailable(self):
        snapshot, decision = self.run_collector("403")
        self.assertEqual(snapshot["protection"], {"unavailable": True})
        self.assertEqual(decision["decision"], "wait")


if __name__ == "__main__":
    unittest.main()
