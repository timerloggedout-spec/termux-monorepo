"""Tribute audit revisions (whole corpus, versioned), census completeness, merge attribution. Offline."""
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.ci import tribute_audit_rev as ar
from scripts.ci import tribute_outcomes as to

FX = Path(__file__).resolve().parent / "fixtures" / "tribute_outcomes"
CENSUS = json.loads((FX / "census_2026-11-12.json").read_text(encoding="utf-8"))
ATTR = json.loads((FX / "real_merge_attribution_2026-11-12.json").read_text(encoding="utf-8"))
DECISIONS = to.read_jsonl([str(FX / "s1_decisions_2026-10-22.jsonl")])
NOW = datetime(2026, 11, 12, 9, 35, tzinfo=timezone.utc)


def census_with_attribution():
    out = []
    for pr in CENSUS:
        pr = dict(pr)
        pr.update({k: v for k, v in ATTR.get(pr["html_url"], {}).items() if not k.startswith("_")})
        out.append(pr)
    return out


class Census(unittest.TestCase):
    def test_verified_census_totals(self):
        merged = sum(1 for p in CENSUS if p.get("merged_at"))
        closed = sum(1 for p in CENSUS if p["state"] == "closed" and not p.get("merged_at"))
        open_ = sum(1 for p in CENSUS if p["state"] == "open")
        chk = to.census_assert(127, {"merged": merged, "closed_unmerged": closed, "open": open_})
        self.assertTrue(chk["ok"], chk)
        self.assertEqual((merged, closed, open_), (20, 99, 8))

    def test_mismatch_fails_gate(self):
        chk = to.census_assert(127, {"merged": 20, "closed_unmerged": 99, "open": 7})
        self.assertFalse(chk["ok"])
        rep = to.build(census_with_attribution(), NOW, census_check=chk)
        self.assertEqual(to.check(rep), 1)

    def test_paginates_past_one_page(self):
        pool = [{"html_url": f"u{i}"} for i in range(250)]
        calls = []

        def fetch(path):
            calls.append(path)
            page = int(path.split("page=")[2].split("&")[0])
            return {"total_count": len(pool), "items": pool[(page - 1) * 100: page * 100]}
        items, total = to.search_all("is:pr x", fetch=fetch)
        self.assertEqual((len(items), total, len(calls)), (250, 250, 3))

    def test_splits_by_created_range_over_search_cap(self):
        # 1500 hits: one per day from 2020-01-01; each created: range returns only its own days.
        from datetime import date, timedelta
        days = [(date(2020, 1, 1) + timedelta(days=i)).isoformat() for i in range(1500)]

        def fetch(path):
            from urllib.parse import unquote
            q = unquote(path.split("q=")[1].split("&")[0])
            page = int(path.split("page=")[2].split("&")[0])
            sel = days
            if "created:" in q:
                a, b = q.split("created:")[1].split("..")
                sel = [d for d in days if a <= d <= b]
            vis = sel[:1000]  # the search API never returns past 1000
            return {"total_count": len(sel), "items": [{"html_url": d} for d in vis[(page - 1) * 100: page * 100]]}
        items, total = to.search_all("is:pr x", fetch=fetch, lo="2020-01-01", hi="2024-12-31")
        self.assertEqual(total, 1500)
        self.assertEqual(len({i["html_url"] for i in items}), 1500)


