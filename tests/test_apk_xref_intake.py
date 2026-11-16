import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.apk_xref import apk_xref_intake as ax

REQUEST = """### Target ID

aihub

### Paired repo brief

#2063

### Target repo URL

https://github.com/SilentCoderHere/aihub

### Artifact source

github-releases

### Authorization basis

Public open-source repository.

### Scope domains

github.com

### Side effect

read

### State-changing authorization

no

### Execution venue

remote-service

### Evidence expectation

reproduced

### Submitter Role{Moniker}

foundry{archW1z}
"""

FINDINGS = """### Target ID

aihub

### Cross-reference issue

#2064

### Package ID

com.aihub.app

### Artifact source

github-releases

### Artifact version + build

1.4.2 (build 1042)

### Manifest permissions

android.permission.INTERNET

### Endpoints actually observed

https://api.example.com/v1

### Source claims checked

offline-only — contradicted

### Divergences — repo to APK

README claims offline-only; artifact calls api.example.com

### Divergences — APK to repo

none found

### Verdict

divergences-found

### Evidence expectation met

reproduced

### Submitter Role{Moniker}

foundry{archW1z}
"""


class ApkXrefTests(unittest.TestCase):
    def test_request_record(self):
        rec = ax.build_record(ax.parse_form(REQUEST))
        self.assertEqual(rec["kind"], "request")
        self.assertEqual(rec["paired_repo_brief"], "#2063")
        self.assertEqual(rec["schema"], "apk-xref/v1")

    def test_findings_record_both_directions(self):
        rec = ax.build_record(ax.parse_form(FINDINGS))
        self.assertEqual(rec["kind"], "findings")
        self.assertEqual(rec["verdict"], "divergences-found")
        self.assertEqual(rec["divergences_apk_to_repo"], ["none found"])
        self.assertEqual(rec["manifest_permissions"], ["android.permission.INTERNET"])

    def test_no_artifact_findings(self):
        f = ax.parse_form(FINDINGS)
        f["verdict"] = "no-artifact-found"; f["package_id"] = "none"
        rec = ax.build_record(f)
        self.assertEqual(rec["package_id"], "")

    def test_refusals(self):
        f = ax.parse_form(REQUEST); f["paired_repo_brief"] = "the other issue"
        with self.assertRaises(ValueError):
            ax.build_record(f)
        f = ax.parse_form(REQUEST); f["submitter"] = "archW1z"
        with self.assertRaises(ValueError):
            ax.build_record(f)
        f = ax.parse_form(REQUEST); f["side_effect"] = "write"  # state_changing stays no
        with self.assertRaises(ValueError):
            ax.build_record(f)
        f = ax.parse_form(FINDINGS); f["divergences_apk_to_repo"] = ""
        with self.assertRaises(ValueError):
            ax.build_record(f)


if __name__ == "__main__":
    unittest.main()
