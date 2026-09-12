"""Self-Healing Engine (SHE) — control-plane primitives.

P0.1 incident · P0.2 ingest observers · P0.3 L0 recovery planner + executor
+ Actions re-run bridge (dry-run default) · job-timestamp metrics · P0.4 dispatcher
· P0.4.1 dispatch→bridge dry-run wire · P0.5 repair sandbox planner
· P0.6 verification planner · P0.7 repair-PR planner · P0.8 learning planner
· P0.9 evolutionary-repair planner · P0.10 promotion-decision planner
· P0.11 append-only evidence ledger · P0.12 attestation digest
· P0.13 attestation replay verifier · P0.14 publication planner.
"""

from she.attest import (
    DIGEST_ALGO,
    Attestation,
    AttestError,
    digest_mapping,
    live_attest_enabled,
    plan_attestation,
)
from she.evolve import (
    HYPOTHESIS_KINDS,
    EvolutionPlan,
    EvolveError,
    ExperimentSpec,
    Hypothesis,
    live_evolve_enabled,
    plan_evolution,
)
from she.incident import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATES,
    Incident,
    IncidentError,
    IncidentState,
    Transition,
)
from she.ingest.actions import (
    fingerprint_workflow_run,
    incident_from_workflow_run,
    normalize_workflow_run_payload,
)
from she.learn import (
    OUTCOMES,
    LearnError,
    LearningRecord,
    live_learn_enabled,
    plan_learning,
)
from she.ledger import (
    ENTRY_KINDS,
    EvidenceLedger,
    LedgerEntry,
    LedgerError,
    live_ledger_enabled,
    plan_ledger,
)
from she.metrics.job_timestamps import (
    JobDuration,
    RunJobStats,
    WorkflowWindowStats,
    aggregate_run_job_stats,
    aggregate_workflow_window,
    duration_ms_from_job,
    duration_ms_from_jobs,
    queue_ms_from_job,
)
from she.promote import (
    DECISIONS,
    PromotionDecision,
    PromotionError,
    live_promote_enabled,
    plan_promotion,
)
from she.publish import (
    ACTIONS as PUBLISH_ACTIONS,
    PublicationPlan,
    PublishError,
    live_publish_enabled,
    plan_publication,
)
from she.recovery.actions_bridge import (
    ActionsBridgeResult,
    ActionsCommand,
    bridge_workflow_failure,
    dispatch_then_bridge,
    execute_actions_bridge,
    filter_execution_plan_by_dispatch,
    plan_actions_commands,
)
from she.recovery.dispatcher import (
    CAPABILITIES,
    DispatchDecision,
    dispatch_from_mapping,
    dispatch_l0_plan,
    rank_actions,
)
from she.recovery.executor import (
    L0_TARGETS,
    L0ExecutionPlan,
    L0Intent,
    intents_for_workflow_failure,
    plan_l0_execution,
)
from she.recovery.l0 import L0_ACTIONS, L0Plan, plan_l0_recovery
from she.repair_pr import (
    REQUIRED_TESTS,
    RepairPRError,
    RepairPRPlan,
    live_repair_pr_enabled,
    plan_repair_pr,
)
from she.replay import (
    VERDICTS,
    ReplayError,
    ReplayVerdict,
    live_replay_enabled,
    plan_replay,
)
from she.sandbox import (
    CREDENTIAL_PROFILES,
    ENV_PROFILES,
    SANDBOX_BRANCH_PREFIX,
    SandboxError,
    SandboxPlan,
    live_sandbox_enabled,
    plan_repair_sandbox,
    sandbox_branch_name,
)
from she.verify import (
    CHECK_OUTCOMES,
    DUAL_GATES,
    VERIFICATION_GATES,
    CheckSpec,
    VerificationError,
    VerificationPlan,
    apply_check_results,
    plan_verification,
    summarize_results,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "TERMINAL_STATES",
    "Incident",
    "IncidentError",
    "IncidentState",
    "Transition",
    "fingerprint_workflow_run",
    "incident_from_workflow_run",
    "normalize_workflow_run_payload",
    "JobDuration",
    "RunJobStats",
    "WorkflowWindowStats",
    "aggregate_run_job_stats",
    "aggregate_workflow_window",
    "duration_ms_from_job",
    "duration_ms_from_jobs",
    "queue_ms_from_job",
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
    "CAPABILITIES",
    "DispatchDecision",
    "rank_actions",
    "dispatch_l0_plan",
    "dispatch_from_mapping",
    "CREDENTIAL_PROFILES",
    "ENV_PROFILES",
    "SANDBOX_BRANCH_PREFIX",
    "SandboxError",
    "SandboxPlan",
    "live_sandbox_enabled",
    "plan_repair_sandbox",
    "sandbox_branch_name",
    "CHECK_OUTCOMES",
    "DUAL_GATES",
    "VERIFICATION_GATES",
    "CheckSpec",
    "VerificationError",
    "VerificationPlan",
    "apply_check_results",
    "plan_verification",
    "summarize_results",
    "REQUIRED_TESTS",
    "RepairPRError",
    "RepairPRPlan",
    "live_repair_pr_enabled",
    "plan_repair_pr",
    "OUTCOMES",
    "LearnError",
    "LearningRecord",
    "live_learn_enabled",
    "plan_learning",
    "HYPOTHESIS_KINDS",
    "EvolveError",
    "Hypothesis",
    "ExperimentSpec",
    "EvolutionPlan",
    "live_evolve_enabled",
    "plan_evolution",
    "DECISIONS",
    "PromotionError",
    "PromotionDecision",
    "live_promote_enabled",
    "plan_promotion",
    "ENTRY_KINDS",
    "LedgerError",
    "LedgerEntry",
    "EvidenceLedger",
    "live_ledger_enabled",
    "plan_ledger",
    "DIGEST_ALGO",
    "AttestError",
    "Attestation",
    "digest_mapping",
    "live_attest_enabled",
    "plan_attestation",
    "VERDICTS",
    "ReplayError",
    "ReplayVerdict",
    "live_replay_enabled",
    "plan_replay",
    "PUBLISH_ACTIONS",
    "PublishError",
    "PublicationPlan",
    "live_publish_enabled",
    "plan_publication",
]

__version__ = "0.15.0"
