import unittest

from archwiz.context_relationships.build_index import advance_history_coverage


class HistoryCoverageLedgerTests(unittest.TestCase):
    def window(self, start, next_page, issues_complete, pulls_complete, issue_count, pull_count):
        return {
            "start_page": start,
            "next_start_page": next_page,
            "limit_per_family": 100,
            "issue_count": issue_count,
            "pull_request_count": pull_count,
            "issues_complete": issues_complete,
            "pull_requests_complete": pulls_complete,
        }

    def test_page_one_starts_a_partial_contiguous_ledger(self):
        result = advance_history_coverage(
            None, self.window(1, 2, False, False, 100, 100), "a" * 40, "2026-10-24T00:00:00Z"
        )
        self.assertEqual(result["status"], "PARTIAL_CONTINUATION_REQUIRED")
        self.assertEqual(result["next_start_page"], 2)
        self.assertEqual([item["start_page"] for item in result["windows"]], [1])

    def test_expected_continuation_closes_the_ledger(self):
        first = advance_history_coverage(
            None, self.window(1, 2, False, False, 100, 100), "a" * 40, "2026-10-24T00:00:00Z"
        )
        result = advance_history_coverage(
            first, self.window(2, None, True, True, 12, 0), "b" * 40, "2026-10-24T00:01:00Z"
        )
        self.assertEqual(result["status"], "COMPLETE")
        self.assertIsNone(result["next_start_page"])
        self.assertEqual([item["start_page"] for item in result["windows"]], [1, 2])

    def test_unproven_late_page_restarts_from_page_one(self):
        result = advance_history_coverage(
            None, self.window(13, None, True, True, 0, 0), "c" * 40, "2026-10-24T00:02:00Z"
        )
        self.assertEqual(result["status"], "UNVERIFIED")
        self.assertEqual(result["next_start_page"], 1)
        self.assertEqual(result["windows"][0]["start_page"], 13)


if __name__ == "__main__":
    unittest.main()
