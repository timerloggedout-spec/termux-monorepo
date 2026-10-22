"""Contract tests for the append-only paper accounting lifecycle."""

import copy
import hashlib
import json
import multiprocessing
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.model_selection_market import market
from scripts.model_selection_market.market import BetEntry, MarketGraph, TradingCard

PROV = {"issuer": "fixture", "source": "synthetic", "reference": "test"}
MAX = 2**63 - 1


def _contend(path, index, queue):
    try:
        graph = MarketGraph(event_path=path)
        bet = BetEntry(actor_class="job", subject_kind="job", subject_id=f"subject-{index}",
                       actor_id="alice", unit_kind="paper_point", units=7)
        graph.reserve_bet(bet, event_id=f"contend-event-{index}", reservation_id=f"contend-res-{index}")
        queue.put(("won", index, None))
    except (ValueError, RuntimeError, OSError) as exc:
        queue.put(("lost", index, type(exc).__name__))
    except BaseException as exc:
        queue.put(("error", index, repr(exc)))
        raise


class PaperAccountingTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.path = Path(self.tempdir.name) / "events.jsonl"
        self.g = MarketGraph(event_path=str(self.path))

    def open(self, owner, event=None):
        return self.g.open_account(owner, event_id=event or f"open-{owner}", provenance=dict(PROV))

    def issue(self, owner="alice", units=10, event=None):
        return self.g.issue_points(owner, units, event_id=event or f"issue-{owner}", provenance=dict(PROV))

    def fund(self, *owners, units=10):
        for owner in owners:
            self.open(owner)
            self.issue(owner, units, f"issue-{owner}")

    def account(self, snapshot, owner):
        return next(row for row in snapshot["accounts"] if row["owner"] == owner)

    def bet(self, actor="alice", subject="task", units=2, actor_class="itself", kind="model", **kw):
        unit_kind = kw.pop("unit_kind", "paper_point")
        return BetEntry(actor_class=actor_class, subject_kind=kind, subject_id=subject,
                        actor_id=actor, unit_kind=unit_kind, units=units, **kw)

    def stream_bytes(self):
        return self.path.read_bytes() if self.path.exists() else b""

    def assert_invariants(self, snap):
        active = {}
        for r in snap["reservations"]:
            if r["status"] == "reserved":
                active[r["owner"]] = active.get(r["owner"], 0) + r["units"]
        for a in snap["accounts"]:
            self.assertEqual(a["reserved"], active.get(a["owner"], 0))
            self.assertEqual(a["available"], a["balance"] - a["reserved"])
            self.assertLessEqual(a["reserved"], a["balance"])
            self.assertLessEqual(a["balance"], MAX)

    def test_open_zero_and_event_count_covers_all_market_events(self):
        empty = self.g.accounting_snapshot()
        self.assertEqual((empty["event_count"], empty["accounts"]), (0, []))
        self.open("empty")
        snap = self.g.snapshot()
        a = self.account(snap["paper_accounting"], "empty")
        self.assertEqual((a["balance"], a["reserved"], a["available"]), (0, 0, 0))
        self.g.add_card(TradingCard(role="review", owner="empty"))
        self.g.place_bet(BetEntry(actor_class="others", subject_kind="model", subject_id="m"))
        accounting = self.g.accounting_snapshot()
        self.assertEqual(accounting["event_count"], 3)
        self.assertEqual(self.g.snapshot()["policy"], "observational_until_promote")

    def test_funded_self_peer_and_job_settlements_to_open_accounts(self):
        self.fund("self", "peer", "job-owner", "recipient", units=10)
        cases = [("self", "itself", "model", "self-subject", "r1"),
                 ("peer", "others", "model", "peer-subject", "r2"),
                 ("job-owner", "job", "job", "job-subject", "r3")]
        for actor, cls, kind, subject, rid in cases:
            self.g.reserve_bet(self.bet(actor, subject, 3, cls, kind), event_id=f"reserve-{rid}", reservation_id=rid)
            self.assert_invariants(self.g.accounting_snapshot())
            self.g.settle(rid, event_id=f"settle-{rid}", recipient="recipient")
            self.assert_invariants(self.g.accounting_snapshot())
        snap = self.g.accounting_snapshot()
        self.assertEqual(self.account(snap, "recipient")["balance"], 19)
        self.assertEqual(sum(a["balance"] for a in snap["accounts"]), 40)
        self.assertEqual(sum(a["reserved"] for a in snap["accounts"]), 0)

    def test_offer_links_card_owner_and_can_settle_or_release(self):
        self.fund("payer", "card-owner")
        card = self.g.add_card(TradingCard(role="review", owner="card-owner"))
        self.g.reserve_offer(card["card_id"], "payer", "card-owner", 4,
                            event_id="offer", reservation_id="offer-r")
        self.assert_invariants(self.g.accounting_snapshot())
        self.g.settle("offer-r", event_id="offer-settle", recipient="card-owner")
        self.assertEqual(self.account(self.g.accounting_snapshot(), "card-owner")["balance"], 14)
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.settle("offer-r", event_id="second-terminal", recipient="payer")
        card2 = self.g.add_card(TradingCard(role="other", owner="card-owner"))
        self.g.reserve_offer(card2["card_id"], "payer", "card-owner", 2,
                            event_id="offer-2", reservation_id="offer-r2")
        self.g.release("offer-r2", event_id="offer-release", reason="cancelled")
        self.assertEqual(self.account(self.g.accounting_snapshot(), "payer")["balance"], 6)
        self.assert_invariants(self.g.accounting_snapshot())

    def test_reserve_checks_available_and_duplicate_operation_lifetime(self):
        self.fund("alice")
        b = self.bet(units=7)
        self.g.reserve_bet(b, event_id="r1-event", reservation_id="r1")
        with self.assertRaises((ValueError, ArithmeticError)):
            self.g.reserve_bet(self.bet("alice", "different", 4), event_id="r2-event", reservation_id="r2")
        self.g.release("r1", event_id="release-r1", reason="void")
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.reserve_bet(b, event_id="r3-event", reservation_id="r3")
        # The same entry may be observed by a distinct actor.
        self.g.open_account("bob", event_id="open-bob", provenance=dict(PROV))
        self.issue("bob", 10)
        self.g.reserve_bet(self.bet("bob", "task", 2), event_id="bob-bet", reservation_id="bob-r")

    def test_exact_retry_timestamp_ignored_conflict_and_terminal_retry_restart(self):
        self.fund("alice", "bob")
        b = self.bet(units=2)
        self.g.reserve_bet(b, event_id="reserve", reservation_id="r")
        first = self.path.read_bytes()
        # BetEntry creates a fresh timestamp, but logical intent and entry key are identical.
        self.g.reserve_bet(self.bet(units=2), event_id="reserve", reservation_id="r")
        self.assertEqual(self.path.read_bytes(), first)
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.reserve_bet(self.bet(units=3), event_id="reserve", reservation_id="r")
        self.g.settle("r", event_id="settle", recipient="bob")
        settled_bytes = self.path.read_bytes()
        reopened = MarketGraph(event_path=str(self.path))
        reopened.settle("r", event_id="settle", recipient="bob")
        self.assertEqual(self.path.read_bytes(), settled_bytes)
        with self.assertRaises((ValueError, RuntimeError)):
            reopened.release("r", event_id="another-terminal", reason="tie")

    def test_duplicate_event_id_with_different_command_fails_without_append(self):
        self.open("alice", "same-id")
        before = self.path.read_bytes()
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.open_account("bob", event_id="same-id", provenance=dict(PROV))
        self.assertEqual(self.path.read_bytes(), before)

    def test_invalid_commands_are_atomic_and_validate_inputs(self):
        before = self.path.read_bytes() if self.path.exists() else b""
        for owner, prov in (("", PROV), ("alice", "fixture"), ("alice", {"issuer": "x"}),
                            ("alice", {"issuer": "", "source": "x", "reference": "x"})):
            with self.subTest(owner=owner, provenance=prov):
                with self.assertRaises((ValueError, TypeError)):
                    self.g.open_account(owner, event_id="bad-open", provenance=prov)
                self.assertEqual(self.stream_bytes(), before)
        self.open("alice")
        baseline = self.path.read_bytes()
        for n in (1.0, True, 0, -1, MAX + 1):
            with self.subTest(units=n):
                with self.assertRaises((ValueError, TypeError, OverflowError)):
                    self.g.issue_points("alice", n, event_id=f"bad-issue-{n}", provenance=dict(PROV))
                self.assertEqual(self.path.read_bytes(), baseline)
        with self.assertRaises((ValueError, RuntimeError)):
            self.issue("unknown", 1, "unknown-issue")
        self.assertEqual(self.path.read_bytes(), baseline)
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.reserve_bet(self.bet("alice", units=1, unit_kind="observational"), event_id="bad-unit", reservation_id="bad")
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.reserve_bet(self.bet("missing", units=1), event_id="unknown-reserve", reservation_id="missing-r")
        self.assertEqual(self.path.read_bytes(), baseline)

    def test_overflow_unsupported_settlement_recipient_and_release_reasons(self):
        self.open("alice")
        self.issue("alice", MAX)
        baseline = self.path.read_bytes()
        with self.assertRaises((ValueError, OverflowError)):
            self.issue("alice", 1, "overflow")
        self.assertEqual(self.path.read_bytes(), baseline)
        self.open("bob", "open-bob")
        self.issue("bob", 10, "issue-bob")
        self.g.reserve_bet(self.bet(units=1), event_id="reserve", reservation_id="r")
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.settle("r", event_id="unknown-recipient", recipient="unknown")
        self.assertEqual(self.path.read_bytes().count(b"\n"), 5)
        self.g.release("r", event_id="release", reason="unresolved")
        for reason in ("cancelled", "expired", "void", "rejected", "unresolved", "tie"):
            self.g.reserve_bet(self.bet("bob", f"s-{reason}", 1), event_id=f"reserve-{reason}", reservation_id=f"r-{reason}")
            self.g.release(f"r-{reason}", event_id=f"release-{reason}", reason=reason)
        self.assert_invariants(self.g.accounting_snapshot())

    def test_distinct_actors_and_offer_operation_key(self):
        self.fund("alice", "bob", "card-owner")
        card = self.g.add_card(TradingCard(role="offer", owner="card-owner"))
        self.g.reserve_offer(card["card_id"], "alice", "card-owner", 2, event_id="o1", reservation_id="or1")
        with self.assertRaises((ValueError, RuntimeError)):
            self.g.reserve_offer(card["card_id"], "alice", "card-owner", 2, event_id="o2", reservation_id="or2")
        self.assert_invariants(self.g.accounting_snapshot())

    def test_ephemeral_api_and_self_settle_max(self):
        graph = MarketGraph()
        graph.open_account("a", event_id="open", provenance=dict(PROV))
        graph.issue_points("a", MAX, event_id="issue", provenance=dict(PROV))
        graph.reserve_bet(self.bet("a", "max", MAX), event_id="reserve", reservation_id="r")
        graph.settle("r", event_id="settle", recipient="a")
        self.assertEqual(graph.accounting_snapshot()["accounts"][0]["balance"], MAX)
        self.assertEqual(graph.accounting_snapshot()["accounts"][0]["available"], MAX)

    def test_history_immutable_snapshot_digest_and_replay(self):
        self.fund("alice", "bob")
        self.g.reserve_bet(self.bet(units=2), event_id="reserve", reservation_id="r")
        prior = self.g.accounting_snapshot()
        reserved_event = copy.deepcopy(next(e for e in prior["events"] if e["event_id"] == "reserve"))
        prefix_digest = prior["source_digest"]
        raw_before = self.path.read_bytes()
        self.g.settle("r", event_id="settle", recipient="bob")
        after = self.g.accounting_snapshot()
        self.assertEqual(next(e for e in after["events"] if e["event_id"] == "reserve"), reserved_event)
        self.assertEqual(prior["source_digest"], prefix_digest)
        self.assertEqual(self.path.read_bytes()[:len(raw_before)], raw_before)
        replayed = MarketGraph(event_path=str(self.path)).accounting_snapshot()
        self.assertEqual(replayed["source_digest"], after["source_digest"])
        self.assertEqual(replayed["accounts"], after["accounts"])
        self.assertEqual(after["event_count"], 6)
        self.assertEqual(after["source_digest"], hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_durable_ack_lost_retry_same_event_id(self):
        self.open("alice")
        original = market.append
        failed = [False]
        def append_then_raise(path, events, candidate):
            result = original(path, events, candidate)
            if not failed[0]:
                failed[0] = True
                raise OSError("simulated lost acknowledgement after durable append")
            return result
        with mock.patch.object(market, "append", side_effect=append_then_raise):
            with self.assertRaises(OSError):
                self.issue("alice", 3, "uncertain")
            recovered = MarketGraph(event_path=str(self.path))
            recovered.issue_points("alice", 3, event_id="uncertain", provenance=dict(PROV))
        snap = MarketGraph(event_path=str(self.path)).accounting_snapshot()
        self.assertEqual(self.account(snap, "alice")["balance"], 3)
        self.assertEqual(snap["event_count"], 2)

    def test_corrupt_and_semantically_invalid_streams_fail_closed(self):
        self.open("alice")
        valid = self.path.read_bytes()
        cases = [valid + b'{"broken":', valid[:-1], b"not-json\n"]
        event = json.loads(valid.splitlines()[0])
        altered = copy.deepcopy(event); altered["version"] = 2
        cases.append(json.dumps(altered, separators=(",", ":")).encode() + b"\n")
        altered = copy.deepcopy(event); altered["seq"] = True
        cases.append(json.dumps(altered, separators=(",", ":")).encode() + b"\n")
        cases.append(valid + valid)
        # Valid JSON, valid envelope, but an invalid semantic transition.
        bad = {"event_id": "bad", "type": "issue", "payload": {"owner": "ghost", "units": 1, "provenance": dict(PROV)},
               "timestamp": event["timestamp"], "correlation_id": "bad", "version": 1, "seq": 2}
        cases.append(valid + json.dumps(bad, sort_keys=True, separators=(",", ":")).encode() + b"\n")
        for raw in cases:
            with self.subTest(raw=raw[:32]):
                self.path.write_bytes(raw)
                with self.assertRaises((ValueError, OSError, json.JSONDecodeError)):
                    MarketGraph(event_path=str(self.path)).accounting_snapshot()

    def test_process_contention_on_shared_balance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "shared.jsonl")
            graph = MarketGraph(event_path=path)
            graph.open_account("alice", event_id="open", provenance=dict(PROV))
            graph.issue_points("alice", 10, event_id="issue", provenance=dict(PROV))
            ctx = multiprocessing.get_context("spawn")
            queue = ctx.Queue()
            processes = [ctx.Process(target=_contend, args=(path, i, queue)) for i in range(2)]
            try:
                for process in processes:
                    process.start()
                for process in processes:
                    process.join(20)
                for process in processes:
                    if process.is_alive():
                        process.terminate()
                        process.join(5)
                outcomes = [queue.get(timeout=5) for _ in processes]
                self.assertFalse([o for o in outcomes if o[0] == "error"], outcomes)
                self.assertTrue(all(p.exitcode == 0 for p in processes), [p.exitcode for p in processes])
                self.assertEqual([o[0] for o in outcomes].count("won"), 1, outcomes)
                self.assertEqual([o[0] for o in outcomes].count("lost"), 1, outcomes)
                snap = MarketGraph(event_path=path).accounting_snapshot()
                alice = self.account(snap, "alice")
                self.assertEqual((alice["balance"], alice["reserved"], alice["available"]), (10, 7, 3))
                self.assert_invariants(snap)
            finally:
                for process in processes:
                    if process.is_alive():
                        process.terminate()
                    process.join(timeout=2)
                queue.close()
                queue.join_thread()


if __name__ == "__main__":
    unittest.main()
