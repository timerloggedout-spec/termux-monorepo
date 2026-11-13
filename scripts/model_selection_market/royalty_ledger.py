"""Origin-attributed residual royalty journal (MSM-025).

This is a separate append-only liability ledger. It records claims and settlement
evidence; it never moves wallet funds, signs transactions, or changes MSM balances.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .accounting import EventStore, _Already, append, canonical, replay
except ImportError:
    from accounting import EventStore, _Already, append, canonical, replay

BPS = 10_000
MAX_UNITS = 2**63 - 1
UNIT_DOMAINS = {"paper_point", "test_token", "production_asset"}


class RoyaltyLedgerError(ValueError):
    """Raised when a royalty event violates lineage or accounting policy."""


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise RoyaltyLedgerError(f"{field} must be a non-empty trimmed string")
    return value


def _integer(value: Any, field: str, low: int = 0, high: int = MAX_UNITS) -> int:
    if type(value) is not int or not low <= value <= high:
        raise RoyaltyLedgerError(f"{field} must be an integer in [{low}, {high}]")
    return value


def _digest(value: Any, field: str) -> str:
    value = _text(value, field)
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise RoyaltyLedgerError(f"{field} must be a lowercase SHA-256 digest")
    return value


def _time(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(_text(value, field).replace("Z", "+00:00"))
    except ValueError as exc:
        raise RoyaltyLedgerError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise RoyaltyLedgerError(f"{field} must include a timezone")
    return parsed


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _allocate(total: int, weights: dict[str, int]) -> dict[str, int]:
    """Largest-remainder allocation with stable lexical tie-breaking."""
    if total == 0:
        return {key: 0 for key in sorted(weights)}
    denominator = sum(weights.values())
    if denominator <= 0:
        raise RoyaltyLedgerError("allocation weights must sum above zero")
    result = {key: (total * weight) // denominator for key, weight in weights.items()}
    remainder = total - sum(result.values())
    order = sorted(weights, key=lambda key: (-(total * weights[key] % denominator), key))
    for key in order[:remainder]:
        result[key] += 1
    return result


def _empty() -> dict[str, Any]:
    return {
        "origins": {}, "derivatives": {}, "artifacts": {}, "policies": {}, "contributions": {}, "settlement_keys": {},
        "accruals": {}, "payables": {}, "settlements": {}, "reversals": {},
        "disputes": {}, "supersessions": {}, "supersession_ids": {}, "ids": {},
    }


class RoyaltyLedger:
    """Independent append-only journal for origin royalties and payable claims."""

    def __init__(self, event_path: str | Path, *, policy_owner: str):
        self.store = EventStore(event_path)
        self.policy_owner = _text(policy_owner, "policy_owner")
        with self.store.locked():
            self._refresh()

    def _refresh(self) -> None:
        self.events = replay(self.store.path)
        self.state = self._reduce(self.events)

    @staticmethod
    def _lineage(parent_rows: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, dict[str, Any]]:
        if not isinstance(parent_rows, list) or not parent_rows:
            raise RoyaltyLedgerError("parents must be a non-empty array")
        parent_ids = set()
        inherited: dict[str, dict[str, Any]] = {}
        weights = {}
        for row in parent_rows:
            if not isinstance(row, dict) or set(row) != {"artifact_id", "weight_bps", "lineage_ref", "evidence_digest"}:
                raise RoyaltyLedgerError("each parent requires artifact_id and weight_bps")
            artifact_id = _text(row["artifact_id"], "parent.artifact_id")
            weight = _integer(row["weight_bps"], "parent.weight_bps", 1, BPS)
            _text(row["lineage_ref"], "parent.lineage_ref")
            _digest(row["evidence_digest"], "parent.evidence_digest")
            if artifact_id in parent_ids or artifact_id not in state["artifacts"]:
                raise RoyaltyLedgerError("parent artifacts must be known and unique")
            parent_ids.add(artifact_id)
            weights[artifact_id] = weight
            inherited[artifact_id] = state["artifacts"][artifact_id]["lineage"]
        if sum(weights.values()) != BPS:
            raise RoyaltyLedgerError("parent weights must sum to 10000 basis points")
        numerators: dict[str, int] = {}
        beneficiaries: dict[str, str] = {}
        for parent_id, parent_weight in weights.items():
            for origin_id, origin in inherited[parent_id].items():
                beneficiaries[origin_id] = origin["beneficiary"]
                numerators[origin_id] = numerators.get(origin_id, 0) + parent_weight * origin["share_bps"]
        shares = _allocate(BPS, numerators)
        return {
            origin_id: {"beneficiary": beneficiaries[origin_id], "share_bps": share}
            for origin_id, share in sorted(shares.items()) if share
        }

    def _reduce(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        state = _empty()
        for index, event in enumerate(events, 1):
            expected = {"version", "seq", "event_id", "type", "payload", "timestamp", "correlation_id"}
            if (set(event) != expected or type(event["version"]) is not int or event["version"] != 1
                    or type(event["seq"]) is not int or event["seq"] != index):
                raise RoyaltyLedgerError(f"invalid royalty event envelope at sequence {index}")
            event_id = _text(event["event_id"], "event_id")
            typ = _text(event["type"], "event.type")
            payload = event["payload"]
            if not isinstance(payload, dict) or event_id in state["ids"]:
                raise RoyaltyLedgerError("invalid payload or duplicate event ID")
            _time(event["timestamp"], "event.timestamp")
            _text(event["correlation_id"], "event.correlation_id")

            if typ == "origin_register":
                if set(payload) != {"artifact_id", "content_digest", "origin_actor"}:
                    raise RoyaltyLedgerError("invalid origin_register payload")
                artifact = _text(payload["artifact_id"], "artifact_id")
                actor = _text(payload["origin_actor"], "origin_actor")
                content = _digest(payload["content_digest"], "content_digest")
                if artifact in state["artifacts"]:
                    raise RoyaltyLedgerError("artifact identity already registered")
                row = {"artifact_id": artifact, "content_digest": content, "origin_actor": actor}
                state["origins"][artifact] = row
                state["artifacts"][artifact] = {
                    "content_digest": content, "lineage": {artifact: {"beneficiary": actor, "share_bps": BPS}}
                }
            elif typ == "derivative_register":
                if set(payload) != {"artifact_id", "content_digest", "author_actor", "parents"}:
                    raise RoyaltyLedgerError("invalid derivative_register payload")
                artifact = _text(payload["artifact_id"], "artifact_id")
                content = _digest(payload["content_digest"], "content_digest")
                author = _text(payload["author_actor"], "author_actor")
                if artifact in state["artifacts"]:
                    raise RoyaltyLedgerError("artifact identity already registered")
                lineage = self._lineage(payload["parents"], state)
                state["derivatives"][artifact] = {
                    "artifact_id": artifact, "content_digest": content,
                    "author_actor": author, "parents": payload["parents"],
                    "lineage": lineage,
                }
                state["artifacts"][artifact] = {"content_digest": content, "lineage": lineage}
            elif typ == "policy_activate":
                if set(payload) != {"policy_id", "version", "rate_bps", "basis_definition",
                                    "effective_from", "effective_until", "approved_by",
                                    "approved_at", "approval_digest"}:
                    raise RoyaltyLedgerError("invalid policy_activate payload")
                policy_id = _text(payload["policy_id"], "policy_id")
                version = _integer(payload["version"], "version", 1, 2**31 - 1)
                rate = _integer(payload["rate_bps"], "rate_bps", 0, BPS)
                basis = _text(payload["basis_definition"], "basis_definition")
                if len(basis) > 128:
                    raise RoyaltyLedgerError("basis_definition exceeds 128 characters")
                start = _time(payload["effective_from"], "effective_from")
                end = _time(payload["effective_until"], "effective_until") if payload["effective_until"] is not None else None
                if end and end <= start:
                    raise RoyaltyLedgerError("effective_until must follow effective_from")
                approved = _text(payload["approved_by"], "approved_by")
                if approved != self.policy_owner:
                    raise RoyaltyLedgerError("policy event lacks configured owner approval")
                _time(payload["approved_at"], "approved_at")
                approval_digest = _digest(payload["approval_digest"], "approval_digest")
                key = f"{policy_id}@{version}"
                if key in state["policies"]:
                    raise RoyaltyLedgerError("policy version already activated")
                prior_versions = [prior for prior in state["policies"].values()
                                  if prior["policy_id"] == policy_id]
                if prior_versions and version != max(prior["version"] for prior in prior_versions) + 1:
                    raise RoyaltyLedgerError("policy versions must increase sequentially")
                for prior in prior_versions:
                    prior_start = datetime.fromisoformat(prior["effective_from"])
                    prior_end = datetime.fromisoformat(prior["effective_until"]) if prior["effective_until"] else None
                    if (end is None or prior_start < end) and (prior_end is None or start < prior_end):
                        raise RoyaltyLedgerError("policy versions for one policy cannot have overlapping effective intervals")
                state["policies"][key] = {
                    "policy_id": policy_id, "version": version, "rate_bps": rate,
                    "basis_definition": basis, "effective_from": start.isoformat(),
                    "effective_until": end.isoformat() if end else None,
                    "approved_by": approved, "approval_digest": approval_digest,
                }
            elif typ == "policy_close":
                if set(payload) != {"policy_id", "version", "effective_until", "approved_by",
                                    "approved_at", "approval_digest"}:
                    raise RoyaltyLedgerError("invalid policy_close payload")
                policy_id = _text(payload["policy_id"], "policy_id")
                version = _integer(payload["version"], "version", 1, 2**31 - 1)
                key = f"{policy_id}@{version}"
                policy = state["policies"].get(key)
                if policy is None or policy["effective_until"] is not None:
                    raise RoyaltyLedgerError("policy version is unknown or already closed")
                end = _time(payload["effective_until"], "effective_until")
                start = datetime.fromisoformat(policy["effective_from"])
                if end <= start:
                    raise RoyaltyLedgerError("policy close must follow its effective start")
                approved = _text(payload["approved_by"], "approved_by")
                if approved != self.policy_owner:
                    raise RoyaltyLedgerError("policy close requires configured owner approval")
                approved_at = _time(payload["approved_at"], "approved_at")
                if end < approved_at:
                    raise RoyaltyLedgerError("policy close cannot predate its approval")
                for accrual in state["accruals"].values():
                    if (accrual["policy_key"] == key
                            and datetime.fromisoformat(accrual["event_time"]) >= end):
                        raise RoyaltyLedgerError("policy close would exclude an already-recorded accrual")
                _digest(payload["approval_digest"], "approval_digest")
                policy["effective_until"] = end.isoformat()
            elif typ == "royalty_accrual":
                if set(payload) != {"accrual_id", "contribution_id", "derivative_artifact_id",
                                    "policy_id", "policy_version", "basis_definition", "basis_units",
                                    "unit_domain", "event_time", "eligibility_decision_ref",
                                    "eligibility_evidence_digest"}:
                    raise RoyaltyLedgerError("invalid royalty_accrual payload")
                accrual_id = _text(payload["accrual_id"], "accrual_id")
                contribution = _text(payload["contribution_id"], "contribution_id")
                artifact = _text(payload["derivative_artifact_id"], "derivative_artifact_id")
                if (accrual_id in state["accruals"] or contribution in state["contributions"]
                        or artifact not in state["derivatives"]):
                    raise RoyaltyLedgerError("accrual ID, contribution ID, or derivative artifact is invalid")
                policy_key = f'{_text(payload["policy_id"], "policy_id")}@{_integer(payload["policy_version"], "policy_version", 1)}'
                policy = state["policies"].get(policy_key)
                if policy is None:
                    raise RoyaltyLedgerError("accrual requires an activated policy version")
                event_time = _time(payload["event_time"], "event_time")
                if event_time < datetime.fromisoformat(policy["effective_from"]):
                    raise RoyaltyLedgerError("accrual precedes policy effective interval")
                if policy["effective_until"] and event_time >= datetime.fromisoformat(policy["effective_until"]):
                    raise RoyaltyLedgerError("accrual falls outside policy effective interval")
                basis_definition = _text(payload["basis_definition"], "basis_definition")
                if basis_definition != policy["basis_definition"]:
                    raise RoyaltyLedgerError("accrual basis does not match the activated policy")
                basis = _integer(payload["basis_units"], "basis_units", 1)
                eligibility_ref = _text(payload["eligibility_decision_ref"], "eligibility_decision_ref")
                eligibility_digest = _digest(payload["eligibility_evidence_digest"], "eligibility_evidence_digest")
                domain = _text(payload["unit_domain"], "unit_domain")
                if domain not in UNIT_DOMAINS:
                    raise RoyaltyLedgerError("unsupported royalty unit domain")
                total = (basis * policy["rate_bps"]) // BPS
                lineage = state["artifacts"][artifact]["lineage"]
                shares = {origin_id: origin["share_bps"] for origin_id, origin in lineage.items()}
                allocations = _allocate(total, shares)
                claims = {
                    origin_id: {"beneficiary": lineage[origin_id]["beneficiary"], "units": units,
                                "settled": 0, "reversed": 0}
                    for origin_id, units in allocations.items() if units
                }
                state["contributions"][contribution] = accrual_id
                state["accruals"][accrual_id] = {
                    "contribution_id": contribution, "derivative_artifact_id": artifact,
                    "policy_key": policy_key, "event_time": event_time.isoformat(),
                    "basis_definition": basis_definition, "basis_units": basis, "unit_domain": domain,
                    "eligibility_decision_ref": eligibility_ref,
                    "eligibility_evidence_digest": eligibility_digest,
                    "royalty_units": total, "claims": claims, "disputed": False,
                }
                for claim in claims.values():
                    key = (claim["beneficiary"], domain)
                    updated = state["payables"].get(key, 0) + claim["units"]
                    if updated > MAX_UNITS:
                        raise RoyaltyLedgerError("origin payable exceeds the supported integer range")
                    state["payables"][key] = updated
            elif typ == "royalty_settlement":
                if set(payload) != {"settlement_id", "accrual_id", "origin_artifact_id", "units",
                                    "destination", "evidence_digest", "idempotency_key"}:
                    raise RoyaltyLedgerError("invalid royalty_settlement payload")
                settlement_id = _text(payload["settlement_id"], "settlement_id")
                accrual_id = _text(payload["accrual_id"], "accrual_id")
                origin_id = _text(payload["origin_artifact_id"], "origin_artifact_id")
                units = _integer(payload["units"], "units", 1)
                destination = _text(payload["destination"], "destination")
                evidence = _digest(payload["evidence_digest"], "evidence_digest")
                idem = _text(payload["idempotency_key"], "idempotency_key")
                accrual = state["accruals"].get(accrual_id)
                if (settlement_id in state["settlements"] or idem in state["settlement_keys"]
                        or accrual is None or accrual["disputed"]):
                    raise RoyaltyLedgerError("settlement is duplicate, unknown, or disputed")
                claim = accrual["claims"].get(origin_id)
                if claim is None or units > claim["units"] - claim["settled"] - claim["reversed"]:
                    raise RoyaltyLedgerError("settlement exceeds the origin's payable claim")
                claim["settled"] += units
                key = (claim["beneficiary"], accrual["unit_domain"])
                state["payables"][key] -= units
                state["settlement_keys"][idem] = settlement_id
                state["settlements"][settlement_id] = {
                    "accrual_id": accrual_id, "origin_artifact_id": origin_id,
                    "units": units, "destination": destination,
                    "evidence_digest": evidence, "idempotency_key": idem,
                }
            elif typ == "royalty_reversal":
                if set(payload) != {"reversal_id", "accrual_id", "origin_artifact_id", "units",
                                    "reason", "evidence_digest"}:
                    raise RoyaltyLedgerError("invalid royalty_reversal payload")
                reversal_id = _text(payload["reversal_id"], "reversal_id")
                accrual_id = _text(payload["accrual_id"], "accrual_id")
                origin_id = _text(payload["origin_artifact_id"], "origin_artifact_id")
                units = _integer(payload["units"], "units", 1)
                reason = _text(payload["reason"], "reason")
                evidence = _digest(payload["evidence_digest"], "evidence_digest")
                accrual = state["accruals"].get(accrual_id)
                if reversal_id in state["reversals"] or accrual is None:
                    raise RoyaltyLedgerError("reversal is duplicate or accrual is unknown")
                claim = accrual["claims"].get(origin_id)
                if claim is None or units > claim["units"] - claim["settled"] - claim["reversed"]:
                    raise RoyaltyLedgerError("reversal exceeds the unsettled payable claim")
                claim["reversed"] += units
                key = (claim["beneficiary"], accrual["unit_domain"])
                state["payables"][key] -= units
                state["reversals"][reversal_id] = {
                    "accrual_id": accrual_id, "origin_artifact_id": origin_id,
                    "units": units, "reason": reason, "evidence_digest": evidence,
                }
            elif typ == "royalty_dispute":
                if set(payload) != {"dispute_id", "accrual_id", "reason", "evidence_digest"}:
                    raise RoyaltyLedgerError("invalid royalty_dispute payload")
                dispute_id = _text(payload["dispute_id"], "dispute_id")
                accrual_id = _text(payload["accrual_id"], "accrual_id")
                reason = _text(payload["reason"], "reason")
                evidence = _digest(payload["evidence_digest"], "evidence_digest")
                if dispute_id in state["disputes"] or accrual_id not in state["accruals"]:
                    raise RoyaltyLedgerError("dispute ID or accrual is invalid")
                state["accruals"][accrual_id]["disputed"] = True
                state["disputes"][dispute_id] = {
                    "accrual_id": accrual_id, "reason": reason, "evidence_digest": evidence,
                }
            elif typ == "lineage_supersede":
                if set(payload) != {"supersession_id", "prior_artifact_id", "replacement_artifact_id",
                                    "reason", "evidence_digest"}:
                    raise RoyaltyLedgerError("invalid lineage_supersede payload")
                sid = _text(payload["supersession_id"], "supersession_id")
                prior = _text(payload["prior_artifact_id"], "prior_artifact_id")
                replacement = _text(payload["replacement_artifact_id"], "replacement_artifact_id")
                reason = _text(payload["reason"], "reason")
                evidence = _digest(payload["evidence_digest"], "evidence_digest")
                if sid in state["supersession_ids"] or prior not in state["artifacts"] or replacement not in state["derivatives"] or prior == replacement:
                    raise RoyaltyLedgerError("invalid supersession reference")
                if prior in state["supersessions"]:
                    raise RoyaltyLedgerError("artifact already has a superseding artifact")
                cursor = replacement
                while cursor in state["supersessions"]:
                    cursor = state["supersessions"][cursor]["replacement_artifact_id"]
                    if cursor == prior:
                        raise RoyaltyLedgerError("lineage supersession cycle detected")
                state["supersessions"][prior] = {
                    "replacement_artifact_id": replacement, "reason": reason,
                    "evidence_digest": evidence, "supersession_id": sid,
                }
            else:
                raise RoyaltyLedgerError(f"unsupported royalty event type: {typ}")
            correlation_fields = {
                "origin_register": payload.get("artifact_id"),
                "derivative_register": payload.get("artifact_id"),
                "policy_activate": f'{payload.get("policy_id")}@{payload.get("version")}',
                "policy_close": f'{payload.get("policy_id")}@{payload.get("version")}',
                "royalty_accrual": payload.get("accrual_id"),
                "royalty_settlement": payload.get("settlement_id"),
                "royalty_reversal": payload.get("reversal_id"),
                "royalty_dispute": payload.get("dispute_id"),
                "lineage_supersede": payload.get("supersession_id"),
            }
            if event["correlation_id"] != correlation_fields.get(typ):
                raise RoyaltyLedgerError("event correlation does not match its royalty operation")
            state["ids"][event_id] = {"type": typ, "payload": payload}
        return state

    def _mutate(self, event_id: str, event_type: str, payload: dict[str, Any], correlation_id: str):
        event_id = _text(event_id, "event_id")
        correlation_id = _text(correlation_id, "correlation_id")
        event = {
            "event_id": event_id, "type": event_type, "payload": payload,
            "timestamp": _now(), "correlation_id": correlation_id,
        }
        with self.store.locked():
            self._refresh()
            prior = next((row for row in self.events if row["event_id"] == event_id), None)
            if prior is not None:
                if (prior["type"] != event_type or prior["payload"] != payload
                        or prior["correlation_id"] != correlation_id):
                    raise RoyaltyLedgerError("event_id already used with different intent")
                return prior
            candidate = dict(event, version=1, seq=len(self.events) + 1)
            self._reduce(self.events + [candidate])
            try:
                append(self.store.path, self.events, event)
            except _Already as already:
                return already.event
            self._refresh()
            return self.events[-1]

    def register_origin(self, *, event_id: str, artifact_id: str, content_digest: str, origin_actor: str):
        payload = {"artifact_id": _text(artifact_id, "artifact_id"),
                   "content_digest": _digest(content_digest, "content_digest"),
                   "origin_actor": _text(origin_actor, "origin_actor")}
        return self._mutate(event_id, "origin_register", payload, payload["artifact_id"])

    def register_derivative(self, *, event_id: str, artifact_id: str, content_digest: str,
                            author_actor: str, parents: list[dict[str, Any]]):
        payload = {"artifact_id": _text(artifact_id, "artifact_id"),
                   "content_digest": _digest(content_digest, "content_digest"),
                   "author_actor": _text(author_actor, "author_actor"), "parents": parents}
        return self._mutate(event_id, "derivative_register", payload, payload["artifact_id"])

    def activate_policy(self, *, event_id: str, policy_id: str, version: int, rate_bps: int,
                        effective_from: str, approved_by: str, approved_at: str,
                        approval_digest: str, basis_definition: str,
                        effective_until: str | None = None):
        if approved_by != self.policy_owner:
            raise RoyaltyLedgerError("policy activation requires the configured owner")
        payload = {"policy_id": _text(policy_id, "policy_id"),
                   "version": _integer(version, "version", 1, 2**31 - 1),
                   "rate_bps": _integer(rate_bps, "rate_bps", 0, BPS),
                   "basis_definition": _text(basis_definition, "basis_definition"),
                   "effective_from": _text(effective_from, "effective_from"),
                   "effective_until": effective_until, "approved_by": approved_by,
                   "approved_at": _text(approved_at, "approved_at"),
                   "approval_digest": _digest(approval_digest, "approval_digest")}
        return self._mutate(event_id, "policy_activate", payload, f'{policy_id}@{version}')

    def close_policy(self, *, event_id: str, policy_id: str, version: int,
                     effective_until: str, approved_by: str, approved_at: str,
                     approval_digest: str):
        if approved_by != self.policy_owner:
            raise RoyaltyLedgerError("policy close requires the configured owner")
        payload = {"policy_id": _text(policy_id, "policy_id"),
                   "version": _integer(version, "version", 1, 2**31 - 1),
                   "effective_until": _text(effective_until, "effective_until"),
                   "approved_by": approved_by,
                   "approved_at": _text(approved_at, "approved_at"),
                   "approval_digest": _digest(approval_digest, "approval_digest")}
        return self._mutate(event_id, "policy_close", payload, f'{policy_id}@{version}')

    def accrue(self, *, event_id: str, accrual_id: str, contribution_id: str,
               derivative_artifact_id: str, policy_id: str, policy_version: int,
               basis_definition: str, basis_units: int, unit_domain: str, event_time: str,
               eligibility_decision_ref: str, eligibility_evidence_digest: str):
        payload = {"accrual_id": _text(accrual_id, "accrual_id"),
                   "contribution_id": _text(contribution_id, "contribution_id"),
                   "derivative_artifact_id": _text(derivative_artifact_id, "derivative_artifact_id"),
                   "policy_id": _text(policy_id, "policy_id"),
                   "policy_version": _integer(policy_version, "policy_version", 1),
                   "basis_definition": _text(basis_definition, "basis_definition"),
                   "basis_units": _integer(basis_units, "basis_units", 1),
                   "unit_domain": _text(unit_domain, "unit_domain"),
                   "event_time": _text(event_time, "event_time"),
                   "eligibility_decision_ref": _text(eligibility_decision_ref, "eligibility_decision_ref"),
                   "eligibility_evidence_digest": _digest(eligibility_evidence_digest, "eligibility_evidence_digest")}
        return self._mutate(event_id, "royalty_accrual", payload, payload["accrual_id"])

    def settle(self, *, event_id: str, settlement_id: str, accrual_id: str,
               origin_artifact_id: str, units: int, destination: str,
               evidence_digest: str, idempotency_key: str):
        payload = {"settlement_id": _text(settlement_id, "settlement_id"),
                   "accrual_id": _text(accrual_id, "accrual_id"),
                   "origin_artifact_id": _text(origin_artifact_id, "origin_artifact_id"),
                   "units": _integer(units, "units", 1),
                   "destination": _text(destination, "destination"),
                   "evidence_digest": _digest(evidence_digest, "evidence_digest"),
                   "idempotency_key": _text(idempotency_key, "idempotency_key")}
        return self._mutate(event_id, "royalty_settlement", payload, payload["settlement_id"])

    def reverse(self, *, event_id: str, reversal_id: str, accrual_id: str,
                origin_artifact_id: str, units: int, reason: str, evidence_digest: str):
        payload = {"reversal_id": _text(reversal_id, "reversal_id"),
                   "accrual_id": _text(accrual_id, "accrual_id"),
                   "origin_artifact_id": _text(origin_artifact_id, "origin_artifact_id"),
                   "units": _integer(units, "units", 1), "reason": _text(reason, "reason"),
                   "evidence_digest": _digest(evidence_digest, "evidence_digest")}
        return self._mutate(event_id, "royalty_reversal", payload, payload["reversal_id"])

    def dispute(self, *, event_id: str, dispute_id: str, accrual_id: str,
                reason: str, evidence_digest: str):
        payload = {"dispute_id": _text(dispute_id, "dispute_id"),
                   "accrual_id": _text(accrual_id, "accrual_id"),
                   "reason": _text(reason, "reason"),
                   "evidence_digest": _digest(evidence_digest, "evidence_digest")}
        return self._mutate(event_id, "royalty_dispute", payload, payload["dispute_id"])

    def supersede(self, *, event_id: str, supersession_id: str, prior_artifact_id: str,
                  replacement_artifact_id: str, reason: str, evidence_digest: str):
        payload = {"supersession_id": _text(supersession_id, "supersession_id"),
                   "prior_artifact_id": _text(prior_artifact_id, "prior_artifact_id"),
                   "replacement_artifact_id": _text(replacement_artifact_id, "replacement_artifact_id"),
                   "reason": _text(reason, "reason"),
                   "evidence_digest": _digest(evidence_digest, "evidence_digest")}
        return self._mutate(event_id, "lineage_supersede", payload, payload["supersession_id"])

    def snapshot(self) -> dict[str, Any]:
        with self.store.locked():
            self._refresh()
            return {
                "origins": self.state["origins"],
                "derivatives": self.state["derivatives"],
                "policies": self.state["policies"],
                "accruals": self.state["accruals"],
                "payables": {f"{actor}|{domain}": units
                             for (actor, domain), units in sorted(self.state["payables"].items())},
                "settlements": self.state["settlements"],
                "reversals": self.state["reversals"],
                "disputes": self.state["disputes"],
                "supersessions": self.state["supersessions"],
                "event_count": len(self.events),
                "event_digest": hashlib.sha256(
                    "".join(canonical(event) + "\n" for event in self.events).encode("utf-8")
                ).hexdigest(),
            }
