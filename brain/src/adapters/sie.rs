//! Adapter from QUE SIE lifecycle observations into bounded Brain context.
//!
//! The SIE host supplies canonical orchestration identity and a validated
//! `que.sie-stage/v1` receipt. This module performs a typed in-process mapping;
//! it owns no queue state, stage transition, policy, execution or persistence.

use crate::{
    Brain, BrainError, BrainInput, BrainMode, BrainResult, ContextClassification, ContextItem,
    EvidenceStatus, PolicyGate, RunIdentity, StageBackend,
};

pub const SIE_STAGE_SCHEMA: &str = "que.sie-stage/v1";

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SieObservation {
    pub schema: String,
    pub event_id: String,
    pub item_key: String,
    pub stage: String,
    pub state: String,
    pub source_kind: String,
    pub source_id: String,
    /// Canonical source URL or artifact reference resolved by the host.
    pub source_ref: String,
    pub observed_at: String,
    pub repository: String,
    pub git_ref: String,
    pub sha: Option<String>,
    pub evidence_refs: Vec<String>,
    pub reason: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SieBrainEnvelope {
    /// Canonical host identity; the adapter preserves all three values.
    pub identity: RunIdentity,
    pub goal: String,
    pub mode: BrainMode,
    pub context_budget_tokens: usize,
    /// Token estimate supplied by the host's tokenizer/context adapter.
    pub estimated_tokens: usize,
    pub observation: SieObservation,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SieAdapterError {
    UnsupportedSchema(String),
    MissingField(&'static str),
    Brain(BrainError),
}

impl std::fmt::Display for SieAdapterError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::UnsupportedSchema(schema) => write!(f, "unsupported SIE schema: {schema}"),
            Self::MissingField(name) => write!(f, "missing SIE adapter field: {name}"),
            Self::Brain(error) => write!(f, "Brain input rejected: {error}"),
        }
    }
}

impl std::error::Error for SieAdapterError {}

impl From<BrainError> for SieAdapterError {
    fn from(value: BrainError) -> Self {
        Self::Brain(value)
    }
}

pub fn into_brain_input(envelope: SieBrainEnvelope) -> Result<BrainInput, SieAdapterError> {
    let observation = envelope.observation;
    if observation.schema != SIE_STAGE_SCHEMA {
        return Err(SieAdapterError::UnsupportedSchema(observation.schema));
    }
    for (name, value) in [
        ("event_id", observation.event_id.as_str()),
        ("item_key", observation.item_key.as_str()),
        ("stage", observation.stage.as_str()),
        ("state", observation.state.as_str()),
        ("source_kind", observation.source_kind.as_str()),
        ("source_id", observation.source_id.as_str()),
        ("source_ref", observation.source_ref.as_str()),
        ("observed_at", observation.observed_at.as_str()),
        ("repository", observation.repository.as_str()),
        ("git_ref", observation.git_ref.as_str()),
    ] {
        if value.trim().is_empty() {
            return Err(SieAdapterError::MissingField(name));
        }
    }
    if envelope.goal.trim().is_empty() {
        return Err(SieAdapterError::MissingField("goal"));
    }
    if envelope.estimated_tokens == 0 {
        return Err(SieAdapterError::MissingField("estimated_tokens"));
    }

    let evidence = observation.evidence_refs.join(", ");
    let reason = observation.reason.unwrap_or_else(|| "none supplied".into());
    let content = format!(
        "SIE stage observation: stage={} state={} item_key={} event_id={} source={}/{} observed_at={} repository={} ref={} sha={} reason={} evidence_refs=[{}]. This is an operational observation, not independent task verification.",
        observation.stage,
        observation.state,
        observation.item_key,
        observation.event_id,
        observation.source_kind,
        observation.source_id,
        observation.observed_at,
        observation.repository,
        observation.git_ref,
        observation.sha.as_deref().unwrap_or("unknown"),
        reason,
        evidence,
    );

    Ok(BrainInput {
        identity: envelope.identity,
        goal: envelope.goal,
        mode: envelope.mode,
        context_budget_tokens: envelope.context_budget_tokens,
        context: vec![ContextItem {
            id: format!("sie:{}", observation.event_id),
            source_ref: observation.source_ref,
            content,
            relevance_bps: 10_000,
            estimated_tokens: envelope.estimated_tokens,
            classification: ContextClassification::Internal,
            // A SIE stage receipt proves that the stage emitted a receipt. It
            // does not prove the underlying task outcome independently.
            evidence: EvidenceStatus::Observed,
        }],
    })
}

