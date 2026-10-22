"""Unit tests for deepcli._v1_pr_rollup (PR triage/merge classifier).

Run: python3 -m unittest deepcli.tests.test_pr_rollup  (from repo root)
or:  python3 tests/test_pr_rollup.py
"""

import os
import sys
import unittest

# Bootstrap: make the package importable from a worktree checkout.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)  # repo root (contains deepcli/ package dir)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from deepcli import _v1_pr_rollup as pr  # noqa: E402


class TestClassify(unittest.TestCase):
    def test_clean_approved_is_merge(self):
        sig = pr.PRSignals(
            number=1,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="success",
            review_decision="approved",
        )
        c = pr.classify(sig)
        self.assertEqual(c.bucket, "merge")
        self.assertTrue(c.actionable)

    def test_trivial_diff_merges_without_review(self):
        sig = pr.PRSignals(
            number=2,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="success",
            additions=5,
            deletions=3,
            changed_files=1,
        )
        c = pr.classify(sig)
        self.assertEqual(c.bucket, "merge")
        self.assertIn("trivial diff", c.reasons)

    def test_large_unreviewed_is_recheck(self):
        sig = pr.PRSignals(
            number=3,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="success",
            additions=400,
            deletions=200,
            changed_files=25,
        )
        c = pr.classify(sig)
        self.assertEqual(c.bucket, "recheck")
        self.assertFalse(c.actionable)

    def test_conflict_is_needs_work(self):
        sig = pr.PRSignals(number=4, mergeable="conflicting")
        self.assertEqual(pr.classify(sig).bucket, "needs_work")

    def test_dirty_merge_state_is_needs_work(self):
        sig = pr.PRSignals(number=5, mergeable="mergeable", merge_state="dirty")
        self.assertEqual(pr.classify(sig).bucket, "needs_work")

    def test_failing_ci_is_needs_work(self):
        sig = pr.PRSignals(
            number=6,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="failure",
            ci_failing=2,
            review_decision="approved",
        )
        c = pr.classify(sig)
        self.assertEqual(c.bucket, "needs_work")
        self.assertIn("ci failing", c.reasons[0])

    def test_changes_requested_is_needs_work(self):
        sig = pr.PRSignals(
            number=7,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="success",
            review_decision="changes_requested",
        )
        self.assertEqual(pr.classify(sig).bucket, "needs_work")

    def test_behind_is_rebase(self):
        sig = pr.PRSignals(
            number=8,
            mergeable="mergeable",
            merge_state="behind",
            ci_state="success",
            review_decision="approved",
        )
        c = pr.classify(sig)
        self.assertEqual(c.bucket, "rebase")
        self.assertTrue(c.actionable)

    def test_pending_ci_is_recheck(self):
        sig = pr.PRSignals(
            number=9,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="pending",
            ci_pending=3,
            review_decision="approved",
        )
        self.assertEqual(pr.classify(sig).bucket, "recheck")

    def test_unknown_mergeable_is_recheck(self):
        sig = pr.PRSignals(
            number=10,
            mergeable="unknown",
            merge_state="clean",
            ci_state="success",
            review_decision="approved",
        )
        self.assertEqual(pr.classify(sig).bucket, "recheck")

    def test_draft_is_skip(self):
        sig = pr.PRSignals(
            number=11,
            draft=True,
            mergeable="mergeable",
            merge_state="clean",
            ci_state="success",
            review_decision="approved",
        )
        self.assertEqual(pr.classify(sig).bucket, "skip")

    def test_default_signals_do_not_crash(self):
        # All-default PRSignals must be classified without error.
        c = pr.classify(pr.PRSignals())
        self.assertIn(c.bucket, pr.BUCKET_ORDER)

    def test_bucket_is_always_valid(self):
        for mergeable in ("mergeable", "conflicting", "unknown", "", "weird"):
            for ci in ("success", "failure", "pending", "unknown", "garbage"):
                sig = pr.PRSignals(number=1, mergeable=mergeable, ci_state=ci)
                self.assertIn(pr.classify(sig).bucket, pr.BUCKET_ORDER)

    def test_merge_requires_all_gates(self):
        """Invariant: merge never wins if any gate fails."""
        # approved but conflicting
        self.assertNotEqual(
            pr.classify(
                pr.PRSignals(
                    mergeable="conflicting",
                    ci_state="success",
                    merge_state="clean",
                    review_decision="approved",
                )
            ).bucket,
            "merge",
        )
        # approved, clean, but CI failing
        self.assertNotEqual(
            pr.classify(
                pr.PRSignals(
                    mergeable="mergeable",
                    ci_state="failure",
                    merge_state="clean",
                    review_decision="approved",
                )
            ).bucket,
            "merge",
        )
        # approved, clean, green, but mergeability unknown
        self.assertNotEqual(
            pr.classify(
                pr.PRSignals(
                    mergeable="unknown",
                    ci_state="success",
                    merge_state="clean",
                    review_decision="approved",
                )
            ).bucket,
            "merge",
        )


