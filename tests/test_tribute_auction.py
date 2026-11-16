"""Tribute claim auction: ante + bid, deterministic, offline (no LLM, no network)."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.ci import tribute_auction as ta
from scripts.ci import tribute_system1 as s1

FX = Path(__file__).resolve().parent / "fixtures" / "tribute_auction"
POOL = ta.load_pool(FX / "pool.json")
NOW = datetime(2026, 11, 12, 8, 0, tzinfo=timezone.utc)
EASY = {"url": "https://github.com/acme/web/issues/5", "repo": "https://github.com/acme/web",
        "labels": ["good first issue", "documentation"], "score_components": {"body_clarity": 15},
        "comments": 1, "language": "TypeScript"}
HARD = {"url": "https://github.com/acme/chain/issues/9", "repo": "https://github.com/acme/chain",
        "labels": ["help wanted"], "score_components": {"body_clarity": 5}, "comments": 20, "language": "Rust"}
OK = {"eligible": True, "reasons": []}


def won(issue=EASY, at=NOW, winner=None, ante=None):
    r = ta.run_auction(issue, POOL, ta.new_state(POOL), OK, {}, at)
    if winner:
        r["winner"], r["ante"] = winner, ante or r["ante"]
    return r


class Pool(unittest.TestCase):
    def test_text_only_dedup_sorted(self):
        ids = [e["id"] for e in POOL]
        self.assertEqual(ids, sorted(set(ids)))
        self.assertFalse(any("Image" in i or "Flux" in i for i in ids))
        self.assertTrue(any(i.startswith("KiloCode/") for i in ids))

    def test_real_pool_file_loads(self):
        self.assertGreater(len(ta.load_pool()), 10)


class Auction(unittest.TestCase):
    def test_deterministic(self):
        a = ta.run_auction(EASY, POOL, ta.new_state(POOL), OK, {}, NOW)
        b = ta.run_auction(EASY, POOL, ta.new_state(POOL), OK, {}, NOW)
        self.assertEqual(a, b)

    def test_easy_issue_has_a_winner_with_ante(self):
        r = ta.run_auction(EASY, POOL, ta.new_state(POOL), OK, {}, NOW)
        self.assertEqual(r["result"], "won")
        self.assertGreater(r["ev"], ta.RESERVE_EV)
        self.assertGreater(r["ante"], 0)
        self.assertEqual(r["winner"], r["bids"][0]["endpoint"])
        self.assertEqual([b["ev"] for b in r["bids"]], sorted((b["ev"] for b in r["bids"]), reverse=True))

    def test_code_endpoint_beats_search_wrapper(self):
        r = ta.run_auction(EASY, POOL, ta.new_state(POOL), OK, {}, NOW)
        self.assertNotIn("Perplexity", r["winner"])

    def test_hard_issue_below_reserve_no_claim(self):
        r = ta.run_auction(HARD, POOL, ta.new_state(POOL), OK, {}, NOW)
        self.assertEqual(r["result"], "below_reserve")
        self.assertIsNone(r["winner"])

    def test_only_preflight_eligible_issues(self):
        r = ta.run_auction(EASY, POOL, ta.new_state(POOL), {"eligible": False, "reasons": ["claimed_by:x"]}, {}, NOW)
        self.assertEqual((r["result"], r["winner"], r["bids"]), ("not_eligible", None, []))
        self.assertEqual(r["reasons"], ["claimed_by:x"])

    def test_program_issue_refused(self):
        r = ta.run_auction(dict(EASY, labels=["good first issue", "Stellar Wave"]), POOL, ta.new_state(POOL), OK, {}, NOW)
        self.assertEqual(r["reasons"], ["program_assigned_issue"])

    def test_repo_cooldown_from_spam_flag(self):
        rf = ta.repo_priors([{"subject": {"url": "u", "repo": "acme/web"}, "primary": "hostile_spam_flag",
                              "delphi_signal": {"repo": "acme/web", "outcome": "hostile_spam_flag", "weight": -1.0}}])
        self.assertEqual(rf["acme/web"], 0.0)
        r = ta.run_auction(EASY, POOL, ta.new_state(POOL), OK, rf, NOW)
        self.assertEqual(r["reasons"], ["repo_cooldown"])

    def test_stake_merge_never_raises_repo_prior(self):
        rf = ta.repo_priors([], [{"repo": "acme/web", "class": "stake_merge"}])
        self.assertEqual(rf["acme/web"], 1.0)
        rf2 = ta.repo_priors([], [{"repo": "acme/web", "class": "closed_unmerged"}])
        self.assertLess(rf2["acme/web"], 1.0)

    def test_no_credit_no_seat(self):
        st = ta.new_state(POOL)
        st["last_refill"] = ta._iso(NOW)
        for e in st["credits"]:
            st["credits"][e] = 1.0
        r = ta.run_auction(EASY, POOL, st, OK, {}, NOW)
        self.assertEqual(r["result"], "no_bidders")

    def test_quota_remaining_lowers_bid(self):
        st = ta.new_state(POOL)
        st["last_refill"] = ta._iso(NOW)
        top = ta.run_auction(EASY, POOL, st, OK, {}, NOW)["winner"]
        st["credits"][top] = 20.0
        b_low = ta.bid(next(e for e in POOL if e["id"] == top), EASY, st, 1.0)
        b_full = ta.bid(next(e for e in POOL if e["id"] == top), EASY, ta.new_state(POOL), 1.0)
        self.assertLess(b_low["p_real_merge"], b_full["p_real_merge"])

    def test_track_record_moves_bids(self):
        st = ta.new_state(POOL)
        e = POOL[0]
        base = ta.bid(e, EASY, st, 1.0)["p_real_merge"]
        st["record"][e["id"]] = {"wins": 4, "real_merges": 0, "forfeits": 4, "refunds": 0}
        self.assertLess(ta.bid(e, EASY, st, 1.0)["p_real_merge"], base)
        st["record"][e["id"]] = {"wins": 4, "real_merges": 4, "forfeits": 0, "refunds": 0}
        self.assertGreater(ta.bid(e, EASY, st, 1.0)["p_real_merge"], base)


class ClaimGate(unittest.TestCase):
    def test_winner_needs_real_patch(self):
        r = won()
        self.assertEqual(ta.claim_gate(r, None, s1.preflight_pr)["reason"], "no_patch")
        stake = [{"filename": ".github/help-wanted-lane-stake.md", "additions": 8}]
        self.assertEqual(ta.claim_gate(r, stake, s1.preflight_pr)["reason"], "placeholder_patch")
        real = [{"filename": "docs/setup.md", "additions": 30, "patch": "+Install with `npm ci` then run `npm test`.\n" * 3},
                {"filename": "src/cli.ts", "additions": 12, "patch": "+export const x = 1;"}]
        self.assertTrue(ta.claim_gate(r, real, s1.preflight_pr)["claim"])

    def test_no_claim_when_not_won(self):
        r = ta.run_auction(HARD, POOL, ta.new_state(POOL), OK, {}, NOW)
        self.assertFalse(ta.claim_gate(r, [{"filename": "src/a.rs", "additions": 40}], s1.preflight_pr)["claim"])


class Settlement(unittest.TestCase):
    def census(self, cls, title="Fix #5: docs", created="2026-11-13T00:00:00Z"):
        return [{"repo": "acme/web", "title": title, "class": cls, "created_at": created, "at": created}]

    def settle(self, receipts, census, now=NOW + timedelta(days=3)):
        return ta.replay(receipts, census, POOL, now)

    def test_real_merge_returns_ante_plus_reward(self):
        r = won()
        led = self.settle([r, {"kind": "claim", "issue": r["issue"]}], self.census("real_merge"))
        s = led["settlements"][0]
        self.assertEqual(s["outcome"], "real_merge")
        self.assertEqual(s["returned"], r["ante"] + ta.REWARD)
        self.assertEqual(led["delphi_signals"][0]["weight"], 1.0)
        self.assertEqual(led["leaderboard"][0]["real_merges"], 1)

    def test_closed_unmerged_and_stake_forfeit(self):
        for cls in ("closed_unmerged", "stake_merge"):
            r = won()
            led = self.settle([r, {"kind": "claim", "issue": r["issue"]}], self.census(cls))
            s = led["settlements"][0]
            self.assertEqual((s["outcome"], s["returned"]), (cls, 0.0), cls)
            self.assertEqual(led["delphi_signals"][0]["weight"], -0.8)
            self.assertEqual(led["leaderboard"][0]["forfeits"], 1)

    def test_claim_without_patch_forfeits_after_deadline(self):
        r = won()
        led = self.settle([r, {"kind": "claim", "issue": r["issue"]}], [], now=NOW + timedelta(days=ta.PATCH_DEADLINE_DAYS + 1))
        self.assertEqual(led["settlements"][0]["outcome"], "no_patch_after_claim")

    def test_open_stays_in_escrow(self):
        r = won()
        led = self.settle([r, {"kind": "claim", "issue": r["issue"]}], self.census("open"))
        self.assertIn(r["issue"], led["escrow"])
        self.assertEqual(led["delphi_signals"], [])

    def test_no_claim_refunds_and_emits_nothing(self):
        r = won()  # won, but no patch -> nothing posted -> no claim receipt
        led = self.settle([r], [])
        self.assertEqual(led["settlements"][0]["outcome"], "no_claim")
        self.assertEqual(led["settlements"][0]["returned"], r["ante"])
        self.assertEqual(led["delphi_signals"], [])

    def test_replay_is_deterministic_and_order_independent(self):
        a, b = won(), won(dict(EASY, url="https://github.com/acme/web/issues/6"))
        c = [a, b, {"kind": "claim", "issue": a["issue"]}]
        cen = self.census("real_merge")
        self.assertEqual(self.settle(c, cen), self.settle(list(reversed(c)), cen))

    def test_forfeits_drain_credit_until_no_seat(self):
        receipts, eid = [], None
        for i in range(12):
            r = won(dict(EASY, url=f"https://github.com/acme/web/issues/{100 + i}"), at=NOW)
            eid = eid or r["winner"]
            r["winner"] = eid
            receipts += [r, {"kind": "claim", "issue": r["issue"]}]
        cen = [{"repo": "acme/web", "title": f"Fix #{100 + i}", "class": "closed_unmerged",
                "created_at": "2026-11-12T09:00:00Z"} for i in range(12)]
        led = ta.replay(receipts, cen, POOL, NOW + timedelta(hours=2))
        outs = [s["outcome"] for s in led["settlements"]]
        self.assertIn("void_insufficient_credit", outs)
        self.assertIn(eid, led["credits_low"])


class Cli(unittest.TestCase):
    def test_auction_then_settle(self):
        with tempfile.TemporaryDirectory() as d:
            cat = Path(d) / "cat.json"
            cat.write_text(json.dumps({"preflight": "tribute_system1.preflight_candidate", "items": [EASY]}))
            rec = Path(d) / "r.jsonl"
            self.assertEqual(ta.main(["auction", "--catalog", str(cat), "--pool", str(FX / "pool.json"),
                                      "--now", "2026-11-12T08:00:00Z", "--out", str(rec)]), 0)
            row = json.loads(rec.read_text().splitlines()[0])
            self.assertEqual(row["result"], "won")
            self.assertFalse(row["claimed"])
            out = Path(d) / "led.json"
            self.assertEqual(ta.main(["settle", "--receipts", str(rec), "--census", str(Path(d) / "none.json"),
                                      "--pool", str(FX / "pool.json"), "--now", "2026-11-13T08:00:00Z",
                                      "--out", str(out), "--dashboard", ""]), 0)
            led = json.loads(out.read_text())
            self.assertEqual(led["totals"]["no_claim"], 1)


class Wiring(unittest.TestCase):
    def test_new_signals_changed_only(self):
        r = won()
        cen = [{"repo": "acme/web", "title": "Fix #5", "class": "real_merge", "created_at": "2026-11-13T00:00:00Z"}]
        led = ta.replay([r, {"kind": "claim", "issue": r["issue"]}], cen, POOL, NOW + timedelta(days=2))
        self.assertEqual(len(ta.new_signals(led, None)), 1)
        self.assertEqual(ta.new_signals(led, led), [])

    def test_merge_summary_into_status(self):
        led = ta.replay([won()], [], POOL, NOW + timedelta(days=1))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "status.json"
            p.write_text(json.dumps({"outcomes": {"skipped": 1}}))
            ta.merge_summary(p, led)
            doc = json.loads(p.read_text())
            self.assertEqual(doc["outcomes"], {"skipped": 1})
            self.assertEqual(doc["tribute_auction"]["totals"]["no_claim"], 1)

    def test_live_preflight_fails_closed_on_bad_url(self):
        self.assertFalse(ta.live_preflight("https://example.com/x", s1)["eligible"])


if __name__ == "__main__":
    unittest.main()
