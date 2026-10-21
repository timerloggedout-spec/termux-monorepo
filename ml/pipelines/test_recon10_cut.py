import json
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from ml.pipelines.cli import main
from ml.pipelines.recon09.rules import classify_open_pr as classify_v09
from ml.pipelines.recon10.catalog import all_observations
from ml.pipelines.recon10.connectors import connector_report
from ml.pipelines.recon10.drift import drift_report
from ml.pipelines.recon10.roles import BOARD_LANES, OPEN_PRS_OBSERVED
from ml.pipelines.recon10.rules import CODERABBIT_FILE_BUDGET, INVALID_PARKING, VALID_LANES, classify_open_pr
from ml.pipelines.recon10.steward import report


class Recon10CutTest(unittest.TestCase):
    def test_stamp_does_not_promote_observer_or_retarget_live(self) -> None:
        payload = report()
        self.assertEqual(payload["version"], "0.10.0")
        self.assertEqual(payload["command"], "cut")
        self.assertEqual(payload["product_sha"], "8d36f149214f4a147932188bc424e7c29b8de444")
        self.assertEqual(payload["observer_tip"], "df342068f969185d8b6e095d8fe039eab95a6012")
        self.assertFalse(payload["observer_tip_promotable"])
        self.assertFalse(payload["writes"])
        self.assertTrue(payload["keep_pipelines"])
        self.assertFalse(payload["locks"]["coderabbit_is_gate"])
        self.assertFalse(payload["locks"]["pulse_comment_175"])
        self.assertFalse(payload["locks"]["force_push_master"])
        self.assertEqual(payload["locks"]["live_cli_frozen_at"], "0.9.0")
        self.assertEqual(payload["open_prs_observed"], 211)
        self.assertFalse(payload["catalog_is_full_board"])
        self.assertEqual(sum(BOARD_LANES.values()), OPEN_PRS_OBSERVED)
        self.assertEqual(BOARD_LANES["CANDIDATE"], 0)

    def test_catalog_matches_rules_and_stays_in_budget(self) -> None:
        rows = all_observations()
        self.assertEqual(len(rows), 87)
        pkg = Path(__file__).resolve().parent / "recon10"
        package_files = [path for path in pkg.rglob("*.py")]
        # package + this test + cli.py + README.md
        self.assertEqual(len(package_files) + 3, CODERABBIT_FILE_BUDGET - 1)
        self.assertEqual(CODERABBIT_FILE_BUDGET, 100)
        for row in rows:
            self.assertIn(row.lane, VALID_LANES)
            self.assertTrue(INVALID_PARKING.isdisjoint(row.reasons))
            self.assertNotIn(row.lane, INVALID_PARKING)
            if row.kind != "pr":
                continue
            lane, reasons, action = classify_open_pr(
                number=row.number,
                base=row.base,
                login=row.login,
                title=row.title,
                draft="draft" in row.reasons,
            )
            self.assertEqual(row.lane, lane, row.number)
            self.assertEqual(row.action, action, row.number)
            self.assertEqual(row.reasons, reasons, row.number)

    def test_session_note_and_jules_login_drift(self) -> None:
        title = "ops(skills): session note 2026-10-12 06:22 UTC — master green, continue monitoring"
        old = classify_v09(number=1209, base="master", login="timerloggedout-spec", title=title)
        new = classify_open_pr(number=1209, base="master", login="timerloggedout-spec", title=title)
        self.assertEqual(old[0], "NEED_EVIDENCE")
        self.assertEqual(new[0], "SUPERSEDE")
        self.assertEqual(new[2], "supersede-generated-board-is-ssot")
        jules = classify_open_pr(
            number=1206,
            base="master",
            login="app/google-labs-jules",
            title="Consolidate development lane upgrades and audit fixes",
        )
        self.assertEqual(jules[0], "EXTRACT")
        self.assertEqual(jules[2], "do-not-overwrite-peer")
        stale_login = classify_v09(
            number=1206,
            base="master",
            login="app/google-labs-jules",
            title="Consolidate development lane upgrades and audit fixes",
        )
        self.assertEqual(stale_login[0], "NEED_EVIDENCE")

    def test_wholesale_staging_and_connectors(self) -> None:
        by_number = {row.number: row for row in all_observations() if row.kind == "pr"}
        for number in (432, 682, 787):
            self.assertEqual(by_number[number].lane, "EXTRACT")
            self.assertEqual(by_number[number].action, "extract-only-keep-pipelines")
        self.assertEqual(by_number[48].action, "never-retarget")
        self.assertEqual(by_number[1211].action, "do-not-overwrite-peer")
        payload = connector_report()
        self.assertFalse(payload["secrets"])
        blob = json.dumps(payload)
        self.assertNotIn("ghp_", blob)
        self.assertNotIn("github_pat_", blob)
        self.assertNotIn("BEGIN PRIVATE", blob)
        names = {row["name"] for row in payload["connectors"]}
        self.assertIn("notion", names)
        self.assertIn("grafana", names)
        grafana = next(row for row in payload["connectors"] if row["name"] == "grafana")
        self.assertEqual(grafana["state"], "LIVE")
        self.assertNotEqual(grafana["lane"], "CANDIDATE")
        gmail = next(row for row in payload["connectors"] if row["name"] == "gmail")
        self.assertEqual(gmail["state"], "LIVE")
        self.assertNotEqual(gmail["lane"], "CANDIDATE")
        vercel = next(row for row in payload["connectors"] if row["name"] == "vercel")
        self.assertNotEqual(vercel["lane"], "CANDIDATE")

    def test_cli_cut_leaves_live_and_status_frozen(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["cut"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["version"], "0.10.0")
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["live"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buf.getvalue())["version"], "0.9.0")
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["status"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buf.getvalue())["version"], "0.8.0")
        drift = drift_report()
        self.assertFalse(drift["writes"])
        self.assertGreater(drift["fresh_rows"], 0)
        self.assertIsInstance(drift["lane_or_action_changes"], list)


if __name__ == "__main__":
    unittest.main()
