"""Honest Tribute outcome census + SLO: zero real merges is a FAILURE, never '0 failures'."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.ci import tribute_outcomes as to

FX = Path(__file__).resolve().parent / "fixtures" / "tribute_outcomes"
CENSUS = json.loads((FX / "census_2026-11-12.json").read_text(encoding="utf-8"))
DECISIONS = to.read_jsonl([str(FX / "s1_decisions_2026-10-22.jsonl")])
NOW = datetime(2026, 11, 12, 7, 45, tzinfo=timezone.utc)
STAKE = [{"filename": ".github/help-wanted-lane-stake.md", "additions": 8}]
REAL = [{"filename": "src/x.rs", "additions": 8}]


def pr(**kw):
    base = {"html_url": "https://github.com/o/r/pull/1", "repo": "o/r", "title": "t", "state": "closed",
            "created_at": "2026-11-01T00:00:00Z", "closed_at": "2026-11-05T00:00:00Z", "merged_at": None}
    base.update(kw)
    return base


class Classify(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(to.classify(pr(merged_at="2026-11-05T00:00:00Z", merged_by="m", files=REAL)), "real_merge")
        self.assertEqual(to.classify(pr(merged_at="2026-11-05T00:00:00Z", merged_by="m", files=STAKE)), "stake_merge")
        self.assertEqual(to.classify(pr(merged_at="2026-11-05T00:00:00Z", merged_by="timerloggedout-spec", files=REAL)), "self_merge")
        self.assertEqual(to.classify(pr()), "closed_unmerged")
        self.assertEqual(to.classify(pr(state="open", closed_at=None)), "open")

    def test_title_fallback_when_files_unread(self):
        self.assertEqual(to.classify(pr(merged_at="2026-11-05T00:00:00Z", title="help-wanted: stake + contribute for #5")), "stake_merge")


class Slo(unittest.TestCase):
    def test_zero_real_merges_is_failure(self):
        prs = [pr(html_url=f"https://github.com/o/r/pull/{i}", merged_at="2026-11-05T00:00:00Z", merged_by="m", files=STAKE)
               for i in range(3)] + [pr(html_url=f"https://github.com/o/r/pull/9{i}") for i in range(4)]
        rep = to.build(prs, NOW)
        self.assertEqual(rep["slo"]["status"], "FAIL")
        codes = {f["code"] for f in rep["slo"]["failures"]}
        self.assertIn("zero_real_merges", codes)
        self.assertIn("real_merge_drought", codes)
        self.assertEqual(rep["windows"]["30d"]["stake_only_merges"], 3)
        self.assertEqual(rep["windows"]["30d"]["weighted_score"], -4.0)  # stake = 0, closed = -1
        self.assertGreater(rep["slo"]["outcome_failures"], 0)  # never "0 failures"
        self.assertEqual(to.check(rep), 1)

    def test_healthy_lane_passes(self):
        prs = [pr(html_url=f"https://github.com/o/r/pull/{i}", merged_at="2026-11-08T00:00:00Z", merged_by="m", files=REAL)
               for i in range(3)] + [pr(html_url="https://github.com/o/r/pull/99", state="open", closed_at=None)]
        rep = to.build(prs, NOW)
        self.assertEqual(rep["slo"]["status"], "OK")
        self.assertEqual(to.check(rep), 0)

    def test_stake_merges_never_count_as_ok(self):
        prs = [pr(html_url="https://github.com/o/r/pull/1", merged_at="2026-11-08T00:00:00Z", merged_by="m", files=REAL),
               pr(html_url="https://github.com/o/r/pull/2", merged_at="2026-11-08T00:00:00Z", merged_by="m", files=STAKE)]
        rep = to.build(prs, NOW)
        self.assertEqual(rep["slo"]["status"], "WARN")
        self.assertEqual(rep["windows"]["30d"]["real_merges"], 1)


class RealCensus(unittest.TestCase):
    """Snapshot of the live search census taken 2026-11-12 07:45 UTC."""

    def setUp(self):
        self.rep = to.build(CENSUS, NOW, decisions=DECISIONS)

    def test_totals(self):
        t = self.rep["totals"]
        self.assertEqual((t["real_merges"], t["stake_only_merges"], t["self_merges_excluded"], t["closed_unmerged"], t["open"]),
                         (2, 14, 4, 99, 8))

    def test_window_30d(self):
        w = self.rep["windows"]["30d"]
        self.assertEqual((w["real_merges"], w["stake_only_merges"], w["closed_unmerged"]), (2, 5, 51))
        self.assertEqual(self.rep["windows"]["14d"]["real_merges"], 0)

    def test_reports_failure(self):
        self.assertEqual(self.rep["slo"]["status"], "FAIL")
        self.assertIn("real_merge_rate_below", {f["code"] for f in self.rep["slo"]["failures"]})

    def test_system1_counts(self):
        s1 = self.rep["system1"]
        self.assertEqual(s1["threads"], 208)
        self.assertGreater(s1["yielded"], 0)
        self.assertGreater(s1["retired"], 0)

    def test_merge_into_status_keeps_existing_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "status.json"
            p.write_text(json.dumps({"outcomes": {"actioned": 5, "skipped": 9}, "tributes": []}))
            to.merge_into(p, self.rep)
            doc = json.loads(p.read_text())
            self.assertEqual(doc["outcomes"], {"actioned": 5, "skipped": 9})
            self.assertEqual(doc["tribute_outcomes"]["status"], "FAIL")
            self.assertEqual(doc["tribute_outcomes"]["merged_real"], 2)
            self.assertEqual(doc["tribute_outcomes"]["closed_unmerged"], 51)
            self.assertNotIn("prs", doc["outcome_slo"])

    def test_cli_offline_check_exits_1(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "o.json"
            rc = to.main(["--census", str(FX / "census_2026-11-12.json"), "--now", "2026-11-12T07:45:00Z",
                          "--out", str(out), "--dashboard", "", "--md", str(Path(d) / "o.md"), "--check"])
            self.assertEqual(rc, 1)
            self.assertEqual(to.main(["--check-file", str(out)]), 1)


class DashboardShowsOutcomes(unittest.TestCase):
    def test_index_reads_tribute_outcomes(self):
        html = (Path(__file__).resolve().parents[1] / "apps" / "tribute-dashboard" / "index.html").read_text(encoding="utf-8")
        for needle in ("tribute_outcomes", "Real merges", "Closed unmerged", "Stake-only merges", "Yielded", "Retired"):
            self.assertIn(needle, html)


if __name__ == "__main__":
    unittest.main()
