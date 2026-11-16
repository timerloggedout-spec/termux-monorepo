import unittest
from pathlib import Path
from datetime import datetime, timezone

from lane_matrix_sweep import classify_pr, _age_bucket, VALID_LANES


class LaneMatrixSweepTests(unittest.TestCase):
    def test_inventory_commit_step_declares_event_context_environment(self):
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "ops-lane-matrix-sweep.yml"
        ).read_text(encoding="utf-8")
        commit_step = workflow.split(
            "- name: Commit generated inventory when changed", 1
        )[1].split("\n      - name:", 1)[0]
        for variable in ("GITHUB_TOKEN", "EVENT_NAME", "EVENT_ACTION", "PR_NUMBER"):
            self.assertIn(f"{variable}:", commit_step)


    def test_age_buckets(self):
        self.assertEqual(_age_bucket(46), "ancient")
        self.assertEqual(_age_bucket(25), "stale")
        self.assertEqual(_age_bucket(10), "mid")
        self.assertEqual(_age_bucket(2), "fresh")

    def test_valid_lanes_have_no_parking(self):
        self.assertEqual(
            VALID_LANES,
            {"EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"},
        )
        self.assertTrue({"HOLD", "WAIT", "OBSERVE"}.isdisjoint(VALID_LANES))

    def test_ml_wholesale_extract(self):
        now = datetime(2026, 9, 21, tzinfo=timezone.utc)
        row = classify_pr(
            {
                "number": 432,
                "title": "feat(ml): observe-mode",
                "user": {"login": "timerloggedout-spec"},
                "draft": False,
                "base": {"ref": "master", "sha": "a"},
                "head": {"ref": "b", "sha": "c"},
                "mergeable_state": "dirty",
                "changed_files": 200,
                "created_at": "2026-09-05T00:00:00Z",
            },
            "deadbeef",
            now,
        )
        self.assertEqual(row["lane"], "EXTRACT")

    def test_wrong_base_need_evidence(self):
        now = datetime(2026, 9, 21, tzinfo=timezone.utc)
        row = classify_pr(
            {
                "number": 48,
                "title": "feat hub",
                "user": {"login": "timerloggedout-spec"},
                "draft": False,
                "base": {"ref": "master-staging", "sha": "a"},
                "head": {"ref": "b", "sha": "c"},
                "mergeable_state": "clean",
                "changed_files": 5,
                "created_at": "2026-08-05T00:00:00Z",
            },
            "deadbeef",
            now,
        )
        self.assertEqual(row["lane"], "NEED_EVIDENCE")
        self.assertIn("wrong-base:master-staging", row["reasons"])

    def test_keep_alive_extract_not_wait(self):
        now = datetime(2026, 9, 25, tzinfo=timezone.utc)
        row = classify_pr(
            {
                "number": 682,
                "title": "feat(ml): keep-alive pipeline DAG",
                "user": {"login": "timerloggedout-spec"},
                "draft": False,
                "base": {"ref": "master", "sha": "a"},
                "head": {"ref": "b", "sha": "c"},
                "mergeable_state": "dirty",
                "changed_files": 12,
                "created_at": "2026-09-20T00:00:00Z",
            },
            "deadbeef",
            now,
        )
        self.assertEqual(row["lane"], "EXTRACT")
        self.assertNotEqual(row["lane"], "WAIT")

    def test_age_is_informational_and_never_changes_disposition(self):
        now = datetime(2026, 11, 5, tzinfo=timezone.utc)
        pr = {
            "number": 900,
            "title": "feat(ops): long-lived but clean PR",
            "user": {"login": "timerloggedout-spec"},
            "draft": False,
            "base": {"ref": "master", "sha": "a"},
            "head": {"ref": "b", "sha": "c"},
            "mergeable_state": "clean",
            "changed_files": 4,
            "created_at": "2026-08-01T00:00:00Z",
        }
        old = classify_pr(pr, "deadbeef", now)
        self.assertEqual(old["age_bucket"], "ancient")
        self.assertEqual(old["lane"], "CANDIDATE")
        self.assertNotIn("ancient-no-auto-promote", old["reasons"])

    def test_age_bucket_changes_do_not_change_lane(self):
        pr = {
            "number": 901,
            "title": "feat(ops): age must not be a state transition",
            "user": {"login": "timerloggedout-spec"},
            "draft": False,
            "base": {"ref": "master", "sha": "a"},
            "head": {"ref": "b", "sha": "c"},
            "mergeable_state": "clean",
            "changed_files": 4,
            "created_at": "2026-11-04T00:00:00Z",
        }
        fresh = classify_pr(pr, "deadbeef", datetime(2026, 11, 5, tzinfo=timezone.utc))
        ancient = classify_pr(pr, "deadbeef", datetime(2027, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(fresh["lane"], ancient["lane"])
        self.assertEqual(fresh["lane"], "CANDIDATE")
        self.assertNotEqual(fresh["age_bucket"], ancient["age_bucket"])

    def test_clean_fresh_is_candidate(self):
        now = datetime(2026, 9, 25, tzinfo=timezone.utc)
        row = classify_pr(
            {
                "number": 900,
                "title": "feat(ops): thin slice",
                "user": {"login": "timerloggedout-spec"},
                "draft": False,
                "base": {"ref": "master", "sha": "a"},
                "head": {"ref": "b", "sha": "c"},
                "mergeable_state": "clean",
                "changed_files": 4,
                "created_at": "2026-09-24T00:00:00Z",
            },
            "deadbeef",
            now,
        )
        self.assertEqual(row["lane"], "CANDIDATE")
        self.assertNotIn(row["lane"], {"HOLD", "WAIT", "OBSERVE"})


if __name__ == "__main__":
    unittest.main()
