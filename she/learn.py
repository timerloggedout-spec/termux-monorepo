"""SHE P0.8 — learning planner (provenance record, no persist)."""
from __future__ import annotations
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from she.incident import Incident, IncidentState
from she.verify import DUAL_GATES, VerificationPlan, plan_verification, summarize_results
OUTCOMES: frozenset[str] = frozenset({"success", "failure", "observe"})
_NO_LEARN = {IncidentState.QUARANTINED, IncidentState.ABANDONED}
class LearnError(ValueError): pass
def live_learn_enabled() -> bool: return os.environ.get("SHE_LEARN_LIVE", "").strip() == "1"
def _is_security(incident: Incident) -> bool:
    c=(incident.classification or "").lower(); fp=incident.fingerprint or ""
    return c.startswith("dependabot-") or fp.startswith("dependabot:")
@dataclass(frozen=True)
class LearningRecord:
    incident_id: str; sha: str; fingerprint: str; outcome: str; verification_summary: str
    reusable: bool=False; live: bool=False; persisted: bool=False; constraints: tuple[str,...]=(); metadata: dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not self.incident_id or not self.sha: raise LearnError("incident identity and sha required")
        if self.outcome not in OUTCOMES: raise LearnError(f"unknown outcome: {self.outcome!r}")
        if self.reusable and self.outcome != "success": raise LearnError("only success outcomes may be reusable")
        if self.live or self.persisted: raise LearnError("P0.8 planner cannot be live or persisted")
    def to_mapping(self): return {"incident_id":self.incident_id,"sha":self.sha,"fingerprint":self.fingerprint,"outcome":self.outcome,"verification_summary":self.verification_summary,"reusable":self.reusable,"live":self.live,"persisted":self.persisted,"constraints":list(self.constraints),"metadata":dict(self.metadata)}
    @classmethod
    def from_mapping(cls,data:Mapping[str,Any]): return cls(str(data["incident_id"]),str(data.get("sha") or ""),str(data.get("fingerprint") or ""),str(data.get("outcome") or "observe"),str(data.get("verification_summary") or ""),False,False,False,tuple(str(x) for x in (data.get("constraints") or ())),dict(data.get("metadata") or {}))
def plan_learning(incident: Incident, *, verification: VerificationPlan|None=None, outcome: str|None=None)->LearningRecord:
    if incident.state in _NO_LEARN: raise LearnError(f"learning not applicable for terminal state {incident.state.value}")
    verification=verification or plan_verification(incident)
    if verification.incident_id != incident.incident_id or verification.sha != incident.sha: raise LearnError("verification identity/SHA must match incident")
    if not DUAL_GATES.issubset(verification.required_gates()): raise LearnError("dual gates repo-gate + termux-smoke must be in verification")
    security=_is_security(incident)
    resolved="observe" if security else (outcome or ("success" if verification.promotion_ready else "failure"))
    if resolved not in OUTCOMES: raise LearnError(f"unknown outcome: {resolved!r}")
    if security and resolved != "observe": raise LearnError("security/dependabot incidents are observe-only")
    reusable=resolved=="success" and verification.promotion_ready and not security and not verification.live
    return LearningRecord(incident.incident_id,incident.sha,incident.fingerprint or incident.classification,resolved,summarize_results(verification),reusable,False,False,("dual_gates_required","no_persist","no_live_store","security_observe_only","reuse_requires_verified_success","append_only_evidence"),{"classification":incident.classification,"source":incident.source,"state":incident.state.value,"repository":incident.repository,"verification_ready":verification.promotion_ready,"live_flag_honored":live_learn_enabled()})
