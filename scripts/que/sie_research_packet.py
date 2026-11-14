#!/usr/bin/env python3
"""Build evidence-bounded SIE research packets for the Oracle Method generator."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sie_pipeline

SCHEMA = "que.sie-research-packet/v1"
EVIDENCE_SCHEMA = "delphi-evidence-set/v1"
GENERATOR = "scripts/delphi/generate_proposal.py oracle-method-generator/v1"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def oracle_method_digest(value: Any) -> str:
    """Match the existing Oracle Method generator's evidence-set hash encoding."""
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires a timezone")
    return parsed


def evidence_index(evidence_sets: list[dict], at: datetime) -> tuple[dict[str, dict], dict[str, str]]:
    """Index only intact, fresh evidence claims; retain a reason for every rejected claim."""
    accepted: dict[str, dict] = {}
    rejected: dict[str, str] = {}
    for evidence_set in evidence_sets:
        if not isinstance(evidence_set, dict) or evidence_set.get("schema") != EVIDENCE_SCHEMA:
            raise ValueError("evidence set schema must be delphi-evidence-set/v1")
        items = evidence_set.get("items")
        if not isinstance(items, list):
            raise ValueError("evidence set items must be an array")
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("evidence items must be objects")
            claim = item.get("claim")
            if not isinstance(claim, str) or not claim.strip():
                continue
            provenance = item.get("provenance") or {}
            path = provenance.get("path")
            payload = {"claim": claim, "value": item.get("value"), "path": path}
            expected = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
            if not isinstance(path, str) or not path or item.get("sha256") != expected:
                rejected[claim] = "integrity_mismatch"
                continue
            try:
                observed_at = parse_time(provenance.get("observed_at", ""))
                fresh_until = parse_time(item.get("fresh_until", ""))
                fresh = observed_at <= at <= fresh_until
            except (TypeError, ValueError):
                fresh = False
            if not fresh:
                rejected[claim] = "stale_or_invalid_freshness"
                continue
            if claim in accepted:
                accepted.pop(claim, None)
                rejected[claim] = "duplicate_claim"
            elif claim not in rejected:
                accepted[claim] = item


def _validate_diagnosis(diagnosis: dict) -> None:
    if not isinstance(diagnosis, dict):
        raise ValueError("diagnosis must be an object")
    required = ("summary", "owner_role", "confirmed_facts", "hypotheses",
                "unknowns", "baseline", "related_history", "replay_recipe",
                "acceptance_tests", "risk_envelope", "alternatives")
    for key in required:
        if key not in diagnosis:
            raise ValueError(f"diagnosis missing {key}")
    for key in ("confirmed_facts", "hypotheses", "unknowns", "related_history",
                "replay_recipe", "acceptance_tests", "alternatives"):
        if not isinstance(diagnosis[key], list):
            raise ValueError(f"diagnosis.{key} must be an array")
    if not isinstance(diagnosis["summary"], str) or not diagnosis["summary"].strip():
        raise ValueError("diagnosis.summary must be non-empty")
    if not isinstance(diagnosis["owner_role"], str) or not diagnosis["owner_role"].strip():
        raise ValueError("diagnosis.owner_role must be non-empty")
    if not isinstance(diagnosis["baseline"], dict):
        raise ValueError("diagnosis.baseline must be an object")
    if not diagnosis["confirmed_facts"]:
        raise ValueError("diagnosis requires at least one confirmed-fact candidate")
    if not diagnosis["replay_recipe"] or not diagnosis["acceptance_tests"]:
        raise ValueError("diagnosis requires replay steps and acceptance tests")
    if not diagnosis["alternatives"]:
        raise ValueError("diagnosis requires alternatives for Oracle Method plan")
    if not isinstance(diagnosis["risk_envelope"], dict) or not diagnosis["risk_envelope"]:
        raise ValueError("diagnosis requires a populated risk envelope")
    if "risks" in diagnosis["risk_envelope"] and (
            not isinstance(diagnosis["risk_envelope"]["risks"], list)
            or not diagnosis["risk_envelope"]["risks"]):
        raise ValueError("diagnosis risk_envelope.risks must be a non-empty array")
    for fact in diagnosis["confirmed_facts"] + diagnosis["hypotheses"]:
        if not isinstance(fact, dict) or not isinstance(fact.get("text"), str) or not fact["text"].strip():
            raise ValueError("facts and hypotheses require non-empty text")
        if not isinstance(fact.get("evidence_refs", []), list):
            raise ValueError("fact evidence_refs must be an array")


