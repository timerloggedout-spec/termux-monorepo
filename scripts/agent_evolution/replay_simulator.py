"""Deterministic replay/evolution primitives for agent orchestration research.

This module implements a small, safe subset of the ideas behind AlphaEvolve and
Dream-RSI for this repository:

* completed discovery history is a replay-only simulator;
* policies are data/configuration, not self-modifying source code;
* an incumbent policy is always evaluated with candidates (non-regression on the
  replay objective);
* evaluation consumes recorded outcomes and performs no agent/provider calls;
* the evolutionary loop emits evidence suitable for the existing MVT/3L0 ledger.

It intentionally does not execute generated code, mutate the repository, or
perform autonomous online deployment. Promotion remains an external dual gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class DiscoveryNode:
    node_id: str
    parent_id: str | None
    score: float
    cost: float = 1.0
    terminal: bool = False
    action: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id is required")
        if self.cost < 0:
            raise ValueError("cost must be non-negative")


@dataclass(frozen=True)
class DiscoveryHistory:
    nodes: tuple[DiscoveryNode, ...]

    @classmethod
    def from_nodes(cls, nodes: Iterable[DiscoveryNode]) -> "DiscoveryHistory":
        materialized = tuple(nodes)
        ids = [node.node_id for node in materialized]
        if len(ids) != len(set(ids)):
            raise ValueError("discovery node IDs must be unique")
        known = set(ids)
        for node in materialized:
            if node.parent_id is not None and node.parent_id not in known:
                raise ValueError(f"unknown parent_id: {node.parent_id}")
        return cls(materialized)

    @classmethod
    def from_jsonl(cls, text: str) -> "DiscoveryHistory":
        nodes: list[DiscoveryNode] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            nodes.append(DiscoveryNode(
                node_id=raw["node_id"], parent_id=raw.get("parent_id"),
                score=float(raw["score"]), cost=float(raw.get("cost", 1.0)),
                terminal=bool(raw.get("terminal", False)), action=raw.get("action", ""),
                metadata=raw.get("metadata", {}),
            ))
        return cls.from_nodes(nodes)

    def to_jsonl(self) -> str:
        return "".join(json.dumps({
            "node_id": n.node_id, "parent_id": n.parent_id, "score": n.score,
            "cost": n.cost, "terminal": n.terminal, "action": n.action,
            "metadata": dict(n.metadata),
        }, sort_keys=True) + "\n" for n in self.nodes)


@dataclass(frozen=True)
class ExplorationPolicy:
    """A replayable exploration policy represented entirely as data."""

    max_active: int = 2
    min_score: float = float("-inf")
    stop_after_terminal: bool = False

    def __post_init__(self) -> None:
        if self.max_active < 1:
            raise ValueError("max_active must be >= 1")

    def canonical(self) -> str:
        return json.dumps({
            "max_active": self.max_active,
            "min_score": self.min_score,
            "stop_after_terminal": self.stop_after_terminal,
        }, sort_keys=True, separators=(",", ":"))

    @property
    def policy_id(self) -> str:
        return hashlib.sha256(self.canonical().encode()).hexdigest()[:16]


@dataclass(frozen=True)
class ReplayResult:
    policy_id: str
    score: float
    covered_nodes: tuple[str, ...]
    replay_cost: float
    terminal_count: int


@dataclass(frozen=True)
class PolicyCandidate:
    policy: ExplorationPolicy
    generation: int
    parent_policy_id: str | None = None


@dataclass(frozen=True)
class EvolutionConfig:
    generations: int = 3
    mutations_per_generation: int = 8
    min_improvement: float = 0.0


class ReplaySimulator:
    """Exact replay over realized history; it never invokes external execution."""

    def __init__(self, history: DiscoveryHistory):
        self.history = history
        self._children: dict[str | None, list[DiscoveryNode]] = {}
        for node in history.nodes:
            self._children.setdefault(node.parent_id, []).append(node)
        for children in self._children.values():
            children.sort(key=lambda n: (-n.score, n.node_id))

    def replay(self, policy: ExplorationPolicy) -> ReplayResult:
        frontier = list(self._children.get(None, ()))
        covered: list[str] = []
        score = 0.0
        cost = 0.0
        terminals = 0

        while frontier:
            frontier.sort(key=lambda n: (-n.score, n.node_id))
            batch = frontier[: policy.max_active]
            frontier = frontier[policy.max_active :]
            for node in batch:
                if node.score < policy.min_score:
                    continue
                covered.append(node.node_id)
                score += node.score
                cost += node.cost
                if node.terminal:
                    terminals += 1
                    if policy.stop_after_terminal:
                        return ReplayResult(policy.policy_id, score, tuple(covered), cost, terminals)
                else:
                    frontier.extend(self._children.get(node.node_id, ()))

        return ReplayResult(policy.policy_id, score, tuple(covered), cost, terminals)


class EvolutionEngine:
    """Evolve replay policies while keeping the incumbent in every generation."""

    def __init__(self, simulator: ReplaySimulator, config: EvolutionConfig | None = None):
        self.simulator = simulator
        self.config = config or EvolutionConfig()

    @staticmethod
    def _mutations(policy: ExplorationPolicy, generation: int, count: int) -> list[PolicyCandidate]:
        candidates: list[PolicyCandidate] = []
        values = [1, 2, 4, 8]
        for i in range(count):
            width = values[i % len(values)]
            if i % 3 == 0:
                child = ExplorationPolicy(width, policy.min_score, policy.stop_after_terminal)
            elif i % 3 == 1:
                child = ExplorationPolicy(policy.max_active, policy.min_score + 0.1 * (i + 1), policy.stop_after_terminal)
            else:
                child = ExplorationPolicy(policy.max_active, policy.min_score, not policy.stop_after_terminal)
            candidates.append(PolicyCandidate(child, generation, policy.policy_id))
        return candidates

    def evolve(self, incumbent: ExplorationPolicy) -> tuple[ExplorationPolicy, tuple[ReplayResult, ...]]:
        current = incumbent
        observations: list[ReplayResult] = []
        baseline = self.simulator.replay(current)
        observations.append(baseline)

        for generation in range(1, self.config.generations + 1):
            candidates = [PolicyCandidate(current, generation)]
            candidates.extend(self._mutations(current, generation, self.config.mutations_per_generation))
            results = [self.simulator.replay(c.policy) for c in candidates]
            observations.extend(results)
            best = max(results, key=lambda result: (result.score, -result.replay_cost, result.policy_id))
            if best.score >= baseline.score + self.config.min_improvement:
                # Recover the immutable policy by matching its ID; no source-code mutation occurs.
                current = next(c.policy for c in candidates if c.policy.policy_id == best.policy_id)
                baseline = best

        return current, tuple(observations)


def evidence_record(
    *,
    task: str,
    manager: str,
    policy: ExplorationPolicy,
    result: ReplayResult,
    history_size: int,
    online_execution: bool = False,
    provider: str | None = None,
    model: str | None = None,
    workflow_run: str | None = None,
    head_sha: str | None = None,
    cohort: str | None = None,
) -> dict[str, Any]:
    """Create a safe, attribution-friendly observation for the existing ledger."""
    return {
        "schema": "agent.replay-evolution.v1",
        "task": task,
        "manager": manager,
        "provider": provider,
        "model": model,
        "workflow_run": workflow_run,
        "head_sha": head_sha,
        "cohort": cohort,
        "policy_id": policy.policy_id,
        "history_nodes": history_size,
        "replay_score": result.score,
        "covered_nodes": len(result.covered_nodes),
        "replay_cost": result.replay_cost,
        "terminal_count": result.terminal_count,
        "execution": "online" if online_execution else "replay_only",
        "verification": (
            "recorded_outcomes_only"
            if not online_execution
            else "external_gate_required"
        ),
    }
