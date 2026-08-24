"""SHE P0.3 — L0 recovery (no source mutation).

Deterministic recovery plans: retry, restart, reconnect, refresh,
regenerate transient state, reacquire locks, safe rollback of ephemeral state.
Actions bridge: command plans + optional live re-run (SHE_L0_LIVE=1).
"""

from she.recovery.actions_bridge import (
    ActionsBridgeResult,
    ActionsCommand,
    bridge_workflow_failure,
    execute_actions_bridge,
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
    "live_enabled",
]
