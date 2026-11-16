#!/usr/bin/env python3
import unittest
from unittest.mock import patch
import github_app_telemetry as telemetry

class ReceiptTests(unittest.TestCase):
    @patch.object(telemetry,"installation_repositories",return_value=["timerloggedout-spec/termux-monorepo"])
    @patch.object(telemetry,"rate_limit",side_effect=[{"limit":5000,"remaining":4999,"reset":1900000000},{"limit":5000,"remaining":4996,"reset":1900000000}])
    def test_complete_g4_receipt(self,rate,repos):
        with patch.object(telemetry,"load_registry",return_value={"registry_id":"x","apps":[{"slug":"termux-fleet-collector"}],"planned_roles":[]}):
            with patch.object(telemetry,"Probe") as probe:
                probe.return_value.status_counts={"200":4}
                result=telemetry.collect("ephemeral","termux-fleet-collector",{"run_id":123,"attempt":1,"head_sha":"a"*40})
        receipt=result["g4_runtime_receipt"]
        self.assertTrue(telemetry.validate_receipt(receipt))
        self.assertEqual(receipt["repositories_inspected"],1)
        self.assertNotIn("ephemeral",str(result))
    def test_pagination_reads_every_page(self):
        probe = unittest.mock.MagicMock()
        probe.get.side_effect = [
            (200, {"repositories": [{"full_name": "org/a"}]},
             {"Link": '<https://api.github.com/installation/repositories?per_page=100&page=2>; rel="next"'}),
            (200, {"repositories": [{"full_name": "org/b"}]}, {}),
        ]
        self.assertEqual(telemetry.installation_repositories(probe), ["org/a", "org/b"])
        self.assertEqual(probe.get.call_count, 2)

    def test_pagination_rejects_external_next_link(self):
        probe = unittest.mock.MagicMock()
        probe.get.return_value = (200, {"repositories": []},
            {"Link": '<https://attacker.example/steal>; rel="next"'})
        with self.assertRaisesRegex(ValueError, "escaped GitHub API host"):
            telemetry.installation_repositories(probe)

    def test_missing_token_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "token is required"):
            telemetry.Probe(None)

    def test_rejects_missing_or_secret_fields(self):
        with self.assertRaisesRegex(ValueError,"missing or unexpected"): telemetry.validate_receipt({"schema_version":1})
    def test_rejects_bad_status_and_nan(self):
        r={"schema_version":1,"receipt_type":"github_app_g4_runtime_receipt","app_slug":"x","mint_outcome":"success","rate_limit_before":{"limit":1,"remaining":1,"reset":1},"rate_limit_after":{"limit":1,"remaining":1,"reset":1},"api_calls_by_status":{"abc":-1},"repositories_inspected":0,"workflow":{"run_id":1,"attempt":1,"head_sha":"a"*40},"duration_seconds":1.0,"conclusion":"success","observed_at":"2026-10-30T00:00:00+00:00"}
        with self.assertRaisesRegex(ValueError,"API status"): telemetry.validate_receipt(r)
        r["api_calls_by_status"]={"200":1}; r["duration_seconds"]=float("nan")
        with self.assertRaisesRegex(ValueError,"duration"): telemetry.validate_receipt(r)

if __name__=="__main__": unittest.main()
