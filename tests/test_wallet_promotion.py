"""Offline wallet-promotion readiness gate tests."""
import copy
import hashlib
import unittest

from scripts.model_selection_market.wallet_promotion import PromotionGateError, evaluate_wallet_manifest

PROD_CHAIN = 1
PROD_NAMESPACE = "prod/msm"


def manifest():
    digest = hashlib.sha256(b"approval").hexdigest()
    return {
        "schema_version": 1,
        "environment": "testnet",
        "asset_class": "test_token",
        "wallet": {"wallet_id": "alice-test", "owner": "alice",
                   "key_namespace": "testnet/msm", "signer_ref": "test-hsm://wallets/alice-test"},
        "chain": {"chain_id": 11155111, "rpc_url": "https://rpc.testnet.example"},
        "limits": {"per_transaction": 10, "daily": 50, "lifetime": 100},
        "controls": {"dual_control": True, "revocation_ref": "policy:revoke-1",
                     "recovery_ref": "runbook:recover-1", "reconciliation_ref": "ledger:reconcile-1",
                     "monitoring_ref": "monitor:wallet-1"},
        "approvals": [
            {"actor": "owner-1", "role": "owner", "approved_at": "2026-11-13T12:00:00+00:00", "evidence_digest": digest},
            {"actor": "security-1", "role": "security", "approved_at": "2026-11-13T12:01:00+00:00", "evidence_digest": digest},
        ],
    }


class WalletPromotionTests(unittest.TestCase):
    def evaluate(self, value):
        return evaluate_wallet_manifest(value, production_chain_id=PROD_CHAIN,
                                        production_key_namespace=PROD_NAMESPACE)

    def test_testnet_manifest_passes_readiness_without_provisioning(self):
        receipt = self.evaluate(manifest())
        self.assertTrue(receipt["eligible"])
        self.assertEqual(receipt["action"], "preflight_only")
        self.assertFalse(receipt["provisioning_performed"])
        self.assertFalse(receipt["signing_performed"])
        self.assertFalse(receipt["funding_performed"])
        self.assertEqual(len(receipt["manifest_sha256"]), 64)

    def test_testnet_chain_and_signer_namespaces_are_isolated(self):
        value = manifest()
        value["chain"]["chain_id"] = PROD_CHAIN
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)
        value = manifest()
        value["wallet"]["key_namespace"] = PROD_NAMESPACE
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)

    def test_credentials_and_private_key_material_stay_out_of_manifest(self):
        value = manifest()
        value["wallet"]["signer_ref"] = "0x" + "a" * 64
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)
        value = manifest()
        value["chain"]["rpc_url"] = "https://user:password@rpc.testnet.example"
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)

    def test_caps_require_monotonic_bounds_and_exact_integers(self):
        value = manifest()
        value["limits"]["per_transaction"] = 51
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)
        value = manifest()
        value["limits"]["daily"] = True
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)

    def test_production_requires_production_profile_and_three_distinct_approvals(self):
        value = manifest()
        value["environment"] = "production"
        value["asset_class"] = "production_asset"
        value["wallet"]["key_namespace"] = PROD_NAMESPACE
        value["chain"]["chain_id"] = PROD_CHAIN
        value["controls"]["custody_review_ref"] = "review:custody"
        value["controls"]["legal_review_ref"] = "review:legal"
        value["approvals"].append({
            "actor": "custody-1", "role": "custody", "approved_at": "2026-11-13T12:02:00+00:00",
            "evidence_digest": hashlib.sha256(b"custody").hexdigest(),
        })
        receipt = self.evaluate(value)
        self.assertTrue(receipt["eligible"])
        self.assertEqual(receipt["environment"], "production")
        value["approvals"].pop()
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)

    def test_unknown_manifest_fields_fail_closed(self):
        value = manifest()
        value["auto_fund"] = True
        with self.assertRaises(PromotionGateError):
            self.evaluate(value)


if __name__ == "__main__":
    unittest.main()
