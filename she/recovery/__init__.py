"""SHE P0.3/P0.5 — L0 recovery (no source mutation).

Deterministic recovery plans: retry, restart, reconnect, refresh,
regenerate transient state, reacquire locks, safe rollback of ephemeral state.
Actions bridge: command plans + optional live re-run (SHE_L0_LIVE=1).
P0.5 wires dispatch_l0_plan ranking into the dry-run bridge.
"""

from she.recovery.actions_bridge import (
    ActionsBridgeResult,
    ActionsCommand,
    bridge_workflow_failure,
    dispatch_then_bridge,
    execute_actions_bridge,
    filter_execution_plan_by_dispatch,
    live_enabled,
    plan_actions_commands,
)
from she.recovery.executor import (
    L0_TARGETS,
    L0ExecutionPlan,
    L0Intent,
    intents_for_workflow_failure,
    plan_l0_execution,
)
from she.recovery.l0 import (
    L0_ACTIONS,
    L0Plan,
    plan_l0_recovery,
)

__all__ = [
    "L0_ACTIONS",
    "L0Plan",
    "plan_l0_recovery",
    "L0_TARGETS",
    "L0ExecutionPlan",
    "L0Intent",
    "plan_l0_execution",
    "intents_for_workflow_failure",
    "ActionsCommand",
    "ActionsBridgeResult",
    "plan_actions_commands",
    "execute_actions_bridge",
    "bridge_workflow_failure",
    "dispatch_then_bridge",
    "filter_execution_plan_by_dispatch",
    "live_enabled",
]
