//! Implements: CNS-06 — end-to-end shadow composition contract for the Brain kernel and MOSAIC.
//!
//! This test is a deterministic host-composition fixture. It exercises the
//! reasoning -> injected policy -> typed specialist path without creating a
//! production host, dispatching work, or persisting memory. Production host
//! selection and its bridge contract remain separately governed.

use std::collections::BTreeMap;

use mosaic_brain::{
    EvaluationSnapshot, EvidenceKind, EvidenceRef, MethodIdentity, MosaicBrain, MosaicRequest,
    RecommendationOutcome, ReviewVerdict,
};
use termux_brain::{
    invoke_extension, Brain, BrainConfig, BrainInput, BrainMode, BrainStage, Complexity,
    DecisionStatus, Decomposition, ExecutionDesign, ExecutionPlan, ExtensionContext,
    IntentAnalysis, PlanStep, PolicyDecision, PolicyGate, PolicyInput, RiskLevel, RunIdentity,
    StageBackend, StageExecution, StageInput, StageOutput, Strategy, Subtask, ValidationCheck,
    ValidationReport,
};

struct FixtureBackend {
    outputs: BTreeMap<BrainStage, StageExecution>,
}

impl FixtureBackend {
    fn new() -> Self {
        let mut outputs = BTreeMap::new();
        outputs.insert(
            BrainStage::Intent,
            execution(StageOutput::Intent(IntentAnalysis {
                intent: "evaluate a methodology revision".into(),
                complexity: Complexity::Moderate,
                confidence_bps: 9_500,
            })),
        );
        outputs.insert(
            BrainStage::Decomposition,
            execution(StageOutput::Decomposition(Decomposition {
                tasks: vec![Subtask {
                    id: "evaluate-method".into(),
                    goal: "evaluate the immutable method revision".into(),
                    depends_on: vec![],
                }],
            })),
        );
        outputs.insert(
            BrainStage::Strategy,
            execution(StageOutput::Strategy(Strategy {
                approach: "invoke the methodology specialist through the typed contract".into(),
                rationale: "keep domain logic outside the shared kernel".into(),
                success_criteria: vec!["specialist response preserves run identity".into()],
                constraints: vec!["shadow-only; no dispatch or persistence".into()],
            })),
        );
        outputs.insert(
            BrainStage::ExecutionDesign,
            execution(StageOutput::ExecutionDesign(ExecutionDesign {
                plan: ExecutionPlan {
                    steps: vec![PlanStep {
                        id: "specialist-evaluation".into(),
                        title: "Evaluate methodology".into(),
                        description: "Request an advisory MOSAIC evaluation".into(),
                        depends_on: vec![],
                        agent_role: Some("methodology-specialist".into()),
                        tool_ids: vec![],
                        expected_output: "Hold, Revise, or PromotionCandidate".into(),
                        verification: vec!["typed contract and identity verified".into()],
                        risk: RiskLevel::Low,
                        has_side_effects: false,
                    }],
                },
            })),
        );
        outputs.insert(
            BrainStage::Validation,
            execution(StageOutput::Validation(ValidationReport {
                passed: true,
                checks: vec![ValidationCheck {
                    id: "shadow-contract".into(),
                    passed: true,
                    evidence_refs: vec!["test://brain-shadow-host/contract".into()],
                }],
                blocking_issues: vec![],
                evidence_refs: vec!["test://brain-shadow-host/contract".into()],
            })),
        );
        Self { outputs }
    }
}

impl StageBackend for FixtureBackend {
    fn run_stage(
        &self,
        stage: BrainStage,
        _input: &StageInput<'_>,
    ) -> Result<StageExecution, String> {
        self.outputs
            .get(&stage)
            .cloned()
            .ok_or_else(|| format!("missing deterministic fixture for {stage:?}"))
    }
}

fn execution(output: StageOutput) -> StageExecution {
    StageExecution {
        output,
        provider_id: Some("deterministic-fixture".into()),
        model_id: Some("brain-shadow-v1".into()),
        fallback_used: false,
    }
}

struct FixturePolicy(DecisionStatus);

impl PolicyGate for FixturePolicy {
    fn evaluate(&self, _input: &PolicyInput<'_>) -> PolicyDecision {
        PolicyDecision {
            status: self.0,
            reason: "decision supplied by the injected host policy adapter fixture".into(),
            evidence_refs: vec!["test://brain-shadow-host/policy".into()],
        }
    }
}