pub fn run_observation<B: StageBackend, P: PolicyGate>(
    brain: &Brain<B, P>,
    envelope: SieBrainEnvelope,
) -> Result<BrainResult, SieAdapterError> {
    Ok(brain.run(into_brain_input(envelope)?)?)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        BrainConfig, BrainStage, Complexity, DecisionStatus, Decomposition, ExecutionDesign,
        ExecutionPlan, IntentAnalysis, OptimizationReport, PlanStep, PolicyDecision, PolicyInput,
        ReflectionReport, RiskLevel, RunStatus, StageExecution, StageInput, StageOutput, Strategy,
        ValidationCheck, ValidationReport,
    };

    struct FixtureBackend;
    impl StageBackend for FixtureBackend {
        fn run_stage(
            &self,
            stage: BrainStage,
            input: &StageInput<'_>,
        ) -> Result<StageExecution, String> {
            let evidence = input
                .selected_context
                .iter()
                .map(|item| item.source_ref.clone())
                .collect::<Vec<_>>();
            let output = match stage {
                BrainStage::Intent => StageOutput::Intent(IntentAnalysis {
                    intent: "assess SIE observation".into(),
                    complexity: Complexity::Moderate,
                    confidence_bps: 9_000,
                }),
                BrainStage::Decomposition => {
                    StageOutput::Decomposition(Decomposition { tasks: vec![] })
                }
                BrainStage::Strategy => StageOutput::Strategy(Strategy {
                    approach: "evidence-first shadow assessment".into(),
                    rationale: "preserve SIE and QUE authority".into(),
                    success_criteria: vec!["identity preserved".into()],
                    constraints: vec!["read-only".into()],
                }),
                BrainStage::ExecutionDesign => StageOutput::ExecutionDesign(ExecutionDesign {
                    plan: ExecutionPlan {
                        steps: vec![PlanStep {
                            id: "inspect".into(),
                            title: "Inspect SIE evidence".into(),
                            description: "Read the supplied observation".into(),
                            depends_on: vec![],
                            agent_role: None,
                            tool_ids: vec![],
                            expected_output: "typed assessment".into(),
                            verification: vec!["source reference retained".into()],
                            risk: RiskLevel::Low,
                            has_side_effects: false,
                        }],
                    },
                }),
                BrainStage::Validation => StageOutput::Validation(ValidationReport {
                    passed: true,
                    checks: vec![ValidationCheck {
                        id: "receipt-present".into(),
                        passed: true,
                        evidence_refs: evidence.clone(),
                    }],
                    blocking_issues: vec![],
                    evidence_refs: evidence,
                }),
                BrainStage::Optimization => StageOutput::Optimization(OptimizationReport {
                    improvements: vec![],
                    tradeoffs: vec![],
                }),
                BrainStage::Reflection => StageOutput::Reflection(ReflectionReport {
                    lessons: vec![],
                    learning_candidates: vec![],
                }),
            };
            Ok(StageExecution {
                output,
                provider_id: Some("fixture".into()),
                model_id: Some("deterministic-test".into()),
                fallback_used: false,
            })
        }
    }

    struct HoldPolicy;
    impl PolicyGate for HoldPolicy {
        fn evaluate(&self, _input: &PolicyInput<'_>) -> PolicyDecision {
            PolicyDecision {
                status: DecisionStatus::NeedsApproval,
                reason: "SIE host approval remains authoritative".into(),
                evidence_refs: vec!["policy-fixture".into()],
            }
        }
    }

    fn envelope() -> SieBrainEnvelope {
        SieBrainEnvelope {
            identity: RunIdentity {
                orchestration_id: "orch-1".into(),
                cycle_id: "cycle-2".into(),
                attempt_id: "attempt-3".into(),
            },
            goal: "Assess the latest SIE stage observation".into(),
            mode: BrainMode::Standard,
            context_budget_tokens: 1024,
            estimated_tokens: 80,
            observation: SieObservation {
                schema: SIE_STAGE_SCHEMA.into(),
                event_id: "a".repeat(64),
                item_key: "b".repeat(24),
                stage: "OBSERVE".into(),
                state: "COMPLETED".into(),
                source_kind: "workflow_run".into(),
                source_id: "12345".into(),
                source_ref:
                    "https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/12345"
                        .into(),
                observed_at: "2026-11-23T10:00:00Z".into(),
                repository: "timerloggedout-spec/termux-monorepo".into(),
                git_ref: "refs/heads/master".into(),
                sha: Some("c".repeat(40)),
                evidence_refs: vec!["run:12345".into()],
                reason: Some("workflow failed".into()),
            },
        }
    }

    #[test]
    fn maps_sie_observation_to_bounded_internal_context_and_preserves_identity() {
        let input = into_brain_input(envelope()).unwrap();
        assert_eq!(input.identity.orchestration_id, "orch-1");
        assert_eq!(input.identity.cycle_id, "cycle-2");
        assert_eq!(input.identity.attempt_id, "attempt-3");
        assert_eq!(input.context[0].id, format!("sie:{}", "a".repeat(64)));
        assert_eq!(
            input.context[0].classification,
            ContextClassification::Internal
        );
        assert_eq!(input.context[0].evidence, EvidenceStatus::Observed);
        assert_eq!(input.context[0].estimated_tokens, 80);
        assert!(input.context[0]
            .content
            .contains("independent task verification"));
    }

    #[test]
    fn runs_kernel_and_preserves_policy_hold() {
        let brain = Brain::new(FixtureBackend, HoldPolicy, BrainConfig::default());
        let result = run_observation(&brain, envelope()).unwrap();
        assert_eq!(result.identity.orchestration_id, "orch-1");
        assert_eq!(result.identity.cycle_id, "cycle-2");
        assert_eq!(result.identity.attempt_id, "attempt-3");
        assert_eq!(result.run_status, RunStatus::Completed);
        assert_eq!(result.decision.status, DecisionStatus::NeedsApproval);
    }

    #[test]
    fn rejects_unknown_sie_schema() {
        let mut request = envelope();
        request.observation.schema = "que.sie-stage/v2".into();
        assert!(matches!(
            into_brain_input(request),
            Err(SieAdapterError::UnsupportedSchema(_))
        ));
    }

    #[test]
    fn rejects_missing_host_resolved_source_reference() {
        let mut request = envelope();
        request.observation.source_ref.clear();
        assert!(matches!(
            into_brain_input(request),
            Err(SieAdapterError::MissingField("source_ref"))
        ));
    }
}
