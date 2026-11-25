"""Offline end-to-end CLI regression: one existing market, disposable CSV."""
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from scripts.model_selection_market.cli import main
from scripts.model_selection_market.market import MarketGraph
from scripts.model_selection_market.paper_wallet import main as csv_main


class TestPaperAccountingCLI(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.events = self.root / "market.jsonl"

    def command(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["paper", "--events", str(self.events), *args]), 0)
        return json.loads(output.getvalue())

    def open(self, owner):
        return self.command("open", "--owner", owner, "--event-id", "open-" + owner,
                            "--issuer", "fixture", "--source", "synthetic", "--reference", "cli-test")

    def test_complete_cli_lifecycle_and_csv_rebuild(self):
        opened = self.open("alice")
        self.assertEqual(opened["paper_accounting"]["accounts"][0]["balance"], 0)
        self.open("bob")
        self.command("issue", "--owner", "alice", "--units", "10", "--event-id", "seed",
                     "--issuer", "fixture", "--source", "synthetic", "--reference", "cli-test")
        reserve = ("reserve-bet", "--owner", "alice", "--actor-class", "job",
                   "--subject-kind", "job", "--subject-id", "offline-fixture", "--units", "6",
                   "--reservation-id", "hold", "--event-id", "reserve")
        first = self.command(*reserve)
        retried = self.command(*reserve)
        self.assertEqual(first, retried)
        account = next(a for a in first["paper_accounting"]["accounts"] if a["owner"] == "alice")
        self.assertEqual((account["balance"], account["reserved"], account["available"]), (10, 6, 4))
        settled = self.command("settle", "--reservation-id", "hold", "--event-id", "settle", "--recipient", "bob")
        self.assertEqual(self.command("status"), settled)
        balances = {a["owner"]: a["balance"] for a in settled["paper_accounting"]["accounts"]}
        self.assertEqual(balances, {"alice": 4, "bob": 6})
        projection = self.root / "paper.csv"
        self.assertEqual(csv_main(["export-events", str(self.events), str(projection)]), 0)
        canonical = projection.read_text()
        with redirect_stdout(io.StringIO()):
            self.assertEqual(csv_main(["view", str(projection), "--events", str(self.events)]), 0)
        projection.write_text(canonical.replace("alice", "mallory"))
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            csv_main(["view", str(projection), "--events", str(self.events)])
        self.assertEqual(MarketGraph(event_path=self.events).snapshot(), settled)
        self.assertFalse((self.root / "performance.jsonl").exists())

    def test_bad_cli_amount_does_not_append(self):
        self.open("alice")
        before = self.events.read_bytes()
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            self.command("issue", "--owner", "alice", "--units", "-1", "--event-id", "bad",
                         "--issuer", "fixture", "--source", "synthetic", "--reference", "cli-test")
        self.assertEqual(error.exception.code, 2)
        self.assertEqual(self.events.read_bytes(), before)

    def test_legacy_demo_still_observational(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["market-demo"]), 0)
        snapshot = json.loads(output.getvalue())
        self.assertEqual(snapshot["policy"], "observational_until_promote")
        self.assertNotIn("paper_accounting", snapshot)
        self.assertFalse(self.events.exists())



    def test_cull_and_pool_distribution_cli(self):
        import hashlib
        self.open("alice")
        self.open("bob")
        self.command("issue", "--owner", "alice", "--units", "20", "--event-id", "seed",
                     "--issuer", "fixture", "--source", "synthetic", "--reference", "cli-test")
        culled = self.command(
            "cull", "--participant", "alice", "--decision-id", "decision-cli",
            "--reason", "cohort_expiry", "--score", "0.25",
            "--evidence-digest", hashlib.sha256(b"cli-score").hexdigest(),
            "--pool-id", "season-cli", "--available-disposition", "donate",
            "--reservation-dispositions", "[]", "--event-id", "cull-cli")
        pool = next(a for a in culled["paper_accounting"]["accounts"] if a["owner"] == "pool:season-cli")
        self.assertEqual(pool["balance"], 20)
        distributed = self.command(
            "distribute-pool", "--pool-id", "season-cli", "--distribution-id", "round-cli",
            "--reason", "cohort_awards", "--allocations", '[{"recipient":"bob","units":12}]',
            "--event-id", "distribution-cli")
        balances = {a["owner"]: a["balance"] for a in distributed["paper_accounting"]["accounts"]}
        self.assertEqual(balances, {"alice": 0, "bob": 12, "pool:season-cli": 8})


if __name__ == "__main__":
    unittest.main()