fn identity() -> RunIdentity {
    RunIdentity {
        orchestration_id: "orch-shadow-001".into(),
        cycle_id: "cycle-shadow-002".into(),
        attempt_id: "attempt-shadow-003".into(),
    }
}

fn brain_input() -> BrainInput {
    BrainInput {
        identity: identity(),
        goal: "evaluate methodology_intelligence using the existing Brain specialist seam".into(),
        mode: BrainMode::Standard,
        context: vec![],
        context_budget_tokens: 256,
    }
}

fn method_identity() -> MethodIdentity {
    MethodIdentity {
        method_id: "methodology.factorial-design".into(),
        version: "1.0.0".into(),
        owner_id: "doe-owner".into(),
        scope_id: "methodology_intelligence".into(),
        source_commit: "0123456789abcdef0123456789abcdef01234567".into(),
        artifact_sha256: "a".repeat(64),
    }
}

fn mosaic_request() -> MosaicRequest {
    let method = method_identity();
    MosaicRequest {
        method: method.clone(),
        snapshot: EvaluationSnapshot {
            method_identity: method,
            evaluator_id: "independent-reviewer".into(),
            method_owner_id: "doe-owner".into(),
            review_verdict: ReviewVerdict::Verified,
            evidence: vec![EvidenceRef {
                source_id: "experiment:shadow-001".into(),
                source_uri: "repo://docs/ops/corpus/EXPERIMENT.schema.json#shadow-001".into(),
                kind: EvidenceKind::ExperimentRecord,
            }],
            practical_gain: Some(true),
            critical_regression: Some(false),
            required_gates_passed: Some(true),
            rollback_ready: Some(true),
        },
    }
}

struct ShadowReceipt {
    identity: RunIdentity,
    kernel_decision: DecisionStatus,
    specialist_outcome: Option<RecommendationOutcome>,
    evidence_refs: Vec<String>,
}

fn run_shadow_composition(policy: DecisionStatus) -> ShadowReceipt {
    let brain = Brain::new(
        FixtureBackend::new(),
        FixturePolicy(policy),
        BrainConfig {
            max_context_tokens: 256,
            max_plan_steps: 4,
        },
    );
    let result = brain
        .run(brain_input())
        .expect("fixture reasoning run succeeds");

    // The host only routes to a specialist after the injected policy gate
    // returns Ready. The kernel's decision remains authoritative.
    let specialist = if result.decision.status == DecisionStatus::Ready {
        let context = ExtensionContext {
            identity: result.identity.clone(),
            domain_id: "methodology_intelligence".into(),
        };
        Some(
            invoke_extension(&MosaicBrain, &context, &mosaic_request())
                .expect("MOSAIC accepts the validated invocation"),
        )
    } else {
        None
    };

    let mut evidence_refs = result.decision.evidence_refs;
    if let Some(response) = &specialist {
        evidence_refs.push("test://brain-shadow-host/mosaic-response".into());
        assert_eq!(response.identity, result.identity);
    }

    ShadowReceipt {
        identity: result.identity,
        kernel_decision: result.decision.status,
        specialist_outcome: specialist.map(|response| response.recommendation.outcome),
        evidence_refs,
    }
}

#[test]
fn reasoning_policy_and_mosaic_form_one_identity_preserving_shadow_handoff() {
    let receipt = run_shadow_composition(DecisionStatus::Ready);

    assert_eq!(receipt.identity, identity());
    assert_eq!(receipt.kernel_decision, DecisionStatus::Ready);
    assert_eq!(
        receipt.specialist_outcome,
        Some(RecommendationOutcome::PromotionCandidate)
    );
    assert!(receipt
        .evidence_refs
        .contains(&"test://brain-shadow-host/mosaic-response".into()));
}

#[test]
fn host_policy_hold_prevents_specialist_handoff() {
    let receipt = run_shadow_composition(DecisionStatus::NeedsApproval);

    assert_eq!(receipt.identity, identity());
    assert_eq!(receipt.kernel_decision, DecisionStatus::NeedsApproval);
    assert_eq!(receipt.specialist_outcome, None);
    assert!(receipt
        .evidence_refs
        .contains(&"test://brain-shadow-host/policy".into()));
}
