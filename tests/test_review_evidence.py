import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.model_selection_market import review_evidence as re

SHA = "a" * 40
REPO = "timerloggedout-spec/termux-monorepo"


def review(i, state="APPROVED", submitted="2025-01-01T00:00:00Z", login="alice", typ="User"):
    return {
        "id": i, "state": state, "submitted_at": submitted,
        "user": {"login": login, "type": typ},
        "html_url": f"https://github.com/{REPO}/pull/1297",
    }


def comment(i, login="bob", typ="User"):
    return {"id": i, "user": {"login": login, "type": typ}}


def commit(i, sha, author=None, committer=None):
    return {"id": i, "sha": sha, "commit": {}, "author": author, "committer": committer}


class ReviewEvidenceTests(unittest.TestCase):
    def test_pages_counts_actor_types_and_commit_identity(self):
        result = re.normalize(
            [[review(1), review(2, "PENDING", None, "ci[bot]", "Bot")]],
            [comment(3)], [[comment(4, "ci[bot]", "Bot")]],
            [commit(5, "b" * 40, {"name": "Hidden Name", "email": "x@y"}, None)],
            repo=REPO, pr=1297, head_sha=SHA,
        )
        self.assertEqual(result["counts"], {
            "formal_submitted_reviews": 1, "pending_reviews": 1,
            "conversation_comments": 1, "inline_comments": 1, "commits": 1,
            "formal_review_states": {"APPROVED": 1},
        })
        self.assertEqual(result["actors"]["formal_reviews"]["users"], {"alice": 1})
        self.assertEqual(result["actors"]["pending_reviews"]["bots"], {"ci[bot]": 1})
        self.assertEqual(result["actors"]["commit_authors"], {})
        output = json.dumps(result)
        self.assertNotIn("x@y", output)
        self.assertNotIn("Hidden Name", output)
        self.assertEqual(result["provenance"]["commit_shas"], ["b" * 40])

    def test_realistic_github_commit_record_and_null_actor_type(self):
        sha = "c" * 40
        github_commit = {
            "sha": sha, "node_id": "C_node", "html_url": f"https://github.com/{REPO}/commit/{sha}",
            "commit": {"author": {"name": "Hidden", "email": "private@example.com"},
                       "committer": {"name": "Hidden", "email": "private@example.com"}},
            "author": None, "committer": None,
        }
        unknown = comment(9)
        unknown["user"].pop("type")
        result = re.normalize([], [unknown], [], [github_commit], repo=REPO, pr=1297, head_sha=SHA)
        self.assertEqual(result["provenance"]["commit_ids"], [sha])
        self.assertEqual(result["actors"]["conversation_comments"]["users"], {})
        self.assertEqual(result["actors"]["conversation_comments"]["bots"], {})
        serialized = json.dumps(result)
        self.assertNotIn("private@example.com", serialized)
        self.assertNotIn("Hidden", serialized)

    def test_review_states_are_enum_validated(self):
        bad = review(7, "SUBMITTED")
        with self.assertRaises(re.EvidenceError):
            re.normalize([bad], [], [], [], repo=REPO, pr=1297, head_sha=SHA)

    def test_flat_inputs_and_comments_are_not_reviews(self):
        result = re.normalize([], [comment(2), comment(3)], [], [], repo=REPO, pr=1297, head_sha=SHA)
        self.assertEqual(result["counts"]["formal_submitted_reviews"], 0)
        self.assertEqual(result["counts"]["conversation_comments"], 2)

    def test_fail_closed_inputs_and_duplicates(self):
        cases = [
            ([[review(1), review(1)]], [], [], []),
            ([{"id": 1}], [], [], []),
            ([[review(1)]], [], [], [commit(2, "bad")]),
        ]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(re.EvidenceError):
                re.normalize(*args, repo=REPO, pr=1297, head_sha=SHA)
        bad = review(8)
        bad["pull_request_url"] = "https://api.github.com/repos/evil/repo/pulls/1"
        with self.assertRaises(re.EvidenceError):
            re.normalize([bad], [], [], [], repo=REPO, pr=1297, head_sha=SHA)

    def test_cli_atomic_on_invalid_and_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = []
            payloads = [[[review(1)]], [[comment(2)]], [], []]
            for i, payload in enumerate(payloads):
                path = root / f"{i}.json"
                path.write_text(json.dumps(payload))
                files.append(path)
            output = root / "out.json"
            output.write_text("preserve")
            args = [
                "--reviews", str(files[0]), "--comments", str(files[1]),
                "--inline-comments", str(files[2]), "--commits", str(files[3]),
                "--output", str(output), "--repo", REPO, "--pr", "1297", "--head-sha", SHA,
            ]
            files[0].write_text(json.dumps([{"id": 1}]))
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                re.main(args)
            self.assertEqual(output.read_text(), "preserve")
            files[0].write_text(json.dumps(payloads[0]))
            self.assertEqual(re.main(args), 0)
            self.assertEqual(json.loads(output.read_text())["counts"]["formal_submitted_reviews"], 1)


if __name__ == "__main__":
    unittest.main()
