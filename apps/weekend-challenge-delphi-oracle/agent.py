"""The entry agent: Delphi Oracle (starting agent) + fetch_evidence (new tool).

Pattern: the Strands Decider shape — an agent that judges a proposed
action, with a tool it can call when the evidence it was handed is not
material. The decision kernel is the offline Oracle MVP itself
(``scripts/delphi/strands_oracle_mvp.py::deterministic_oracle``, merged
via PR #1620); this module adds the tool loop around it:

1. Judge the request on asserted evidence alone (claims are not
   material, so this normally yields ABSTAIN).
2. If the request names an artifact, call ``fetch_evidence`` and judge
   again on the fetched, provenance-stamped evidence set.
3. Consequential actions (merge, credential_mutation, deploy, ...)
   ESCALATE regardless of evidence — the oracle's class rule runs
   before evidence is weighed, in both passes.

Every run emits a receipt: both judgements, the evidence set (or why
there is none), the honest count of read-only API calls the tool made,
and ``deployment: False`` — the completion record runs locally; no AWS
account exists and none is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

from fetch_evidence import CountingTransport, fetch_evidence, github_transport

RECEIPT_SCHEMA = "weekend-challenge-delphi-agent-receipt/v1"


def _load_oracle():
    root = Path(__file__).resolve().parents[2]
    path = root / "scripts" / "delphi" / "strands_oracle_mvp.py"
    spec = importlib.util.spec_from_file_location("strands_oracle_mvp", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.deterministic_oracle


def _case(request: dict, evidence_refs: list[str], material: bool) -> dict:
    return {
        "id": request["id"],
        "action": request["action"],
        "risk_tier": request.get("risk_tier", "standard"),
        "evidence_refs": evidence_refs,
        "evidence_material": material,
        "untrusted_instruction": False,
    }


def run_agent(request: dict, transport=None, now: datetime | None = None) -> dict:
    """Run one decision request through the oracle + tool loop."""
    oracle = _load_oracle()
    counting = CountingTransport(transport or github_transport)
    now = now or datetime.now(timezone.utc)

    asserted_refs = [f"asserted:{request['id']}"] if request.get("asserted") else []
    decision_asserted = oracle(_case(request, asserted_refs, material=False))

    evidence_set = None
    decision_final = decision_asserted
    if request.get("artifact"):
        evidence_set = fetch_evidence(request["artifact"], transport=counting,
                                      now=now)
        fetched_refs = [it["provenance"]["path"] for it in evidence_set["items"]]
        decision_final = oracle(_case(request, fetched_refs,
                                      material=evidence_set["material"]))

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "request_id": request["id"],
        "action": request["action"],
        "decision_on_asserted_evidence": decision_asserted,
        "decision_final": decision_final,
        "evidence_set": evidence_set,
        "tool_calls": {"fetch_evidence": 1 if evidence_set else 0,
                       "read_only_api_calls": counting.calls},
        "external_calls": counting.calls,
        "deployment": False,
        "human_ballots_received": 0,
        "generated_at": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True).encode()).hexdigest()
    return receipt