class Attribution(unittest.TestCase):
    def setUp(self):
        self.rep = to.build(census_with_attribution(), NOW, decisions=DECISIONS)
        self.by = {a["url"]: a for a in self.rep["real_merge_attribution"]}

    def test_two_real_merges_attributed(self):
        self.assertEqual(len(self.by), 2)
        g = self.by["https://github.com/xtekky/gpt4free/pull/3541"]
        z = self.by["https://github.com/vedantnimbarte/zero/pull/81"]
        self.assertEqual((g["merged_by"], g["merger_association"], g["lane_produced"], g["collaborator_integration"]),
                         ("hlohaus", "COLLABORATOR", False, False))
        self.assertEqual(g["attribution_class"], "maintainer_accept_manual")
        self.assertEqual((z["merged_by"], z["merger_association"], z["lane_produced"], z["collaborator_integration"]),
                         ("vedantnimbarte", "OWNER", True, False))
        self.assertEqual(z["attribution_class"], "maintainer_accept_lane")

    def test_collaborator_integration_when_we_are_collaborator(self):
        pr = {"html_url": "https://github.com/o/r/pull/1", "repo": "o/r", "title": "x", "state": "closed",
              "created_at": "2026-10-01T00:00:00Z", "closed_at": "2026-10-02T00:00:00Z", "merged_at": "2026-10-02T00:00:00Z",
              "merged_by": "friend", "author_association": "COLLABORATOR", "files": [{"filename": "src/a.py"}]}
        a = to.attribution(pr, to.classify(pr))
        self.assertTrue(a["collaborator_integration"])
        self.assertEqual(a["attribution_class"], "collaborator_integration")

    def test_self_org_is_self_merge_even_without_merged_by(self):
        pr = {"html_url": "https://github.com/Research-Astute/x/pull/1", "repo": "Research-Astute/x", "state": "closed",
              "merged_at": "2026-08-21T00:00:00Z", "files": [{"filename": "a.py"}]}
        self.assertEqual(to.classify(pr), "self_merge")


class Revisions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "revs"
        self.rep = to.build(census_with_attribution(), NOW, decisions=DECISIONS)
        self.items = ar.corpus_items(self.rep, DECISIONS)

    def tearDown(self):
        self.tmp.cleanup()

    def test_rev1_is_whole_corpus(self):
        rev = ar.make_rev(self.items, NOW, self.dir, ar.slo_primary(self.items, NOW))
        self.assertEqual(rev["rev"], 1)
        self.assertEqual(rev["counts_by_kind"]["pr"], 127)
        c = rev["counts"]
        self.assertEqual((c["real_merge"], c["stake_merge"], c["self_merge"], c["closed_unmerged"], c["open"]), (2, 14, 4, 99, 8))
        self.assertGreater(rev["counts_by_kind"]["issue"], 0)
        self.assertEqual(rev["diff"]["n_new"], rev["corpus_size"])
        self.assertTrue((self.dir / "rev-0001.json").exists())
        self.assertTrue(rev["hash"].startswith("sha256:"))

    def test_hash_is_stable_and_rerun_is_idempotent(self):
        r1 = ar.make_rev(self.items, NOW, self.dir, ar.slo_primary(self.items, NOW))
        r1b = ar.make_rev(list(reversed(self.items)), NOW, self.dir, ar.slo_primary(self.items, NOW))
        self.assertEqual(r1b["rev"], 1)
        self.assertEqual(r1["hash"], r1b["hash"])
        self.assertEqual(len(json.loads((self.dir / "index.json").read_text())["revs"]), 1)

    def test_rev2_diff_reports_changes_and_count_delta(self):
        ar.make_rev(self.items, NOW, self.dir, ar.slo_primary(self.items, NOW))
        items2 = [dict(i) for i in self.items]
        opened = next(i for i in items2 if i["kind"] == "pr" and i["class"] == "open")
        opened.update({"class": "closed_unmerged", "state": "closed"})
        items2.append({"url": "https://github.com/o/r/pull/999", "kind": "pr", "repo": "o/r", "class": "open",
                       "state": "open", "at": None, "created_at": "2026-11-12T09:00:00Z", "attribution_class": None})
        r2 = ar.make_rev(items2, NOW, self.dir, ar.slo_primary(items2, NOW))
        self.assertEqual(r2["rev"], 2)
        self.assertEqual(r2["prev_rev"], 1)
        self.assertEqual(r2["diff"]["n_new"], 1)
        self.assertEqual(r2["diff"]["n_changed"], 1)
        self.assertEqual(r2["diff"]["counts_delta"], {"closed_unmerged": 1})
        self.assertTrue((self.dir / "rev-0001.json").exists() and (self.dir / "rev-0002.json").exists())

    def test_append_only_refuses_overwrite(self):
        ar.make_rev(self.items, NOW, self.dir, ar.slo_primary(self.items, NOW))
        (self.dir / "index.json").write_text(json.dumps({"schema": "x", "genesis": ar.GENESIS, "revs": []}))
        with self.assertRaises(SystemExit):
            ar.make_rev(self.items, NOW, self.dir, ar.slo_primary(self.items, NOW))

    def test_status_merge(self):
        rev = ar.make_rev(self.items, NOW, self.dir, ar.slo_primary(self.items, NOW))
        st = Path(self.tmp.name) / "status.json"
        st.write_text(json.dumps({"receipts": 1}))
        ar.merge_into(st, rev)
        doc = json.loads(st.read_text())
        self.assertEqual(doc["receipts"], 1)
        self.assertEqual(doc["audit_rev"]["rev"], 1)
        self.assertIn("counts_delta", doc["audit_rev"]["delta"])


