import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "que"))
sys.path.insert(0, str(ROOT / "scripts" / "delphi"))

from sie_pipeline import build_receipt
from sie_research_packet import build_research_packet, digest, main as research_packet_main
from generate_proposal import generate, _sha


def evidence_item(claim, value, path, fresh_until):
    payload = {"claim": claim, "value": value, "path": path}
    return {
        "claim": claim,
        "value": value,
        "provenance": {"source": "github-api", "path": path,
                       "observed_at": "2026-11-14T00:00:00Z"},
        "fresh_until": fresh_until,
        "sha256": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
    }


def fixture():
    receipt = build_receipt(
        source_kind="workflow_run", source_id="123",
        source_revision="a" * 40, failure_class="repo-gate",
        sha="a" * 40, observed_at="2026-11-14T00:00:00Z",
    )
    evidence = {
        "schema": "delphi-evidence-set/v1",
        "artifact": {"kind": "workflow_run", "ref": "123",
                     "repo": "timerloggedout-spec/termux-monorepo"},
        "assembled_at": "2026-11-14T00:00:00Z",
        "fresh_until": "2026-11-14T00:15:00Z",
        "items": [
            evidence_item("run.conclusion", "failure", "/actions/runs/123",
                          "2026-11-14T00:15:00Z"),
            evidence_item("file.blob_sha", "b" * 40, "/contents/scripts/ci.py",
                          "2026-11-13T00:15:00Z"),
        ],
        "material": True,
    }
    diagnosis = {
        "summary": "Diagnose the failing repository gate and define a replayable repair.",
        "owner_role": "que",
        "confirmed_facts": [
            {"text": "The source workflow run concluded with failure.",
             "evidence_refs": ["run.conclusion"]},
            {"text": "The source file evidence is stale.",
             "evidence_refs": ["file.blob_sha"]},
            {"text": "A referenced claim is absent.",
             "evidence_refs": ["missing.claim"]},
        ],
        "hypotheses": [{"text": "A recent source change may explain the failure."}],
        "unknowns": ["The independent replay outcome remains unmeasured."],
        "baseline": {"queue_wait_p95_s": None, "quality": "unmeasured"},
        "related_history": [{"ref": "PR-1", "relationship": "prior repair"}],
        "replay_recipe": ["Run the focused regression suite.",
                          "Run the repository gate on the candidate SHA."],
        "acceptance_tests": ["Focused regression passes.",
                             "Repository gate passes on the same SHA."],
        "risk_envelope": {"risks": ["Regression risk across adjacent workflows."]},
        "alternatives": ["Repair the producer contract.",
                         "Add a narrow compatibility adapter."],
    }
    return receipt, diagnosis, [evidence]


