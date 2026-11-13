"""Contract tests for the separate origin-attributed royalty journal."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.model_selection_market.royalty_ledger import RoyaltyLedger, RoyaltyLedgerError


def sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def setup_ledger(path):
    ledger = RoyaltyLedger(path, policy_owner="governance-owner")
    ledger.register_origin(event_id="origin-a", artifact_id="artifact-a",
                           content_digest=sha("source-a"), origin_actor="author-a")
    ledger.register_origin(event_id="origin-b", artifact_id="artifact-b",
                           content_digest=sha("source-b"), origin_actor="author-b")
    ledger.register_derivative(
        event_id="derivative-ab", artifact_id="artifact-ab",
        content_digest=sha("combined"), author_actor="builder",
        parents=[
            {"artifact_id": "artifact-a", "weight_bps": 6000, "lineage_ref": "commit-a:path:1-60", "evidence_digest": sha("range-a")},
            {"artifact_id": "artifact-b", "weight_bps": 4000, "lineage_ref": "commit-b:path:20-80", "evidence_digest": sha("range-b")},
        ],
    )
    ledger.activate_policy(
        event_id="policy-1", policy_id="legacy-residual", version=1,
        rate_bps=1000, effective_from="2026-01-01T00:00:00+00:00",
        approved_by="governance-owner", approved_at="2026-01-01T00:00:00+00:00",
        approval_digest=sha("approved-policy-v1"),
    )
    return ledger


class RoyaltyLedgerTests(unittest.TestCase):
    def test_split_merge_lineage_allocates_origin_shares_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            snap = ledger.snapshot()
            lineage = snap["derivatives"]["artifact-ab"]["lineage"]
            self.assertEqual(lineage["artifact-a"]["share_bps"], 6000)
            self.assertEqual(lineage["artifact-b"]["share_bps"], 4000)

    def test_accrual_creates_separate_origin_payables(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            ledger.accrue(
                event_id="accrual-event-1", accrual_id="accrual-1",
                contribution_id="contribution-1", derivative_artifact_id="artifact-ab",
                policy_id="legacy-residual", policy_version=1, basis_units=10000,
                unit_domain="paper_point", event_time="2026-02-01T00:00:00+00:00",
            )
            snap = ledger.snapshot()
            self.assertEqual(snap["accruals"]["accrual-1"]["royalty_units"], 1000)
            self.assertEqual(snap["payables"]["author-a|paper_point"], 600)
            self.assertEqual(snap["payables"]["author-b|paper_point"], 400)

    def test_partial_settlement_reduces_only_matching_origin_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            ledger.accrue(
                event_id="accrual-event-1", accrual_id="accrual-1",
                contribution_id="contribution-1", derivative_artifact_id="artifact-ab",
                policy_id="legacy-residual", policy_version=1, basis_units=10000,
                unit_domain="paper_point", event_time="2026-02-01T00:00:00+00:00",
            )
            ledger.settle(
                event_id="settlement-event-1", settlement_id="settlement-1",
                accrual_id="accrual-1", origin_artifact_id="artifact-a", units=200,
                destination="paper-ledger-reference:payee-a",
                evidence_digest=sha("settlement-proof"), idempotency_key="settle-op-1",
            )
            snap = ledger.snapshot()
            self.assertEqual(snap["payables"]["author-a|paper_point"], 400)
            self.assertEqual(snap["payables"]["author-b|paper_point"], 400)

    def test_dispute_freezes_settlement_and_reversal_reduces_payable(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            ledger.accrue(
                event_id="accrual-event-1", accrual_id="accrual-1",
                contribution_id="contribution-1", derivative_artifact_id="artifact-ab",
                policy_id="legacy-residual", policy_version=1, basis_units=10000,
                unit_domain="paper_point", event_time="2026-02-01T00:00:00+00:00",
            )
            ledger.dispute(event_id="dispute-event-1", dispute_id="dispute-1",
                           accrual_id="accrual-1", reason="lineage review",
                           evidence_digest=sha("dispute-evidence"))
            with self.assertRaises(RoyaltyLedgerError):
                ledger.settle(
                    event_id="settlement-event-1", settlement_id="settlement-1",
                    accrual_id="accrual-1", origin_artifact_id="artifact-a", units=1,
                    destination="reference", evidence_digest=sha("proof"),
                    idempotency_key="settle-op-1",
                )
            ledger.reverse(
                event_id="reversal-event-1", reversal_id="reversal-1",
                accrual_id="accrual-1", origin_artifact_id="artifact-a", units=100,
                reason="incorrect attribution", evidence_digest=sha("reversal-proof"),
            )
            self.assertEqual(ledger.snapshot()["payables"]["author-a|paper_point"], 500)

    def test_policy_versions_require_sequential_non_overlapping_intervals(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            with self.assertRaises(RoyaltyLedgerError):
                ledger.activate_policy(
                    event_id="policy-3", policy_id="legacy-residual", version=3,
                    rate_bps=900, effective_from="2026-03-01T00:00:00+00:00",
                    approved_by="governance-owner", approved_at="2026-03-01T00:00:00+00:00",
                    approval_digest=sha("approval-v3"),
                )
            with self.assertRaises(RoyaltyLedgerError):
                ledger.activate_policy(
                    event_id="policy-2", policy_id="legacy-residual", version=2,
                    rate_bps=900, effective_from="2026-03-01T00:00:00+00:00",
                    effective_until="2026-04-01T00:00:00+00:00",
                    approved_by="governance-owner", approved_at="2026-03-01T00:00:00+00:00",
                    approval_digest=sha("approval-v2"),
                )

    def test_policy_activation_requires_configured_owner(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            with self.assertRaises(RoyaltyLedgerError):
                ledger.activate_policy(
                    event_id="policy-2", policy_id="unauthorized", version=1,
                    rate_bps=100, effective_from="2026-03-01T00:00:00+00:00",
                    approved_by="different-actor", approved_at="2026-03-01T00:00:00+00:00",
                    approval_digest=sha("bad-approval"),
                )

    def test_duplicate_contribution_and_settlement_idempotency_key_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            kwargs = dict(
                contribution_id="contribution-1", derivative_artifact_id="artifact-ab",
                policy_id="legacy-residual", policy_version=1, basis_units=10000,
                unit_domain="paper_point", event_time="2026-02-01T00:00:00+00:00",
            )
            ledger.accrue(event_id="accrual-event-1", accrual_id="accrual-1", **kwargs)
            with self.assertRaises(RoyaltyLedgerError):
                ledger.accrue(event_id="accrual-event-2", accrual_id="accrual-2", **kwargs)
            ledger.settle(
                event_id="settlement-event-1", settlement_id="settlement-1",
                accrual_id="accrual-1", origin_artifact_id="artifact-a", units=10,
                destination="reference", evidence_digest=sha("proof"),
                idempotency_key="settle-op-1",
            )
            with self.assertRaises(RoyaltyLedgerError):
                ledger.settle(
                    event_id="settlement-event-2", settlement_id="settlement-2",
                    accrual_id="accrual-1", origin_artifact_id="artifact-a", units=10,
                    destination="reference", evidence_digest=sha("proof-2"),
                    idempotency_key="settle-op-1",
                )

    def test_exact_event_retry_returns_original_and_conflicting_reuse_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "royalties.jsonl"
            ledger = RoyaltyLedger(path, policy_owner="governance-owner")
            args = dict(event_id="origin-event", artifact_id="artifact-a",
                        content_digest=sha("source-a"), origin_actor="author-a")
            first = ledger.register_origin(**args)
            second = ledger.register_origin(**args)
            self.assertEqual(first, second)
            with self.assertRaises(RoyaltyLedgerError):
                ledger.register_origin(**{**args, "origin_actor": "different-author"})
            self.assertEqual(len(ledger.snapshot()["origins"]), 1)

    def test_invalid_transition_is_rejected_before_append(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "royalties.jsonl"
            ledger = RoyaltyLedger(path, policy_owner="governance-owner")
            before = path.read_bytes() if path.exists() else b""
            with self.assertRaises(RoyaltyLedgerError):
                ledger.register_derivative(
                    event_id="bad-derivative", artifact_id="bad",
                    content_digest=sha("bad"), author_actor="builder",
                    parents=[{"artifact_id": "unknown", "weight_bps": 10000}],
                )
            after = path.read_bytes() if path.exists() else b""
            self.assertEqual(before, after)

    def test_replay_preserves_claims_after_origin_cull_in_another_domain(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "royalties.jsonl"
            ledger = setup_ledger(path)
            ledger.accrue(
                event_id="accrual-event-1", accrual_id="accrual-1",
                contribution_id="contribution-1", derivative_artifact_id="artifact-ab",
                policy_id="legacy-residual", policy_version=1, basis_units=10000,
                unit_domain="paper_point", event_time="2026-02-01T00:00:00+00:00",
            )
            replayed = RoyaltyLedger(path, policy_owner="governance-owner")
            self.assertEqual(replayed.snapshot()["payables"]["author-a|paper_point"], 600)
            self.assertEqual(replayed.snapshot()["origins"]["artifact-a"]["origin_actor"], "author-a")

    def test_supersession_preserves_original_lineage_and_claim_history(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = setup_ledger(Path(directory) / "royalties.jsonl")
            ledger.register_derivative(
                event_id="derivative-v2", artifact_id="artifact-ab-v2",
                content_digest=sha("combined-v2"), author_actor="builder-v2",
                parents=[{"artifact_id": "artifact-ab", "weight_bps": 10000, "lineage_ref": "commit-ab:merge", "evidence_digest": sha("range-ab")}],
            )
            ledger.supersede(
                event_id="supersede-event", supersession_id="supersede-1",
                prior_artifact_id="artifact-ab", replacement_artifact_id="artifact-ab-v2",
                reason="optimized upgrade", evidence_digest=sha("supersession-proof"),
            )
            snap = ledger.snapshot()
            self.assertEqual(snap["supersessions"]["artifact-ab"]["replacement_artifact_id"], "artifact-ab-v2")
            self.assertEqual(snap["derivatives"]["artifact-ab-v2"]["lineage"]["artifact-a"]["share_bps"], 6000)


if __name__ == "__main__":
    unittest.main()