class PrimarySlo(unittest.TestCase):
    @staticmethod
    def pr(i, cls, created, at=None, att=None):
        return {"url": f"https://github.com/o/r/pull/{i}", "kind": "pr", "repo": "o/r", "class": cls,
                "state": "open", "at": at, "created_at": created, "attribution_class": att}

    def test_whole_corpus_rate_fails(self):
        items = ar.corpus_items(to.build(census_with_attribution(), NOW), [])
        s = ar.slo_primary(items, NOW)
        self.assertEqual(s["status"], "FAIL")
        self.assertIn("corpus_real_rate_below", [f["code"] for f in s["failures"]])
        self.assertEqual(s["corpus"]["real_merges_lane"], 1)
        self.assertIn("real_merges_not_lane_produced", [w["code"] for w in s["warnings"]])

    def test_paused_attempts_do_not_count(self):
        real = self.pr(0, "real_merge", "2026-10-01T00:00:00Z", at="2026-10-02T00:00:00Z", att="maintainer_accept_lane")
        paused = [self.pr(i, "closed_unmerged", f"2026-10-{22 + i % 9:02d}T12:00:00Z") for i in range(1, 30)]
        s = ar.slo_primary([real] + paused, datetime(2026, 11, 1, tzinfo=timezone.utc), max_attempts_since_real=5, min_decided=999)
        self.assertEqual(s["recency"]["active_attempts_since_real"], 0)
        self.assertNotIn("attempt_drought", [f["code"] for f in s["failures"]])

    def test_starved_is_not_success_nor_failure(self):
        real = self.pr(0, "real_merge", "2026-10-01T00:00:00Z", at="2026-10-02T00:00:00Z", att="maintainer_accept_lane")
        s = ar.slo_primary([real], datetime(2026, 11, 12, tzinfo=timezone.utc), min_decided=999)
        self.assertEqual(s["activity_state"], "starved")
        self.assertEqual(s["status"], "WARN")
        self.assertEqual(s["failures"], [])

    def test_active_attempt_drought_fails(self):
        real = self.pr(0, "real_merge", "2026-09-20T00:00:00Z", at="2026-09-21T00:00:00Z", att="maintainer_accept_lane")
        tries = [self.pr(i, "closed_unmerged", f"2026-11-{1 + i % 10:02d}T12:00:00Z") for i in range(1, 8)]
        s = ar.slo_primary([real] + tries, datetime(2026, 11, 12, tzinfo=timezone.utc), max_attempts_since_real=5, min_decided=999)
        self.assertIn("attempt_drought", [f["code"] for f in s["failures"]])
        self.assertEqual(s["activity_state"], "active")


if __name__ == "__main__":
    unittest.main()