def build_research_packet(*, source_receipt: dict, diagnosis: dict,
                          evidence_sets: list[dict],
                          generated_at: str | None = None) -> tuple[dict, dict, list[dict]]:
    """Return (packet, Oracle Method brief, fresh evidence sets)."""
    receipt_errors = sie_pipeline.validate_receipt(source_receipt)
    if receipt_errors:
        raise ValueError("invalid SIE source receipt: " + "; ".join(receipt_errors))
    _validate_diagnosis(diagnosis)
    generated_at = generated_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    at = parse_time(generated_at)
    accepted, rejected = evidence_index(evidence_sets, at)

    facts = []
    unverified = []
    summary_points = []
    for fact in diagnosis["confirmed_facts"]:
        refs = fact.get("evidence_refs") or []
        missing = [ref for ref in refs if ref not in accepted]
        row = {"text": fact["text"], "evidence_refs": refs}
        if refs and not missing:
            facts.append(row)
            summary_points.append({"text": "Confirmed: " + fact["text"], "evidence_refs": refs})
        else:
            for ref in missing:
                rejected.setdefault(ref, "missing_claim")
            reasons = {ref: rejected[ref] for ref in missing}
            unverified.append({**row, "disposition": reasons})
            summary_points.append({"text": "Unverified: " + fact["text"], "evidence_refs": []})

    for hypothesis in diagnosis["hypotheses"]:
        summary_points.append({"text": "Hypothesis: " + hypothesis["text"], "evidence_refs": []})
    for unknown in diagnosis["unknowns"]:
        summary_points.append({"text": "Unknown: " + str(unknown), "evidence_refs": []})

    fresh_sets = []
    evidence_manifest = []
    for evidence_set in evidence_sets:
        fresh_items = [item for item in evidence_set.get("items", [])
                       if item.get("claim") in accepted and accepted[item["claim"]] is item]
        if not fresh_items:
            continue
        fresh_set = {**evidence_set, "items": fresh_items, "material": len(fresh_items) >= 2}
        fresh_sets.append(fresh_set)
        evidence_manifest.append({
            "artifact": evidence_set.get("artifact"),
            "source_set_digest": oracle_method_digest(evidence_set),
            "fresh_subset_digest": oracle_method_digest(fresh_set),
            "accepted_claims": [item["claim"] for item in fresh_items],
        })

    if not facts:
        raise ValueError("research packet requires at least one confirmed fact with fresh, intact evidence")

    source = source_receipt.get("source") or {}
    source_id = source.get("id", "")
    related_issues = (
        [int(source_id)]
        if source.get("kind") in {"queue_item", "stall_gap"}
        and re.fullmatch(r"\d+", str(source_id))
        else []
    )
    risks = diagnosis["risk_envelope"].get("risks") or [
        f"{key}: {value}" for key, value in diagnosis["risk_envelope"].items()
    ]
    brief_id = "que-sie-" + source_receipt["item_key"]
    brief = {
        "id": brief_id,
        "title": f"QUE SIE research and repair brief — {source_receipt['item_key']}",
        "kind": "research",
        "surface": "QUE SIE",
        "priority": diagnosis.get("priority", "P1"),
        "related_issues": related_issues,
        "executive_request": (
            "Research objective: " + diagnosis["summary"]
            + "\n\nOwner role: " + str(diagnosis["owner_role"])
            + "\n\nBaseline candidate (provisional until source-linked): " + json.dumps(diagnosis["baseline"], sort_keys=True)
            + "\n\nRelated history candidates (verify refs before reliance): " + json.dumps(diagnosis["related_history"], sort_keys=True)
        ),
        "summary_points": summary_points,
        "items": [{"item": test, "state": "proposed",
                   "evidence": "Pass the replay recipe against the pinned source revision."}
                  for test in diagnosis["acceptance_tests"]],
        "require_plan": True,
        "plan": {
            "steps": diagnosis["replay_recipe"],
            "risks": risks,
            "alternatives": diagnosis["alternatives"],
        },
    }

    packet = {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "source_receipt": source_receipt,
        "diagnosis": diagnosis,
        "confirmed_facts": facts,
        "unverified_facts": unverified,
        "evidence": {
            "sets": evidence_manifest,
            "accepted_claims": sorted(accepted),
            "rejected_claims": rejected,
        },
        "oracle_method": {
            "generator": GENERATOR,
            "brief": brief,
            "evidence_set_digests": [oracle_method_digest(item) for item in fresh_sets],
        },
    }
    packet["package_digest"] = digest(packet)
    return packet, brief, fresh_sets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a QUE SIE research packet and Oracle Method brief")
    parser.add_argument("--receipt", required=True, help="SIE stage receipt JSON")
    parser.add_argument("--diagnosis", required=True, help="Research diagnosis JSON")
    parser.add_argument("--evidence", action="append", default=[], help="Delphi evidence-set JSON path (repeatable)")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--generated-at", help="Fixed ISO timestamp for reproducible packet builds")
    args = parser.parse_args(argv)

    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    diagnosis = json.loads(Path(args.diagnosis).read_text(encoding="utf-8"))
    evidence_sets = [json.loads(Path(path).read_text(encoding="utf-8"))
                     for path in args.evidence]
    packet, brief, fresh_sets = build_research_packet(
        source_receipt=receipt, diagnosis=diagnosis,
        evidence_sets=evidence_sets, generated_at=args.generated_at,
    )
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "research-packet.json").write_text(
        json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "oracle-brief.json").write_text(
        json.dumps(brief, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    evidence_dir = out / "evidence"
    if evidence_dir.is_symlink():
        raise ValueError("managed evidence output directory must not be a symlink")
    evidence_dir.mkdir(exist_ok=True)
    # Remove only files owned by this generator; keep unrelated operator notes/artifacts.
    for stale in evidence_dir.iterdir():
        if re.fullmatch(r"evidence-\d{3}\.json", stale.name) and (stale.is_file() or stale.is_symlink()):
            stale.unlink()
    for index, evidence_set in enumerate(fresh_sets, start=1):
        (evidence_dir / f"evidence-{index:03d}.json").write_text(
            json.dumps(evidence_set, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
    print(f"research packet ready: {packet['package_digest']} "
          f"brief={brief['id']} evidence_sets={len(fresh_sets)}")
    print("Run scripts/delphi/generate_proposal.py with oracle-brief.json and each fresh evidence file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
