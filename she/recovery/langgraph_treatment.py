"""Optional LangGraph treatment for the deterministic escalation policy.

The graph is an orchestration adapter, not an authorization or execution layer.
It uses deterministic stub nodes only; provider/tool side effects remain outside
this module. Importing SHE does not require LangGraph to be installed.
"""
from __future__ import annotations

from typing import TypedDict

from she.recovery.escalation import (
    EscalationBudget,
    ExecutorCandidate,
    decide_escalation,
)


_HANDOFF_DECISIONS = frozenset({
    "HANDOFF_SPECIALIST",
    "HANDOFF_ALTERNATE_FAMILY",
    "INDEPENDENT_VERIFY",
})


class EscalationGraphState(TypedDict, total=False):
    classification: str
    budget: EscalationBudget
    candidates: tuple[ExecutorCandidate, ...]
    required_capabilities: tuple[str, ...]
    current_executor_ref: str | None
    current_family: str | None
    authorization_scope: tuple[str, ...]
    authorization_scope_snapshot: tuple[str, ...]
    decision: object
    executor_ref: str | None
    repair_applied: bool
    verification_passed: bool


def _decide(state: EscalationGraphState) -> dict:
    decision = decide_escalation(
        state.get("classification", "UNKNOWN"),
        budget=state.get("budget", EscalationBudget()),
        candidates=state.get("candidates", ()),
        required_capabilities=state.get("required_capabilities", ()),
        current_executor_ref=state.get("current_executor_ref"),
        current_family=state.get("current_family"),
    )
    return {
        "decision": decision,
        "authorization_scope_snapshot": state.get("authorization_scope", ()),
    }


def _route(state: EscalationGraphState) -> str:
    decision = state["decision"]
    if decision.decision in _HANDOFF_DECISIONS:
        return "handoff"
    if decision.decision == "REPAIR_LOCAL":
        return "repair"
    return "end"


def _handoff(state: EscalationGraphState) -> dict:
    """Record a selected executor; never invoke it or alter authorization."""
    return {"executor_ref": state["decision"].target_executor_ref}


def _repair(state: EscalationGraphState) -> dict:
    """Deterministic repair stub; real repair remains behind existing adapters."""
    return {"repair_applied": True}


def _verify(state: EscalationGraphState) -> dict:
    decision = state["decision"]
    handoff_ok = (
        decision.decision not in _HANDOFF_DECISIONS
        or (
            bool(state.get("executor_ref"))
            and state.get("executor_ref") != state.get("current_executor_ref")
        )
    )
    # The graph has no node that writes authorization_scope. Equality here is
    # an explicit invariant check, not an authorization grant.
    return {
        "verification_passed": (
            decision.authorization_preserved
            and handoff_ok
            and state.get("authorization_scope") == state.get("authorization_scope_snapshot")
        )
    }


def build_escalation_graph():
    """Compile the optional deterministic StateGraph treatment.

    Raises RuntimeError with an actionable message when the optional extra is
    absent. No checkpointer is configured: durable recovery is LGB-005.
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "LangGraph is optional; install requirements-langgraph-test.txt "
            "to run this treatment."
        ) from exc

    builder = StateGraph(EscalationGraphState)
    builder.add_node("decide", _decide)
    builder.add_node("handoff", _handoff)
    builder.add_node("repair", _repair)
    builder.add_node("verify", _verify)
    builder.add_edge(START, "decide")
    builder.add_conditional_edges(
        "decide",
        _route,
        {"handoff": "handoff", "repair": "repair", "end": END},
    )
    builder.add_edge("handoff", "verify")
    builder.add_edge("repair", "verify")
    builder.add_edge("verify", END)
    return builder.compile()
