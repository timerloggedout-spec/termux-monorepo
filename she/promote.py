"""SHE P0.10 — promotion-decision planner (observer-only, no live merge)."""
from __future__ import annotations
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from she.evolve import EvolutionPlan
from she.incident import Incident, IncidentState
from she.repair_pr import RepairPRPlan, plan_repair_pr
from she.verify import DUAL_GATES, VerificationPlan, apply_check_results, plan_verification
DECISIONS=frozenset({"hold","promote","observe-only"})
_TERMINAL_BLOCK={IncidentState.LEARNED,IncidentState.QUARANTINED,IncidentState.ABANDONED}
class PromotionError(ValueError): pass
def live_promote_enabled()->bool: return os.environ.get("SHE_PROMOTE_LIVE","").strip()=="1"
def _is_security(i:Incident)->bool:
    c=(i.classification or "").lower(); fp=i.fingerprint or ""
    return c.startswith("dependabot-") or fp.startswith("dependabot:")
@dataclass(frozen=True)
class PromotionDecision:
    incident_id:str; sha:str; decision:str; required_gates:tuple[str,...]; rollback_sha:str
    promotion_ready:bool=False; live:bool=False; mutates_source:bool=False; reasons:tuple[str,...]=(); constraints:tuple[str,...]=(); metadata:dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if self.decision not in DECISIONS: raise PromotionError(f"unknown decision: {self.decision!r}")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise PromotionError("dual gates repo-gate + termux-smoke must be required")
        if self.rollback_sha!=self.sha: raise PromotionError("rollback_sha must match sha")
        if not self.incident_id or not self.sha: raise PromotionError("incident identity and sha required")
        if self.live or self.mutates_source: raise PromotionError("P0.10 planner cannot be live or mutate source")
        if self.decision=="promote" and not self.promotion_ready: raise PromotionError("promote requires promotion_ready")
        if self.decision!="promote" and self.promotion_ready: raise PromotionError("non-promote decisions cannot be promotion_ready")
    def to_mapping(self): return {"incident_id":self.incident_id,"sha":self.sha,"decision":self.decision,"required_gates":list(self.required_gates),"rollback_sha":self.rollback_sha,"promotion_ready":self.promotion_ready,"live":self.live,"mutates_source":self.mutates_source,"reasons":list(self.reasons),"constraints":list(self.constraints),"metadata":dict(self.metadata)}
    @classmethod
    def from_mapping(cls,data:Mapping[str,Any]):
        sha=str(data.get("sha") or "")
        return cls(str(data["incident_id"]),sha,"hold",tuple(str(x) for x in (data.get("required_gates") or ())),str(data.get("rollback_sha") or sha),False,False,False,tuple(str(x) for x in (data.get("reasons") or ("from_mapping_fail_closed",))),tuple(str(x) for x in (data.get("constraints") or ())),dict(data.get("metadata") or {}))
def plan_promotion(incident:Incident,*,verification:VerificationPlan|None=None,repair:RepairPRPlan|None=None,evolution:EvolutionPlan|None=None,check_results:Mapping[str,Mapping[str,Any]]|None=None)->PromotionDecision:
    if incident.state in _TERMINAL_BLOCK: raise PromotionError(f"promotion not applicable for terminal state {incident.state.value}")
    if _is_security(incident): return PromotionDecision(incident.incident_id,incident.sha,"observe-only",tuple(sorted(DUAL_GATES|{"security-checks"})),incident.sha,False,False,False,("security_dependabot_observe_only",),("dual_gates_required","no_live_merge","http_200_is_not_pass"),{"classification":incident.classification,"fingerprint":incident.fingerprint,"live_flag_honored":live_promote_enabled()})
    verification=verification or plan_verification(incident)
    if check_results: verification=apply_check_results(verification,check_results)
    repair=repair or plan_repair_pr(incident,verification=verification)
    if verification.incident_id!=incident.incident_id or verification.sha!=incident.sha or repair.incident_id!=incident.incident_id or repair.sha!=incident.sha or repair.rollback_sha!=incident.sha: raise PromotionError("child plan identity/SHA mismatch")
    needed=set(verification.required_gates())|set(repair.required_tests)|DUAL_GATES
    if evolution is not None:
        if evolution.incident_id!=incident.incident_id or evolution.sha!=incident.sha: raise PromotionError("evolution identity/SHA mismatch")
        needed|=set(evolution.required_gates)
    reasons=[]
    if repair.live or verification.live: reasons.append("child_plan_live")
    if not verification.promotion_ready: reasons.append("verification_not_ready")
    if any(c.required and c.outcome in {"pending","inconclusive"} for c in verification.checks): reasons.append("required_gate_not_pass")
    if any(c.required and c.outcome=="fail" for c in verification.checks): reasons.append("required_gate_failed")
    if evolution is not None and not evolution.promotion_ready: reasons.append("evolution_not_promotion_ready")
    ready=verification.promotion_ready and not reasons and not live_promote_enabled()
    return PromotionDecision(incident.incident_id,incident.sha,"promote" if ready else "hold",tuple(sorted(needed)),incident.sha,ready,False,False,tuple(reasons) or (("all_required_gates_pass",) if ready else ("held",)),("dual_gates_required","no_live_merge","http_200_is_not_pass","rollback_sha_bound","subset_required_gates","child_plans_must_match","evolution_cannot_auto_promote"),{"classification":incident.classification,"fingerprint":incident.fingerprint,"source":incident.source,"state":incident.state.value,"repair_branch":repair.branch,"verification_ready":verification.promotion_ready,"evolution_bound":evolution is not None,"live_flag_honored":live_promote_enabled()})
