import json
import unittest
from pathlib import Path

from scripts.swarms.inventory import collect


def record(name, owner="kyegomez", description=None):
    return {
        "name": name,
        "full_name": f"{owner}/{name}",
        "owner": {"login": owner},
        "description": description,
        "html_url": f"https://github.com/{owner}/{name}",
        "default_branch": "main",
        "fork": False,
        "archived": False,
        "disabled": False,
        "license": {"spdx_id": "MIT"},
    }


class InventoryTests(unittest.TestCase):
    def test_default_and_explicit_owner_endpoint_validation(self):
        calls = []

        def fetch(url):
            calls.append(url)
            return 200, {}, json.dumps([record("project")]).encode()

        result = collect(fetch=fetch)
        self.assertEqual(result["owner"], "kyegomez")
        self.assertIn("/users/kyegomez/repos", calls[0])
        with self.assertRaises(ValueError):
            collect("not/a-user", fetch=fetch)

    def test_link_pagination_and_candidate_categories(self):
        calls = []
        second = "https://api.github.com/user/98760976/repos?per_page=100&page=2"

        def fetch(url):
            calls.append(url)
            if len(calls) == 1:
                return 200, {"Link": f'<{second}>; rel="next"'}, json.dumps([record("swarms-demo", description="agent toolkit")]).encode()
            return 200, {}, json.dumps([record("llm-bench", description="model benchmark")]).encode()

        result = collect(fetch=fetch)
        self.assertTrue(result["exhaustive"])
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["pages_fetched"], 2)
        self.assertEqual(result["candidate_classification"]["swarms_related"], ["swarms-demo"])
        self.assertEqual(result["candidate_classification"]["model_research"], ["llm-bench"])
        self.assertIn("not verified code findings", result["candidate_classification"]["basis"])

    def test_rejects_wrong_owner_and_duplicate(self):
        def fetch(_url):
            return 200, {}, json.dumps([record("good"), record("wrong", owner="someoneelse"), record("good")]).encode()

        result = collect(fetch=fetch)
        self.assertFalse(result["exhaustive"])
        self.assertEqual([r["name"] for r in result["repositories"]], ["good"])
        self.assertEqual(result["duplicate_names"], ["good"])
        self.assertTrue(any("wrong repository owner" in e for e in result["errors"]))
        self.assertTrue(any("duplicate repository" in e for e in result["errors"]))

    def test_failure_and_malformed_payload_never_mark_exhaustive(self):
        def fail(_url):
            raise TimeoutError("timed out")

        result = collect(fetch=fail)
        self.assertFalse(result["exhaustive"])
        self.assertTrue(result["errors"])
        failed_status = collect(fetch=lambda _url: (503, {}, b"unavailable"))
        self.assertFalse(failed_status["exhaustive"])
        self.assertIn("HTTP 503", failed_status["errors"][0])
        malformed = collect(fetch=lambda _url: (200, {}, b"{}"))
        self.assertFalse(malformed["exhaustive"])

    def test_missing_next_link_is_exhausted_only_for_successful_page(self):
        result = collect(fetch=lambda _url: (200, {}, json.dumps([record("only")]).encode()))
        self.assertTrue(result["exhaustive"])
        self.assertEqual(result["pages_fetched"], 1)

    def test_unsafe_pagination_is_not_followed(self):
        for target in ("https://example.com/repos", "http://api.github.com/users/kyegomez/repos",
                       "https://api.github.com/user/0", "https://api.github.com/users/other/repos"):
            with self.subTest(target=target):
                calls = []
                def fetch(url):
                    calls.append(url)
                    return 200, {"Link": f'<{target}>; rel="next"'}, b"[]"
                result = collect(fetch=fetch)
                self.assertFalse(result["exhaustive"])
                self.assertEqual(len(calls), 1)

    def test_pagination_loop_is_incomplete(self):
        def fetch(url):
            return 200, {"Link": f'<{url}>; rel="next"'}, b"[]"
        result = collect(fetch=fetch)
        self.assertFalse(result["exhaustive"])
        self.assertIn("pagination loop detected", result["errors"])

    def test_saved_snapshot_is_for_kye_not_monorepo_owner(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = json.loads((root / "docs/research/swarms-kyegomez-repositories.json").read_text())
        self.assertEqual(snapshot["owner"], "kyegomez")
        self.assertTrue(snapshot["public_only"])
        self.assertTrue(snapshot["exhaustive"])
        self.assertEqual(snapshot["errors"], [])
        names = [repo["full_name"] for repo in snapshot["repositories"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(snapshot["total"], len(names))
        self.assertTrue(all(name.lower().startswith("kyegomez/") for name in names))
        self.assertIn("kyegomez/swarms", names)
        historical = json.loads((root / "docs/research/swarms-user-repositories.json").read_text())
        self.assertEqual(historical["owner"], "timerloggedout-spec")


if __name__ == "__main__":
    unittest.main()
