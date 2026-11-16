"""SHE P0.9 — evolutionary-repair planner (L2 contract, no live mutation).

Novel failures produce competing hypotheses, isolated experiment specs,
benchmarks, and candidate repairs. Promotion stays gated: this module
plans. It does not mutate git, dispatch workers, or merge.

Live evolution is a later slice behind SHE_EVOLVE_LIVE=1.
stdlib-only. No network.
"""
from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from she.incident import Incident, IncidentState
from she.repair_pr import REQUIRED_TESTS, plan_repair_pr
from she.sandbox import SandboxPlan, plan_repair_sandbox
from she.verify import DUAL_GATES, VerificationPlan, plan_verification

HYPOTHESIS_KINDS: frozenset[str] = frozenset(
    {
        "retry-known-fix",
        "narrow-regression",
        "isolate-flaky-gate",
        "capability-mismatch",
        "environment-drift",
    }
)

_TERMINAL_BLOCK = {
    IncidentState.LEARNED,
    IncidentState.QUARANTINED,
    IncidentState.ABANDONED,
}


class EvolveError(ValueError):
    """Invalid evolutionary-repair construction or policy violation."""


def live_evolve_enabled() -> bool:
    """Live evolution remains gated and unused in P0.9."""
    return os.environ.get("SHE_EVOLVE_LIVE", "").strip() == "1"


def _is_security(incident: Incident) -> bool:
    classification = (incident.classification or "").lower()
    fp = incident.fingerprint or ""
    return classification.startswith("dependabot-") or fp.startswith("dependabot:")


@dataclass(frozen=True)
class Hypothesis:
    """One competing repair hypothesis for a novel failure."""

    kind: str
    rationale: str
    required_gates: tuple[str, ...]
    isolated: bool = True
    selected: bool = False

    def __post_init__(self) -> None:
        if self.kind not in HYPOTHESIS_KINDS:
            raise EvolveError(f"unknown hypothesis kind: {self.kind!r}")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise EvolveError("dual gates repo-gate + termux-smoke must be required")
        if not self.isolated:
            raise EvolveError("hypotheses must stay isolated")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "rationale": self.rationale,
            "required_gates": list(self.required_gates),
            "isolated": self.isolated,
            "selected": self.selected,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Hypothesis:
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        return cls(
            kind=str(data.get("kind") or ""),
            rationale=str(data.get("rationale") or ""),
            required_gates=gates,
            isolated=True,
            selected=False,
        )


@dataclass(frozen=True)
class ExperimentSpec:
    """Isolated experiment that may later become a candidate repair."""

    hypothesis_kind: str
    branch: str
    benchmark: str
    required_gates: tuple[str, ...]
    live: bool = False
    mutates_source: bool = False
    promotion_ready: bool = False

    def __post_init__(self) -> None:
        if not self.branch.startswith("she/evolve/"):
            raise EvolveError("experiment branch must stay in she/evolve/ namespace")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise EvolveError("dual gates must remain required on experiments")
        if self.live or self.mutates_source or self.promotion_ready:
            raise EvolveError("P0.9 experiments cannot be live, mutating, or promotion-ready")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "hypothesis_kind": self.hypothesis_kind,
            "branch": self.branch,
            "benchmark": self.benchmark,
            "required_gates": list(self.required_gates),
            "live": self.live,
            "mutates_source": self.mutates_source,
            "promotion_ready": self.promotion_ready,
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> ExperimentSpec:
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        return cls(
            hypothesis_kind=str(data.get("hypothesis_kind") or ""),
            branch=str(data.get("branch") or ""),
            benchmark=str(data.get("benchmark") or ""),
            required_gates=gates,
            live=False,
            mutates_source=False,
            promotion_ready=False,
        )


@dataclass(frozen=True)
class EvolutionPlan:
    """Inspectable L2 evolutionary-repair contract for one incident."""

    incident_id: str
    sha: str
    hypotheses: tuple[Hypothesis, ...]
    experiments: tuple[ExperimentSpec, ...]
    required_gates: tuple[str, ...]
    selected_kind: str = ""
    live: bool = False
    mutates_source: bool = False
    promotion_ready: bool = False
    constraints: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.incident_id:
            raise EvolveError("incident_id required")
        if not self.sha:
            raise EvolveError("sha required")
        needed = set(self.required_gates)
        if not DUAL_GATES.issubset(needed):
            raise EvolveError("dual gates repo-gate + termux-smoke must be required")
        if self.live or self.mutates_source or self.promotion_ready:
            raise EvolveError("P0.9 planner cannot be live, mutating, or promotion-ready")
        kinds = {h.kind for h in self.hypotheses}
        if self.selected_kind and self.selected_kind not in kinds:
            raise EvolveError("selected_kind must name a planned hypothesis")
        if len(self.experiments) != len(self.hypotheses):
            raise EvolveError("each hypothesis must have exactly one experiment")

    def to_mapping(self) -> dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "sha": self.sha,
            "hypotheses": [h.to_mapping() for h in self.hypotheses],
            "experiments": [e.to_mapping() for e in self.experiments],
            "required_gates": list(self.required_gates),
            "selected_kind": self.selected_kind,
            "live": self.live,
            "mutates_source": self.mutates_source,
            "promotion_ready": self.promotion_ready,
            "constraints": list(self.constraints),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> EvolutionPlan:
        hyps = tuple(Hypothesis.from_mapping(x) for x in (data.get("hypotheses") or ()))
        exps = tuple(ExperimentSpec.from_mapping(x) for x in (data.get("experiments") or ()))
        gates = tuple(str(x) for x in (data.get("required_gates") or ()))
        return cls(
            incident_id=str(data["incident_id"]),
            sha=str(data.get("sha") or ""),
            hypotheses=hyps,
            experiments=exps,
            required_gates=gates,
            selected_kind=str(data.get("selected_kind") or ""),
            live=False,
            mutates_source=False,
            promotion_ready=False,
            constraints=tuple(str(x) for x in (data.get("constraints") or ())),
            metadata=dict(data.get("metadata") or {}),
        )


