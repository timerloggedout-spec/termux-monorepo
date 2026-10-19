import json
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from ml.pipelines.cli import main
from ml.pipelines.recon10.rules import classify_open_pr as classify_v10
from ml.pipelines.recon11.catalog import all_observations
from ml.pipelines.recon11.connectors import connector_report
from ml.pipelines.recon11.drift import drift_report
from ml.pipelines.recon11.locks import LOCKS
from ml.pipelines.recon11.roles import BOARD_LANES, OPEN_PRS_OBSERVED
from ml.pipelines.recon11.rules import CODERABBIT_FILE_BUDGET, INVALID_PARKING, VALID_LANES, classify_open_pr
from ml.pipelines.recon11.steward import report


class Recon11ProbeTest(unittest.TestCase):
    def test_stamp_does_not_promote_observer_or_retarget_frozen_cuts(self) -> None:
        payload = report()
        self.assertEqual(payload["version"], "0.11.0")
        self.assertEqual(payload["command"], "probe")
        self.assertEqual(payload["product_sha"], "8d36f149214f4a147932188bc424e7c29b8de444")
        self.assertEqual(payload["observer_tip"], "fd8c30ace52de915cf50fc3f18a070abf462cc89")
        self.assertFalse(payload["observer_tip_promotable"])
        self.assertFalse(payload["writes"])
        self.assertTrue(payload["keep_pipelines"])
        self.assertFalse(payload["locks"]["coderabbit_is_gate"])
        self.assertFalse(payload["locks"]["pulse_comment_175"])
        self.assertFalse(payload["locks"]["force_push_master"])
        self.assertEqual(payload["locks"]["cut_cli_frozen_at"], "0.10.0")
        self.assertEqual(payload["locks"]["live_cli_frozen_at"], "0.9.0")
        self.assertEqual(payload["open_prs_observed"], 173)
        self.assertFalse(payload["catalog_is_full_board"])
        self.assertEqual(sum(BOARD_LANES.values()), OPEN_PRS_OBSERVED)
        self.assertEqual(BOARD_LANES["CANDIDATE"], 0)
        self.assertEqual(LOCKS["wholesale_ml"], (432, 549, 601, 682, 724, 746, 787, 817))

    def test_catalog_matches_rules_and_stays_in_budget(self) -> None:
        rows = all_observations()
        self.assertEqual(len(rows), 87)
        pkg = Path(__file__).resolve().parent / "recon11"
        package_files = [path for path in pkg.rglob("*.py")]
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

    def test_status_recon_and_jules_peer_drift(self) -> None:
        title = "ops(skills): live status recon 2026-10-14T06:26Z"
        old = classify_v10(number=1223, base="master", login="timerloggedout-spec", title=title)
        new = classify_open_pr(number=1223, base="master", login="timerloggedout-spec", title=title)
        self.assertEqual(old[0], "NEED_EVIDENCE")
        self.assertEqual(new[0], "SUPERSEDE")
        self.assertEqual(new[2], "supersede-generated-board-is-ssot")
        jules = classify_open_pr(
            number=1217,
            base="master",
            login="app/google-labs-jules",
            title="Sentinel: Harden hub_mcp CLI",
        )
        self.assertEqual(jules[0], "EXTRACT")
        self.assertEqual(jules[2], "do-not-overwrite-peer")

    def test_closed_wholesale_stays_locked_and_connectors_have_no_secrets(self) -> None:
        by_number = {row.number: row for row in all_observations() if row.kind == "pr"}
        for number in (432, 682, 787):
            self.assertNotIn(number, by_number)
        self.assertIn(1249, by_number)
        self.assertEqual(by_number[1249].action, "bind-dual-gate-on-this-sha")
        self.assertEqual(by_number[1217].action, "do-not-overwrite-peer")
        if 48 in by_number:
            self.assertEqual(by_number[48].action, "never-retarget")
        payload = connector_report()
        self.assertFalse(payload["secrets"])
        self.assertEqual(payload["probed_on"], "2026-10-19")
        blob = json.dumps(payload)
        self.assertNotIn("ghp_", blob)
        self.assertNotIn("github_pat_", blob)
        self.assertNotIn("BEGIN PRIVATE", blob)
        self.assertNotIn("@gmail.com", blob)
        states = {row["name"]: row for row in payload["connectors"]}
        self.assertEqual(states["grafana"]["state"], "DEGRADED")
        self.assertNotEqual(states["grafana"]["lane"], "CANDIDATE")
        self.assertEqual(states["mixpanel"]["state"], "LIVE")
        self.assertEqual(states["gamma"]["state"], "EMPTY")
        self.assertEqual(states["figma"]["state"], "AUTHENTICATED")
        self.assertEqual(states["bigquery"]["state"], "NOT_PROBED")
        self.assertEqual(states["gmail"]["state"], "LIVE")
        self.assertNotEqual(states["vercel"]["lane"], "CANDIDATE")
        self.assertEqual(states["github"]["lane"], "CANDIDATE")

    def test_cli_probe_leaves_cut_live_and_status_frozen(self) -> None:
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["probe"])
        self.assertEqual(code, 0)
        payload = json.loads(buf.getvalue())
        self.assertEqual(payload["version"], "0.11.0")
        buf = StringIO()
        with patch("sys.stdout", buf):
            code = main(["cut"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buf.getvalue())["version"], "0.10.0")
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
