"""SHE P0.9 — evolutionary-repair planner (L2 contract, no live mutation)."""
from __future__ import annotations
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any
from she.incident import Incident, IncidentState
from she.repair_pr import REQUIRED_TESTS, plan_repair_pr
from she.sandbox import SandboxPlan, plan_repair_sandbox
from she.verify import DUAL_GATES, VerificationPlan, plan_verification
HYPOTHESIS_KINDS=frozenset({"retry-known-fix","narrow-regression","isolate-flaky-gate","capability-mismatch","environment-drift"})
_TERMINAL_BLOCK={IncidentState.LEARNED,IncidentState.QUARANTINED,IncidentState.ABANDONED}
class EvolveError(ValueError): pass
def live_evolve_enabled(): return os.environ.get("SHE_EVOLVE_LIVE","").strip()=="1"
def _is_security(i):
    c=(i.classification or "").lower(); fp=i.fingerprint or ""
    return c.startswith("dependabot-") or fp.startswith("dependabot:")
@dataclass(frozen=True)
class Hypothesis:
    kind:str; rationale:str; required_gates:tuple[str,...]; isolated:bool=True; selected:bool=False
    def __post_init__(self):
        if self.kind not in HYPOTHESIS_KINDS: raise EvolveError(f"unknown hypothesis kind: {self.kind!r}")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise EvolveError("dual gates repo-gate + termux-smoke must be required")
        if not self.isolated: raise EvolveError("hypotheses must stay isolated")
    def to_mapping(self): return {"kind":self.kind,"rationale":self.rationale,"required_gates":list(self.required_gates),"isolated":self.isolated,"selected":self.selected}
    @classmethod
    def from_mapping(cls,d): return cls(str(d.get("kind") or ""),str(d.get("rationale") or ""),tuple(str(x) for x in (d.get("required_gates") or ())),True,False)
@dataclass(frozen=True)
class ExperimentSpec:
    hypothesis_kind:str; branch:str; benchmark:str; required_gates:tuple[str,...]; live:bool=False; mutates_source:bool=False; promotion_ready:bool=False
    def __post_init__(self):
        if not self.branch.startswith("she/evolve/"): raise EvolveError("experiment branch must stay in she/evolve/ namespace")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise EvolveError("dual gates must remain required on experiments")
        if self.live or self.mutates_source or self.promotion_ready: raise EvolveError("P0.9 experiments cannot be live, mutating, or promotion-ready")
    def to_mapping(self): return {"hypothesis_kind":self.hypothesis_kind,"branch":self.branch,"benchmark":self.benchmark,"required_gates":list(self.required_gates),"live":self.live,"mutates_source":self.mutates_source,"promotion_ready":self.promotion_ready}
    @classmethod
    def from_mapping(cls,d): return cls(str(d.get("hypothesis_kind") or ""),str(d.get("branch") or ""),str(d.get("benchmark") or ""),tuple(str(x) for x in (d.get("required_gates") or ())),False,False,False)
@dataclass(frozen=True)
class EvolutionPlan:
    incident_id:str; sha:str; hypotheses:tuple[Hypothesis,...]; experiments:tuple[ExperimentSpec,...]; required_gates:tuple[str,...]; selected_kind:str=""; live:bool=False; mutates_source:bool=False; promotion_ready:bool=False; constraints:tuple[str,...]=(); metadata:dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not self.incident_id or not self.sha: raise EvolveError("incident identity and sha required")
        if not DUAL_GATES.issubset(set(self.required_gates)): raise EvolveError("dual gates required")
        if self.live or self.mutates_source or self.promotion_ready: raise EvolveError("P0.9 planner cannot be live, mutating, or promotion-ready")
        if self.selected_kind and self.selected_kind not in {h.kind for h in self.hypotheses}: raise EvolveError("selected_kind must name a planned hypothesis")
        if len(self.experiments)!=len(self.hypotheses): raise EvolveError("each hypothesis must have exactly one experiment")
    def to_mapping(self): return {"incident_id":self.incident_id,"sha":self.sha,"hypotheses":[h.to_mapping() for h in self.hypotheses],"experiments":[e.to_mapping() for e in self.experiments],"required_gates":list(self.required_gates),"selected_kind":self.selected_kind,"live":self.live,"mutates_source":self.mutates_source,"promotion_ready":self.promotion_ready,"constraints":list(self.constraints),"metadata":dict(self.metadata)}
    @classmethod
    def from_mapping(cls,d): return cls(str(d["incident_id"]),str(d.get("sha") or ""),tuple(Hypothesis.from_mapping(x) for x in (d.get("hypotheses") or ())),tuple(ExperimentSpec.from_mapping(x) for x in (d.get("experiments") or ())),tuple(str(x) for x in (d.get("required_gates") or ())),str(d.get("selected_kind") or ""),False,False,False,tuple(str(x) for x in (d.get("constraints") or ())),dict(d.get("metadata") or {}))
def plan_evolution(incident:Incident,*,sandbox:SandboxPlan|None=None,verification:VerificationPlan|None=None)->EvolutionPlan:
    if incident.state in _TERMINAL_BLOCK: raise EvolveError(f"evolution not applicable for terminal state {incident.state.value}")
    if _is_security(incident): raise EvolveError("security/dependabot incidents are observe-only")
    sandbox=sandbox or plan_repair_sandbox(incident); verification=verification or plan_verification(incident,sandbox=sandbox)
    if sandbox.incident_id!=incident.incident_id or sandbox.base_sha!=incident.sha or verification.incident_id!=incident.incident_id or verification.sha!=incident.sha: raise EvolveError("child identity/SHA mismatch")
    repair=plan_repair_pr(incident,sandbox=sandbox,verification=verification)
    gates=tuple(sorted(set(verification.required_gates())|set(repair.required_tests)|DUAL_GATES))
    specs=(("retry-known-fix",f"retry known pattern for {incident.fingerprint or incident.classification}"),("narrow-regression",f"narrow regression around {incident.classification}"),("isolate-flaky-gate","isolate flake vs deterministic gate failure"),("capability-mismatch","worker capability subset vs required authority"),("environment-drift","termux vs Actions environment drift"))
    hyps=tuple(Hypothesis(k,r,gates,True,False) for k,r in specs)
    exps=tuple(ExperimentSpec(h.kind,f"she/evolve/{incident.incident_id}/{h.kind.replace('-','_')}",f"file://{sandbox.evidence_dir}/evolve-{h.kind}.txt",tuple(sorted(DUAL_GATES|REQUIRED_TESTS))) for h in hyps)
    return EvolutionPlan(incident.incident_id,incident.sha,hyps,exps,gates,"",False,False,False,("dual_gates_required","isolated_experiments_only","no_live_evolution","no_source_mutation","security_observe_only","promotion_requires_verified_success","append_only_evidence"),{"classification":incident.classification,"fingerprint":incident.fingerprint,"source":incident.source,"state":incident.state.value,"repository":incident.repository,"sandbox_branch":sandbox.branch,"repair_branch":repair.branch,"verification_ready":verification.promotion_ready,"live_flag_honored":live_evolve_enabled(),"hypothesis_count":len(hyps)})