def _hypotheses_for(incident: Incident, gates: Sequence[str]) -> tuple[Hypothesis, ...]:
    classification = (incident.classification or "unknown").lower()
    fp = incident.fingerprint or classification
    required = tuple(sorted(set(gates) | DUAL_GATES | REQUIRED_TESTS))
    specs = (
        ("retry-known-fix", f"retry known pattern for {fp}"),
        ("narrow-regression", f"narrow regression around {classification}"),
        ("isolate-flaky-gate", "isolate flake vs deterministic gate failure"),
        ("capability-mismatch", "worker capability subset vs required authority"),
        ("environment-drift", "termux vs Actions environment drift"),
    )
    return tuple(
        Hypothesis(
            kind=kind,
            rationale=rationale,
            required_gates=required,
            isolated=True,
            selected=False,
        )
        for kind, rationale in specs
    )


def _experiments_for(
    incident: Incident,
    hypotheses: Sequence[Hypothesis],
    sandbox: SandboxPlan,
) -> tuple[ExperimentSpec, ...]:
    gates = tuple(sorted(DUAL_GATES | REQUIRED_TESTS))
    out: list[ExperimentSpec] = []
    for hyp in hypotheses:
        slug = hyp.kind.replace("-", "_")
        out.append(
            ExperimentSpec(
                hypothesis_kind=hyp.kind,
                branch=f"she/evolve/{incident.incident_id}/{slug}",
                benchmark=f"file://{sandbox.evidence_dir}/evolve-{slug}.txt",
                required_gates=gates,
                live=False,
                mutates_source=False,
                promotion_ready=False,
            )
        )
    return tuple(out)


def _bind_children(
    incident: Incident,
    sandbox: SandboxPlan,
    verification: VerificationPlan,
) -> None:
    if sandbox.incident_id != incident.incident_id:
        raise EvolveError("sandbox incident_id must match incident")
    if sandbox.base_sha != incident.sha:
        raise EvolveError("sandbox base_sha must match incident sha")
    if verification.incident_id != incident.incident_id:
        raise EvolveError("verification incident_id must match incident")
    if verification.sha != incident.sha:
        raise EvolveError("verification sha must match incident sha")


def plan_evolution(
    incident: Incident,
    *,
    sandbox: SandboxPlan | None = None,
    verification: VerificationPlan | None = None,
) -> EvolutionPlan:
    """Plan competing isolated experiments. Does not mutate source.

    Dual gates are always required (subset). Security/Dependabot stay
    observe-only. promotion_ready stays false until a later executor
    records passing dual-gate evidence against the current SHA.
    """
    if incident.state in _TERMINAL_BLOCK:
        raise EvolveError(
            f"evolution not applicable for terminal state {incident.state.value}"
        )
    if _is_security(incident):
        raise EvolveError("security/dependabot incidents are observe-only")

    sandbox = sandbox or plan_repair_sandbox(incident)
    verification = verification or plan_verification(incident, sandbox=sandbox)
    _bind_children(incident, sandbox, verification)
    repair = plan_repair_pr(incident, sandbox=sandbox, verification=verification)
    gates = tuple(sorted(set(verification.required_gates()) | set(repair.required_tests) | DUAL_GATES))
    if not DUAL_GATES.issubset(gates):
        raise EvolveError("dual gates must remain required")

    hypotheses = _hypotheses_for(incident, gates)
    experiments = _experiments_for(incident, hypotheses, sandbox)
    return EvolutionPlan(
        incident_id=incident.incident_id,
        sha=incident.sha,
        hypotheses=hypotheses,
        experiments=experiments,
        required_gates=gates,
        selected_kind="",
        live=False,
        mutates_source=False,
        promotion_ready=False,
        constraints=(
            "dual_gates_required",
            "isolated_experiments_only",
            "no_live_evolution",
            "no_source_mutation",
            "security_observe_only",
            "promotion_requires_verified_success",
            "append_only_evidence",
        ),
        metadata={
            "classification": incident.classification,
            "fingerprint": incident.fingerprint,
            "source": incident.source,
            "state": incident.state.value,
            "repository": incident.repository,
            "sandbox_branch": sandbox.branch,
            "repair_branch": repair.branch,
            "verification_ready": verification.promotion_ready,
            "live_flag_honored": live_evolve_enabled(),
            "hypothesis_count": len(hypotheses),
        },
    )
