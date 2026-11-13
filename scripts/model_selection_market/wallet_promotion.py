"""Read-only wallet promotion preflight; validates policy without provisioning keys or wallets."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

SCHEMA_VERSION = 1
SIGNER_SCHEMES = ("vault://", "kms://", "hsm://", "test-hsm://")


class PromotionGateError(ValueError):
    """Raised when a wallet promotion manifest fails its policy gates."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise PromotionGateError(f"{field} must be a non-empty trimmed string")
    return value


def _digest(value: Any, field: str) -> str:
    value = _text(value, field)
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise PromotionGateError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _timestamp(value: Any, field: str) -> None:
    try:
        parsed = datetime.fromisoformat(_text(value, field))
    except ValueError as exc:
        raise PromotionGateError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise PromotionGateError(f"{field} must include a timezone")


def _positive_int(value: Any, field: str) -> int:
    if type(value) is not int or value <= 0 or value > 2**63 - 1:
        raise PromotionGateError(f"{field} must be a positive bounded integer")
    return value


def evaluate_wallet_manifest(
    manifest: dict[str, Any], *, production_chain_id: int, production_key_namespace: str
) -> dict[str, Any]:
    """Return a deterministic readiness receipt; perform zero network or key operations."""
    if not isinstance(manifest, dict):
        raise PromotionGateError("manifest must be an object")
    required = {"schema_version", "environment", "asset_class", "wallet", "chain", "limits", "controls", "approvals"}
    if set(manifest) != required:
        raise PromotionGateError("manifest fields must match wallet-promotion/v1")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != SCHEMA_VERSION:
        raise PromotionGateError("unsupported wallet promotion schema")
    environment = manifest["environment"]
    if environment not in ("testnet", "production"):
        raise PromotionGateError("environment must be testnet or production")
    expected_asset = "test_token" if environment == "testnet" else "production_asset"
    if manifest["asset_class"] != expected_asset:
        raise PromotionGateError("asset class must match the promotion environment")

    wallet = manifest["wallet"]
    chain = manifest["chain"]
    limits = manifest["limits"]
    controls = manifest["controls"]
    approvals = manifest["approvals"]
    if not isinstance(wallet, dict) or set(wallet) != {"wallet_id", "owner", "key_namespace", "signer_ref"}:
        raise PromotionGateError("wallet identity fields are incomplete or unknown")
    if not isinstance(chain, dict) or set(chain) != {"chain_id", "rpc_url"}:
        raise PromotionGateError("chain fields are incomplete or unknown")
    if not isinstance(limits, dict) or set(limits) != {"per_transaction", "daily", "lifetime"}:
        raise PromotionGateError("limit fields are incomplete or unknown")
    control_fields = {"dual_control", "revocation_ref", "recovery_ref", "reconciliation_ref", "monitoring_ref"}
    if environment == "production":
        control_fields |= {"custody_review_ref", "legal_review_ref"}
    if not isinstance(controls, dict) or set(controls) != control_fields:
        raise PromotionGateError("control fields are incomplete or unknown")

    _text(wallet["wallet_id"], "wallet.wallet_id")
    _text(wallet["owner"], "wallet.owner")
    namespace = _text(wallet["key_namespace"], "wallet.key_namespace")
    signer = _text(wallet["signer_ref"], "wallet.signer_ref")
    if not signer.startswith(SIGNER_SCHEMES):
        raise PromotionGateError("signer_ref must identify a vault, KMS, or HSM handle")
    handle = signer.split("://", 1)[1]
    lowered_signer = signer.lower()
    if (not handle or "-----begin" in lowered_signer or len(signer) > 512
            or any(marker in lowered_signer for marker in ("token=", "secret=", "private_key=", "api_key=", "password="))
            or re.fullmatch(r"(?:0x)?[0-9a-fA-F]{32,}", handle)):
        raise PromotionGateError("signer_ref must remain a bounded non-secret handle")

    chain_id = _positive_int(chain["chain_id"], "chain.chain_id")
    rpc_url = _text(chain["rpc_url"], "chain.rpc_url")
    parsed = urlsplit(rpc_url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise PromotionGateError("chain.rpc_url must be HTTPS without embedded credentials or query tokens")
    if type(production_chain_id) is not int or production_chain_id <= 0:
        raise PromotionGateError("production_chain_id must be a positive integer")
    production_key_namespace = _text(production_key_namespace, "production_key_namespace")
    if environment == "testnet":
        if chain_id == production_chain_id:
            raise PromotionGateError("testnet chain ID must differ from production")
        if namespace == production_key_namespace:
            raise PromotionGateError("testnet signer namespace must be isolated from production")
    else:
        if chain_id != production_chain_id or namespace != production_key_namespace:
            raise PromotionGateError("production chain and signer namespace must match the approved production profile")

    per_tx = _positive_int(limits["per_transaction"], "limits.per_transaction")
    daily = _positive_int(limits["daily"], "limits.daily")
    lifetime = _positive_int(limits["lifetime"], "limits.lifetime")
    if per_tx > daily or daily > lifetime:
        raise PromotionGateError("limits must satisfy per_transaction <= daily <= lifetime")

    if controls["dual_control"] is not True:
        raise PromotionGateError("dual control must be enabled")
    for field in control_fields - {"dual_control"}:
        _text(controls[field], f"controls.{field}")

    if not isinstance(approvals, list):
        raise PromotionGateError("approvals must be a list")
    required_roles = {"owner", "security"} if environment == "testnet" else {"owner", "security", "custody"}
    actors, roles = set(), set()
    role_actors = {}
    for approval in approvals:
        if not isinstance(approval, dict) or set(approval) != {"actor", "role", "approved_at", "evidence_digest"}:
            raise PromotionGateError("each approval requires actor, role, approved_at, evidence_digest")
        actor = _text(approval["actor"], "approval.actor")
        role = _text(approval["role"], "approval.role")
        if role not in ("owner", "security", "custody"):
            raise PromotionGateError("unsupported approval role")
        if actor in actors:
            raise PromotionGateError("approvers must be distinct actors")
        if role in role_actors:
            raise PromotionGateError("each approval role must have one accountable actor")
        _timestamp(approval["approved_at"], "approval.approved_at")
        _digest(approval["evidence_digest"], "approval.evidence_digest")
        actors.add(actor)
        roles.add(role)
        role_actors[role] = actor
    if role_actors.get("owner") != wallet["owner"]:
        raise PromotionGateError("owner approval actor must match wallet.owner")
    if not required_roles.issubset(roles):
        raise PromotionGateError("approval roles incomplete: " + ", ".join(sorted(required_roles - roles)))

    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return {
        "schema": "wallet-promotion-receipt/v1",
        "eligible": True,
        "environment": environment,
        "wallet_id": wallet["wallet_id"],
        "chain_id": chain_id,
        "key_namespace": namespace,
        "approval_roles": sorted(roles),
        "manifest_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "action": "preflight_only",
        "provisioning_performed": False,
        "signing_performed": False,
        "funding_performed": False,
    }

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--production-chain-id", type=int, required=True)
    parser.add_argument("--production-key-namespace", required=True)
    args = parser.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        receipt = evaluate_wallet_manifest(
            manifest, production_chain_id=args.production_chain_id,
            production_key_namespace=args.production_key_namespace)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(receipt, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
