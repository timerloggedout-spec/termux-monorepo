use termux_brain::*;
use std::collections::BTreeMap;

struct FixtureBackend {
    outputs: BTreeMap<BrainStage, StageExecution>,
    failure: Option<BrainStage>,
}

impl StageBackend for FixtureBackend {
    fn run_stage(&self, stage: BrainStage, _input: &StageInput<'_>) -> Result<StageExecution, String> {
        if self.failure == Some(stage) { return Err(format!("fixture failure at {stage:?}")); }
        self.outputs.get(&stage).cloned().ok_or_else(|| format!("missing fixture for {stage:?}"))
    }
}

struct FixturePolicy(DecisionStatus);

impl PolicyGate for FixturePolicy {
    fn evaluate(&self, _input: &PolicyInput<'_>) -> PolicyDecision {
        PolicyDecision {
            status: self.0,
            reason: "fixture policy decision".into(),
            evidence_refs: vec!["policy-fixture:1".into()],
        }
    }
}

fn execution(output: StageOutput) -> StageExecution {
    StageExecution {
        output,
        provider_id: Some("fixture".into()),
        model_id: Some("fixture-v1".into()),
        fallback_used: false,
    }
}

fn outputs() -> BTreeMap<BrainStage, StageExecution> {
    let mut map = BTreeMap::new();
    map.insert(BrainStage::Intent, execution(StageOutput::Intent(IntentAnalysis {
        intent: "build a shared cognitive kernel".into(),
        complexity: Complexity::Complex,
        confidence_bps: 9_500,
    })));
    map.insert(BrainStage::Decomposition, execution(StageOutput::Decomposition(Decomposition {
        tasks: vec![Subtask { id: "design".into(), goal: "design the kernel".into(), depends_on: vec![] }],
    })));
    map.insert(BrainStage::Strategy, execution(StageOutput::Strategy(Strategy {
        approach: "typed adapter-driven core".into(),
        rationale: "preserve existing boundaries".into(),
        success_criteria: vec!["deterministic tests".into()],
        constraints: vec!["no tool execution".into()],
    })));
    map.insert(BrainStage::ExecutionDesign, execution(StageOutput::ExecutionDesign(ExecutionDesign {
        plan: ExecutionPlan { steps: vec![
            PlanStep {
                id: "recon".into(), title: "Recon".into(), description: "inspect sources".into(),
                depends_on: vec![], agent_role: Some("researcher".into()), tool_ids: vec![],
                expected_output: "source map".into(), verification: vec!["paths verified".into()],
                risk: RiskLevel::Low, has_side_effects: false,
            },
            PlanStep {
                id: "design".into(), title: "Design".into(), description: "define contract".into(),
                depends_on: vec!["recon".into()], agent_role: Some("architect".into()), tool_ids: vec![],
                expected_output: "typed contract".into(), verification: vec!["reviewed".into()],
                risk: RiskLevel::Low, has_side_effects: false,
            },
        ]},
    })));
    map.insert(BrainStage::Validation, execution(StageOutput::Validation(ValidationReport {
        passed: true,
        checks: vec![ValidationCheck { id: "contract".into(), passed: true, evidence_refs: vec!["test:1".into()] }],
        blocking_issues: vec![],
        evidence_refs: vec!["test:1".into()],
    })));
    map.insert(BrainStage::Optimization, execution(StageOutput::Optimization(OptimizationReport {
        improvements: vec![], tradeoffs: vec![],
    })));
    map.insert(BrainStage::Reflection, execution(StageOutput::Reflection(ReflectionReport {
        lessons: vec![],
        learning_candidates: vec![LearningCandidate {
            summary: "keep policy outside the kernel".into(),
            confidence_bps: 9_000,
            evidence_refs: vec!["test:1".into()],
        }],
    })));
    map
}

fn input(mode: BrainMode) -> BrainInput {
    BrainInput {
        identity: RunIdentity {
            orchestration_id: "orch-1".into(),
            cycle_id: "cycle-1".into(),
            attempt_id: "attempt-1".into(),
        },
        goal: "build the shared brain kernel".into(),
        mode,
        context: vec![],
        context_budget_tokens: 1_000,
    }
}

fn run(outputs: BTreeMap<BrainStage, StageExecution>, failure: Option<BrainStage>, mode: BrainMode, policy: DecisionStatus) -> BrainResult {
    Brain::new(
        FixtureBackend { outputs, failure },
        FixturePolicy(policy),
        BrainConfig { max_context_tokens: 2_000, max_plan_steps: 10 },
    ).run(input(mode)).unwrap()
}

#[test]
fn standard_pipeline_returns_a_structurally_valid_plan() {
    let result = run(outputs(), None, BrainMode::Standard, DecisionStatus::Ready);
    assert_eq!(result.contract_version, CONTRACT_VERSION);
    assert_eq!(result.run_status, RunStatus::Completed);
    assert_eq!(result.decision.status, DecisionStatus::Ready);
    assert_eq!(result.plan_validation.as_ref().unwrap().parallel_groups,
        vec![vec!["recon".to_string()], vec!["design".to_string()]]);
}

#[test]
fn policy_decision_is_preserved_without_brain_override() {
    let result = run(outputs(), None, BrainMode::Standard, DecisionStatus::NeedsApproval);
    assert_eq!(result.decision.status, DecisionStatus::NeedsApproval);
}

#[test]
fn failed_required_stage_never_produces_ready_handoff() {
    let result = run(outputs(), Some(BrainStage::Strategy), BrainMode::Standard, DecisionStatus::Ready);
    assert_eq!(result.run_status, RunStatus::Failed);
    assert_eq!(result.decision.status, DecisionStatus::NeedsReview);
}

