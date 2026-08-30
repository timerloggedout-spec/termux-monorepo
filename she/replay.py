"""SHE P0.13 — attestation replay verifier (observer-only)."""
from __future__ import annotations
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from she.attest import Attestation, digest_mapping, plan_attestation
from she.incident import Incident, IncidentState
from she.ledger import EvidenceLedger, plan_ledger
from she.verify import DUAL_GATES
VERDICTS=frozenset({"match","mismatch","observe-only","hold"})
_TERMINAL_BLOCK={IncidentState.QUARANTINED,IncidentState.ABANDONED}
class ReplayError(ValueError): pass
def live_replay_enabled(): return os.environ.get("SHE_REPLAY_LIVE","").strip()=="1"
def _is_security(i):
    c=(i.classification or "").lower(); fp=i.fingerprint or ""
    return c.startswith("dependabot-") or fp.startswith("dependabot:")
@dataclass(frozen=True)
class ReplayVerdict:
    incident_id:str; sha:str; required_gates:tuple[str,...]; expected_digest:str; observed_digest:str; verdict:str; promotion_decision:str="hold"; live:bool=False; persisted:bool=False; signed:bool=False; mutates_source:bool=False; constraints:tuple[str,...]=(); metadata:dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not self.incident_id or not self.sha: raise ReplayError("incident identity and sha required")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise ReplayError("dual gates repo-gate + termux-smoke must be required")
        if self.verdict not in VERDICTS: raise ReplayError(f"unsupported verdict: {self.verdict!r}")
        if len(self.expected_digest)!=64 or len(self.observed_digest)!=64: raise ReplayError("digests must be sha256 hex")
        if self.live or self.persisted or self.signed or self.mutates_source: raise ReplayError("P0.13 planner cannot be live, persisted, signed, or mutate source")
    def to_mapping(self): return {"incident_id":self.incident_id,"sha":self.sha,"required_gates":list(self.required_gates),"expected_digest":self.expected_digest,"observed_digest":self.observed_digest,"verdict":self.verdict,"promotion_decision":self.promotion_decision,"live":self.live,"persisted":self.persisted,"signed":self.signed,"mutates_source":self.mutates_source,"constraints":list(self.constraints),"metadata":dict(self.metadata)}
    @classmethod
    def from_mapping(cls,d): return cls(str(d["incident_id"]),str(d.get("sha") or ""),tuple(str(x) for x in (d.get("required_gates") or ())),str(d.get("expected_digest") or ""),str(d.get("observed_digest") or ""),"hold","hold",False,False,False,False,tuple(str(x) for x in (d.get("constraints") or ("from_mapping_fail_closed",))),dict(d.get("metadata") or {}))
def plan_replay(incident:Incident,*,attestation:Attestation|None=None,ledger:EvidenceLedger|None=None,check_results:Mapping[str,Mapping[str,Any]]|None=None)->ReplayVerdict:
    if incident.state in _TERMINAL_BLOCK: raise ReplayError(f"replay not applicable for terminal state {incident.state.value}")
    ledger=ledger or plan_ledger(incident,check_results=check_results)
    if ledger.incident_id!=incident.incident_id or ledger.sha!=incident.sha: raise ReplayError("ledger identity/SHA must match incident")
    attestation=attestation or plan_attestation(incident,ledger=ledger,check_results=check_results)
    if attestation.incident_id!=incident.incident_id or attestation.sha!=incident.sha: raise ReplayError("attestation identity/SHA must match incident")
    required=set(ledger.required_gates)|set(attestation.required_gates)|DUAL_GATES
    security=_is_security(incident)
    if security: required.add("security-checks")
    payload={"incident_id":incident.incident_id,"sha":incident.sha,"required_gates":sorted(required),"ledger":ledger.to_mapping()}
    observed=digest_mapping(payload); expected=attestation.digest; matched=observed==expected
    verdict="observe-only" if security else ("match" if matched else "mismatch")
    decision="observe-only" if security else (attestation.promotion_decision if matched else "hold")
    return ReplayVerdict(incident.incident_id,incident.sha,tuple(sorted(required)),expected,observed,verdict,decision,False,False,False,False,("dual_gates_required","canonical_sha256","no_sign","no_persist","no_live_store","no_git_mutation","security_observe_only","subset_required_gates","child_ledger_must_match","child_attestation_must_match"),{"classification":incident.classification,"fingerprint":incident.fingerprint,"source":incident.source,"state":incident.state.value,"security":security,"matched":matched,"attestation_decision":attestation.promotion_decision,"live_flag_honored":live_replay_enabled()})