class TestFromGh(unittest.TestCase):
    def test_status_rollup_all_success(self):
        data = {
            "number": 100,
            "isDraft": False,
            "mergeable": "MERGEABLE",
            "mergeStateStatus": "CLEAN",
            "reviewDecision": "APPROVED",
            "statusCheckRollup": [
                {"conclusion": "SUCCESS", "status": "COMPLETED"},
                {"state": "success"},
            ],
        }
        sig = pr.PRSignals.from_gh(data)
        self.assertEqual(sig.ci_state, "success")
        self.assertEqual(sig.mergeable, "mergeable")
        self.assertEqual(sig.merge_state, "clean")
        self.assertEqual(pr.classify(sig).bucket, "merge")

    def test_status_rollup_mixed_failure(self):
        data = {
            "number": 101,
            "mergeable": "MERGEABLE",
            "statusCheckRollup": [
                {"conclusion": "SUCCESS"},
                {"conclusion": "FAILURE"},
            ],
        }
        sig = pr.PRSignals.from_gh(data)
        self.assertEqual(sig.ci_state, "failure")
        self.assertEqual(sig.ci_failing, 1)
        self.assertEqual(pr.classify(sig).bucket, "needs_work")

    def test_status_rollup_pending(self):
        data = {"number": 102, "statusCheckRollup": [{"status": "IN_PROGRESS"}]}
        sig = pr.PRSignals.from_gh(data)
        self.assertEqual(sig.ci_state, "pending")
        self.assertEqual(sig.ci_pending, 1)

    def test_status_rollup_empty_is_unknown(self):
        sig = pr.PRSignals.from_gh({"number": 103})
        self.assertEqual(sig.ci_state, "unknown")

    def test_comments_list_and_int(self):
        self.assertEqual(pr.PRSignals.from_gh({"comments": [1, 2, 3]}).comments, 3)
        self.assertEqual(pr.PRSignals.from_gh({"comments": 7}).comments, 7)
        self.assertEqual(pr.PRSignals.from_gh({"comments": "5"}).comments, 5)

    def test_is_draft_string_and_bool(self):
        self.assertTrue(pr.PRSignals.from_gh({"isDraft": True}).draft)
        self.assertTrue(pr.PRSignals.from_gh({"isDraft": "true"}).draft)
        self.assertFalse(pr.PRSignals.from_gh({"isDraft": 0}).draft)

    def test_malformed_checks_ignored(self):
        data = {
            "number": 104,
            "statusCheckRollup": [None, "x", {"conclusion": "SUCCESS"}],
        }
        sig = pr.PRSignals.from_gh(data)
        self.assertEqual(sig.ci_state, "success")

    def test_bad_int_coercion(self):
        sig = pr.PRSignals.from_gh({"number": "nope", "additions": None})
        self.assertEqual(sig.number, 0)
        self.assertEqual(sig.additions, 0)


class TestRollup(unittest.TestCase):
    def test_counts_and_actionable_order(self):
        sigs = [
            pr.PRSignals(
                number=1,
                mergeable="mergeable",
                merge_state="clean",
                ci_state="success",
                review_decision="approved",
            ),
            pr.PRSignals(
                number=2,
                mergeable="mergeable",
                merge_state="behind",
                ci_state="success",
                review_decision="approved",
            ),
            pr.PRSignals(number=3, mergeable="conflicting"),
            pr.PRSignals(number=4, draft=True),
            pr.PRSignals(
                number=5, mergeable="mergeable", merge_state="clean", ci_state="pending"
            ),
        ]
        out = pr.rollup(sigs)
        self.assertEqual(out["counts"]["merge"], 1)
        self.assertEqual(out["counts"]["rebase"], 1)
        self.assertEqual(out["counts"]["needs_work"], 1)
        self.assertEqual(out["counts"]["skip"], 1)
        self.assertEqual(out["counts"]["recheck"], 1)
        # merge before rebase in actionable ordering
        self.assertEqual(out["actionable"], [1, 2])

    def test_every_input_accounted_for_once(self):
        sigs = [pr.PRSignals(number=n, mergeable="unknown") for n in range(1, 11)]
        out = pr.rollup(sigs)
        total = sum(out["counts"].values())
        self.assertEqual(total, len(sigs))
        seen = [x["number"] for b in pr.BUCKET_ORDER for x in out["buckets"][b]]
        self.assertEqual(sorted(seen), list(range(1, 11)))

    def test_duplicate_numbers_deduped(self):
        sigs = [
            pr.PRSignals(number=7, mergeable="conflicting"),
            pr.PRSignals(
                number=7,
                mergeable="mergeable",
                merge_state="clean",
                ci_state="success",
                review_decision="approved",
            ),
        ]
        out = pr.rollup(sigs)
        self.assertEqual(sum(out["counts"].values()), 1)

    def test_empty_input(self):
        out = pr.rollup([])
        self.assertEqual(sum(out["counts"].values()), 0)
        self.assertEqual(out["actionable"], [])

    def test_bucket_keys_stable(self):
        out = pr.rollup([])
        self.assertEqual(set(out["counts"].keys()), set(pr.BUCKET_ORDER))
        self.assertEqual(set(out["buckets"].keys()), set(pr.BUCKET_ORDER))


class TestClassificationSerialization(unittest.TestCase):
    def test_to_dict_roundtrip(self):
        c = pr.classify(pr.PRSignals(number=1, mergeable="conflicting"))
        d = c.to_dict()
        self.assertEqual(d["number"], 1)
        self.assertEqual(d["bucket"], "needs_work")
        self.assertIsInstance(d["reasons"], list)
        self.assertFalse(d["actionable"])


if __name__ == "__main__":
    unittest.main()