class TestSIEResearchPacket(unittest.TestCase):
    def test_packet_preserves_freshness_and_evidence_boundaries(self):
        receipt, diagnosis, evidence = fixture()
        packet, brief, fresh_sets = build_research_packet(
            source_receipt=receipt, diagnosis=diagnosis,
            evidence_sets=evidence, generated_at="2026-11-14T00:05:00Z",
        )
        self.assertEqual(packet["schema"], "que.sie-research-packet/v1")
        self.assertEqual(packet["evidence"]["sets"][0]["source_set_digest"], _sha(evidence[0]))
        self.assertEqual(packet["evidence"]["sets"][0]["fresh_subset_digest"], _sha(fresh_sets[0]))
        self.assertEqual(packet["oracle_method"]["evidence_set_digests"], [_sha(fresh_sets[0])])
        self.assertEqual([fact["text"] for fact in packet["confirmed_facts"]],
                         ["The source workflow run concluded with failure."])
        self.assertEqual(len(packet["unverified_facts"]), 2)
        self.assertEqual(packet["evidence"]["rejected_claims"]["file.blob_sha"],
                         "stale_or_invalid_freshness")
        self.assertEqual(packet["evidence"]["rejected_claims"]["missing.claim"],
                         "missing_claim")
        self.assertEqual([item["claim"] for item in fresh_sets[0]["items"]],
                         ["run.conclusion"])
        self.assertEqual(brief["summary_points"][0]["evidence_refs"],
                         ["run.conclusion"])
        self.assertTrue(all(not point["evidence_refs"]
                            for point in brief["summary_points"][1:]))
        claimed_digest = packet.pop("package_digest")
        self.assertEqual(claimed_digest, digest(packet))

    def test_packet_feeds_existing_oracle_method_generator(self):
        receipt, diagnosis, evidence = fixture()
        packet, brief, fresh_sets = build_research_packet(
            source_receipt=receipt, diagnosis=diagnosis,
            evidence_sets=evidence, generated_at="2026-11-14T00:05:00Z",
        )
        docs = generate(brief, fresh_sets, generated_at="2026-11-14T00:05:00Z")
        self.assertEqual(set(docs), {"MANIFEST.md", "ITEMS.md", "RFP.md", "PROVENANCE.json"})
        self.assertIn("Confirmed: The source workflow run concluded with failure.", docs["RFP.md"])
        self.assertIn("Unverified:", docs["RFP.md"])
        provenance = json.loads(docs["PROVENANCE.json"])
        self.assertEqual(provenance["external_calls_by_generator"], 0)
        self.assertEqual(provenance["human_ballots_received"], 0)
        self.assertEqual(provenance["proposal_id"], brief["id"])
        self.assertEqual(brief["related_issues"], [])

    def test_issue_backed_sources_keep_issue_refs(self):
        _, diagnosis, evidence = fixture()
        receipt = build_receipt(
            source_kind="queue_item", source_id="8123",
            source_revision="issue-revision-1", failure_class="queue-repair",
            sha="a" * 40, observed_at="2026-11-14T00:00:00Z",
        )
        _, brief, _ = build_research_packet(
            source_receipt=receipt, diagnosis=diagnosis,
            evidence_sets=evidence, generated_at="2026-11-14T00:05:00Z",
        )
        self.assertEqual(brief["related_issues"], [8123])

    def test_rebuild_removes_obsolete_managed_evidence_files(self):
        receipt, diagnosis, evidence = fixture()
        second = json.loads(json.dumps(evidence[0]))
        second["artifact"]["ref"] = "second-set"
        second["items"] = [evidence_item(
            "second.claim", "second value", "/second/source",
            "2026-11-14T00:15:00Z",
        )]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt_path = root / "receipt.json"
            diagnosis_path = root / "diagnosis.json"
            first_evidence = root / "first-evidence.json"
            second_evidence = root / "second-evidence.json"
            out = root / "out"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            diagnosis_path.write_text(json.dumps(diagnosis), encoding="utf-8")
            first_evidence.write_text(json.dumps(evidence[0]), encoding="utf-8")
            second_evidence.write_text(json.dumps(second), encoding="utf-8")

            common = [
                "--receipt", str(receipt_path),
                "--diagnosis", str(diagnosis_path),
                "--out", str(out),
                "--generated-at", "2026-11-14T00:05:00Z",
            ]
            self.assertEqual(research_packet_main(common + [
                "--evidence", str(first_evidence),
                "--evidence", str(second_evidence),
            ]), 0)
            evidence_dir = out / "evidence"
            self.assertTrue((evidence_dir / "evidence-002.json").exists())
            (evidence_dir / "operator-notes.txt").write_text("keep", encoding="utf-8")

            self.assertEqual(research_packet_main(common + [
                "--evidence", str(first_evidence),
            ]), 0)
            self.assertTrue((evidence_dir / "evidence-001.json").exists())
            self.assertFalse((evidence_dir / "evidence-002.json").exists())
            self.assertEqual((evidence_dir / "operator-notes.txt").read_text(encoding="utf-8"), "keep")

    def test_packet_rejects_evidence_integrity_drift(self):
        receipt, diagnosis, evidence = fixture()
        evidence[0]["items"][0]["value"] = "success"
        with self.assertRaisesRegex(ValueError, "at least one confirmed fact"):
            build_research_packet(
                source_receipt=receipt, diagnosis=diagnosis,
                evidence_sets=evidence, generated_at="2026-11-14T00:05:00Z",
            )

    def test_packet_requires_complete_oracle_plan(self):
        receipt, diagnosis, evidence = fixture()
        diagnosis["alternatives"] = []
        with self.assertRaisesRegex(ValueError, "alternatives"):
            build_research_packet(
                source_receipt=receipt, diagnosis=diagnosis,
                evidence_sets=evidence, generated_at="2026-11-14T00:05:00Z",
            )

    def test_packet_rejects_invalid_source_receipt(self):
        receipt, diagnosis, evidence = fixture()
        receipt["sha"] = "invalid"
        with self.assertRaisesRegex(ValueError, "invalid SIE source receipt"):
            build_research_packet(
                source_receipt=receipt, diagnosis=diagnosis,
                evidence_sets=evidence, generated_at="2026-11-14T00:05:00Z",
            )


if __name__ == "__main__":
    unittest.main()
