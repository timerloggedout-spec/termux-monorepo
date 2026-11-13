import csv
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr

from scripts.model_selection_market.market import BetEntry, MarketGraph
from scripts.model_selection_market.paper_wallet import FIELDS, main, parse_csv, write_csv
from scripts.model_selection_market.paper_wallet import _amount, _same_path


class PaperAccountingCsvTests(unittest.TestCase):
    def test_account_rows_and_integer_paper_point_stake(self):
        graph = MarketGraph()
        graph.open_account("alice", event_id="open", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
        graph.issue_points("alice", 9, event_id="issue", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
        bet = BetEntry(actor_class="itself", subject_kind="model", subject_id="m", actor_id="alice",
                       unit_kind="paper_point", units=3)
        graph.reserve_bet(bet, event_id="reserve", reservation_id="r1")
        snapshot = graph.snapshot()
        out = io.StringIO(newline="")
        write_csv(snapshot, out)
        rows = list(csv.DictReader(io.StringIO(out.getvalue(), newline="")))
        account = next(r for r in rows if r["record_type"] == "account")
        self.assertEqual((account["balance"], account["reserved"], account["available"]), ("9", "3", "6"))
        stake = next(r for r in rows if r["record_type"] == "stake")
        reservation = next(r for r in rows if r["record_type"] == "reservation")
        self.assertEqual(stake["reservation_id"], "r1")
        self.assertEqual(reservation["reservation_id"], "r1")
        self.assertEqual(reservation["entry_id"], stake["entry_id"])
        self.assertEqual(account["source_digest"], snapshot["paper_accounting"]["source_digest"])
        self.assertEqual(parse_csv(out.getvalue()), rows)
        self.assertEqual(FIELDS[:22], ["paper_only", "record_type", "actor_id", "actor_class", "entry_id", "subject_kind", "subject_id", "model", "task", "units", "unit_kind", "status", "prediction", "role", "card_id", "card_owner", "card_share", "artifact_path", "opt_script_path", "offer_to", "offer_at", "note"])

    def test_invalid_accounting_and_csv_amounts_rejected(self):
        graph = MarketGraph()
        graph.open_account("alice", event_id="open", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
        graph.issue_points("alice", 5, event_id="issue", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
        snapshot = graph.snapshot()
        snapshot["paper_accounting"]["accounts"][0]["available"] = 99
        with self.assertRaises(ValueError):
            write_csv(snapshot, io.StringIO())
        malformed = ",".join(FIELDS) + "\n" + ",".join(["x"] * len(FIELDS)) + "\n"
        with self.assertRaises(ValueError):
            parse_csv(malformed)

    def test_snapshot_history_and_integer_bounds_are_verified(self):
        graph = MarketGraph()
        graph.open_account("alice", event_id="open", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
        graph.issue_points("alice", 5, event_id="issue", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
        snapshot = graph.snapshot()
        for bad in (True, 2**63):
            with self.assertRaises(ValueError): _amount(bad, "amount", integer=True)
        changed = copy.deepcopy(snapshot)
        changed["paper_accounting"]["events"][1]["payload"]["units"] = 4
        with self.assertRaises(ValueError): write_csv(changed, io.StringIO())
        changed = copy.deepcopy(snapshot)
        changed["paper_accounting"]["event_count"] = 99
        with self.assertRaises(ValueError): write_csv(changed, io.StringIO())

    def test_source_symlink_protects_resolved_lock(self):
        with tempfile.TemporaryDirectory() as d:
            real = Path(d) / "real.jsonl"
            alias = Path(d) / "alias.jsonl"
            real.write_text("")
            alias.symlink_to(real)
            self.assertTrue(_same_path(alias, Path(str(real) + ".lock")))

    def test_replay_exports_and_view_detects_stale_or_tampered_csv(self):
        with tempfile.TemporaryDirectory() as d:
            event_log = Path(d) / "events.jsonl"
            view_path = Path(d) / "view.csv"
            MarketGraph(event_path=str(event_log)).open_account("alice", event_id="open", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
            MarketGraph(event_path=str(event_log)).issue_points("alice", 4, event_id="i", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
            main(["export-events", str(event_log), str(view_path)])
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main(["view", str(view_path), "--events", str(event_log)]), 0)
            view_path.write_text(view_path.read_text() + "tamper\n")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["view", str(view_path), "--events", str(event_log)])

    def test_source_and_lock_cannot_be_overwritten_and_invalid_export_preserves_destination(self):
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "events.jsonl"
            graph = MarketGraph(event_path=str(source))
            graph.open_account("alice", event_id="open", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
            graph.issue_points("alice", 1, event_id="i", provenance={"issuer": "fixture", "source": "synthetic", "reference": "test"})
            original = source.read_bytes()
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["export-events", str(source), str(source)])
            self.assertEqual(source.read_bytes(), original)
            lock = Path(str(source) + ".lock")
            lock.write_text("keep")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["export-events", str(source), str(lock)])
            self.assertEqual(lock.read_text(), "keep")
            bad = Path(d) / "bad.json"
            bad.write_text(json.dumps({"schema_version": 1, "policy": "observational_until_promote", "cards": [None], "bets": []}))
            output = Path(d) / "out.csv"
            output.write_text("old")
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                main(["export", str(bad), str(output)])
            self.assertEqual(output.read_text(), "old")


if __name__ == "__main__":
    unittest.main()