#[test]
fn optional_stage_failure_is_visible_as_degraded() {
    let result = run(outputs(), Some(BrainStage::Optimization), BrainMode::Deep, DecisionStatus::Ready);
    assert_eq!(result.run_status, RunStatus::Degraded);
    assert_eq!(result.decision.status, DecisionStatus::Ready);
    assert_eq!(result.stages[5].status, StageStatus::Failed);
}

#[test]
fn fallback_use_is_not_reported_as_a_clean_run() {
    let mut map = outputs();
    map.get_mut(&BrainStage::Intent).unwrap().fallback_used = true;
    let result = run(map, None, BrainMode::Standard, DecisionStatus::Ready);
    assert_eq!(result.run_status, RunStatus::Degraded);
    assert_eq!(result.stages[0].status, StageStatus::Degraded);
}

#[test]
fn failed_validation_cannot_be_overridden_by_policy_allow() {
    let mut map = outputs();
    map.insert(BrainStage::Validation, execution(StageOutput::Validation(ValidationReport {
        passed: false, checks: vec![], blocking_issues: vec!["missing evidence".into()], evidence_refs: vec![],
    })));
    let result = run(map, None, BrainMode::Standard, DecisionStatus::Ready);
    assert_eq!(result.decision.status, DecisionStatus::NeedsReview);
}

#[test]
fn validation_without_evidence_references_requires_evidence() {
    let mut map = outputs();
    map.insert(BrainStage::Validation, execution(StageOutput::Validation(ValidationReport {
        passed: true, checks: vec![], blocking_issues: vec![], evidence_refs: vec![],
    })));
    let result = run(map, None, BrainMode::Standard, DecisionStatus::Ready);
    assert_eq!(result.decision.status, DecisionStatus::NeedEvidence);
}

#[test]
fn context_selection_excludes_sensitive_items_and_obeys_budget() {
    let mut request = input(BrainMode::Fast);
    request.context_budget_tokens = 5;
    request.context = vec![
        ContextItem {
            id: "lower".into(), source_ref: "a".into(), content: "lower".into(),
            relevance_bps: 100, estimated_tokens: 3,
            classification: ContextClassification::Public, evidence: EvidenceStatus::Observed,
        },
        ContextItem {
            id: "secret".into(), source_ref: "b".into(), content: "secret".into(),
            relevance_bps: 10_000, estimated_tokens: 1,
            classification: ContextClassification::Secret, evidence: EvidenceStatus::Unknown,
        },
        ContextItem {
            id: "higher".into(), source_ref: "c".into(), content: "higher".into(),
            relevance_bps: 9_000, estimated_tokens: 4,
            classification: ContextClassification::Internal, evidence: EvidenceStatus::Verified,
        },
    ];
    let result = Brain::new(
        FixtureBackend { outputs: outputs(), failure: None },
        FixturePolicy(DecisionStatus::Ready),
        BrainConfig { max_context_tokens: 5, max_plan_steps: 10 },
    ).run(request).unwrap();
    assert_eq!(result.context.selected_ids, vec!["higher".to_string()]);
    assert_eq!(result.context.excluded_by_classification, vec!["secret".to_string()]);
    assert_eq!(result.context.omitted_by_budget, vec!["lower".to_string()]);
}

#[test]
fn plan_cycles_and_missing_dependencies_are_rejected() {
    let plan = ExecutionPlan { steps: vec![
        PlanStep {
            id: "a".into(), title: "A".into(), description: "".into(), depends_on: vec!["b".into()],
            agent_role: None, tool_ids: vec![], expected_output: "".into(), verification: vec![],
            risk: RiskLevel::Low, has_side_effects: false,
        },
        PlanStep {
            id: "b".into(), title: "B".into(), description: "".into(), depends_on: vec!["a".into(), "missing".into()],
            agent_role: None, tool_ids: vec![], expected_output: "".into(), verification: vec![],
            risk: RiskLevel::Low, has_side_effects: false,
        },
    ]};
    let report = validate_plan(&plan, 10);
    assert!(!report.valid);
    assert!(report.issues.iter().any(|issue| issue.contains("missing dependency")));
    assert!(report.issues.iter().any(|issue| issue.contains("cycle")));
}

#[test]
fn duplicate_context_ids_are_rejected() {
    let mut request = input(BrainMode::Fast);
    let item = ContextItem {
        id: "same".into(), source_ref: "src".into(), content: "x".into(),
        relevance_bps: 1, estimated_tokens: 1,
        classification: ContextClassification::Public, evidence: EvidenceStatus::Verified,
    };
    request.context = vec![item.clone(), item];
    let result = Brain::new(
        FixtureBackend { outputs: outputs(), failure: None },
        FixturePolicy(DecisionStatus::Ready),
        BrainConfig::default(),
    ).run(request);
    assert_eq!(result.unwrap_err(), BrainError::DuplicateContextId("same".into()));
}

#[test]
fn fast_mode_skips_decomposition_and_execution_design() {
    let result = run(outputs(), None, BrainMode::Fast, DecisionStatus::Ready);
    let stages: Vec<BrainStage> = result.stages.iter().map(|record| record.stage).collect();
    assert_eq!(stages, vec![BrainStage::Intent, BrainStage::Strategy, BrainStage::Validation]);
    assert!(result.plan.is_none());
}

#[test]
fn wrong_stage_output_fails_closed() {
    let mut map = outputs();
    map.insert(BrainStage::Strategy, execution(StageOutput::Intent(IntentAnalysis {
        intent: "wrong stage".into(), complexity: Complexity::Simple, confidence_bps: 8_000,
    })));
    let result = run(map, None, BrainMode::Standard, DecisionStatus::Ready);
    assert_eq!(result.decision.status, DecisionStatus::NeedsReview);
}
