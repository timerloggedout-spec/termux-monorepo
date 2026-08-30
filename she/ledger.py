"""SHE P0.11 — append-only evidence ledger (observer-only, no persist)."""
from __future__ import annotations
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any
from she.incident import Incident, IncidentState
from she.learn import LearningRecord, plan_learning
from she.promote import PromotionDecision, plan_promotion
from she.verify import DUAL_GATES, VerificationPlan, apply_check_results, plan_verification, summarize_results
ENTRY_KINDS=frozenset({"incident","verification","promotion","learning"})
_TERMINAL_BLOCK={IncidentState.QUARANTINED,IncidentState.ABANDONED}
class LedgerError(ValueError): pass
def live_ledger_enabled(): return os.environ.get("SHE_LEDGER_LIVE","").strip()=="1"
def _is_security(i):
    c=(i.classification or "").lower(); fp=i.fingerprint or ""
    return c.startswith("dependabot-") or fp.startswith("dependabot:")
@dataclass(frozen=True)
class LedgerEntry:
    kind:str; ref:str; sha:str; summary:str; metadata:dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if self.kind not in ENTRY_KINDS: raise LedgerError(f"unknown entry kind: {self.kind!r}")
        if not self.ref or not self.sha: raise LedgerError("entry ref and sha required")
    def to_mapping(self): return {"kind":self.kind,"ref":self.ref,"sha":self.sha,"summary":self.summary,"metadata":dict(self.metadata)}
    @classmethod
    def from_mapping(cls,d): return cls(str(d["kind"]),str(d.get("ref") or ""),str(d.get("sha") or ""),str(d.get("summary") or ""),dict(d.get("metadata") or {}))
@dataclass(frozen=True)
class EvidenceLedger:
    incident_id:str; sha:str; required_gates:tuple[str,...]; entries:tuple[LedgerEntry,...]; promotion_decision:str; persisted:bool=False; live:bool=False; mutates_source:bool=False; constraints:tuple[str,...]=(); metadata:dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not self.incident_id or not self.sha: raise LedgerError("incident identity and sha required")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise LedgerError("dual gates repo-gate + termux-smoke must be required")
        if "incident" not in [e.kind for e in self.entries]: raise LedgerError("ledger must include an incident entry")
        if any(e.sha!=self.sha for e in self.entries): raise LedgerError("entry sha must match ledger sha")
        if self.live or self.persisted or self.mutates_source: raise LedgerError("P0.11 planner cannot be live, persisted, or mutate source")
    def to_mapping(self): return {"incident_id":self.incident_id,"sha":self.sha,"required_gates":list(self.required_gates),"entries":[e.to_mapping() for e in self.entries],"promotion_decision":self.promotion_decision,"persisted":self.persisted,"live":self.live,"mutates_source":self.mutates_source,"constraints":list(self.constraints),"metadata":dict(self.metadata)}
    @classmethod
    def from_mapping(cls,d):
        raw=d.get("entries") or ()
        if not isinstance(raw,Sequence) or isinstance(raw,(str,bytes)): raise LedgerError("entries must be a sequence")
        return cls(str(d["incident_id"]),str(d.get("sha") or ""),tuple(str(x) for x in (d.get("required_gates") or ())),tuple(LedgerEntry.from_mapping(x) for x in raw),"hold",False,False,False,tuple(str(x) for x in (d.get("constraints") or ("from_mapping_fail_closed",))),dict(d.get("metadata") or {}))
def plan_ledger(incident:Incident,*,verification:VerificationPlan|None=None,promotion:PromotionDecision|None=None,learning:LearningRecord|None=None,check_results:Mapping[str,Mapping[str,Any]]|None=None)->EvidenceLedger:
    if incident.state in _TERMINAL_BLOCK: raise LedgerError(f"ledger not applicable for terminal state {incident.state.value}")
    verification=verification or plan_verification(incident)
    if check_results: verification=apply_check_results(verification,check_results)
    if verification.incident_id!=incident.incident_id or verification.sha!=incident.sha: raise LedgerError("verification identity/SHA must match incident")
    promotion=promotion or plan_promotion(incident,verification=verification,check_results=check_results)
    if promotion.incident_id!=incident.incident_id or promotion.sha!=incident.sha: raise LedgerError("promotion identity/SHA must match incident")
    learning=learning or plan_learning(incident,verification=verification)
    if learning.incident_id!=incident.incident_id or learning.sha!=incident.sha: raise LedgerError("learning identity/SHA must match incident")
    required=set(verification.required_gates())|set(promotion.required_gates)|DUAL_GATES
    if _is_security(incident): required.add("security-checks")
    entries=(LedgerEntry("incident",incident.incident_id,incident.sha,f"{incident.state.value}:{incident.classification}",{"fingerprint":incident.fingerprint,"source":incident.source}),LedgerEntry("verification",incident.incident_id,incident.sha,summarize_results(verification),{"promotion_ready":verification.promotion_ready}),LedgerEntry("promotion",incident.incident_id,incident.sha,promotion.decision,{"promotion_ready":promotion.promotion_ready,"reasons":list(promotion.reasons)}),LedgerEntry("learning",incident.incident_id,incident.sha,learning.outcome,{"reusable":learning.reusable}))
    return EvidenceLedger(incident.incident_id,incident.sha,tuple(sorted(required)),entries,"observe-only" if _is_security(incident) else promotion.decision,False,False,False,("dual_gates_required","append_only","no_persist","no_live_store","no_git_mutation","security_observe_only","subset_required_gates","child_plans_must_match"),{"classification":incident.classification,"fingerprint":incident.fingerprint,"source":incident.source,"state":incident.state.value,"security":_is_security(incident),"verification_ready":verification.promotion_ready,"live_flag_honored":live_ledger_enabled()})
