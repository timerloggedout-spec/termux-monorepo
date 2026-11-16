//! Repository-wide, provider-neutral cognitive kernel.
//!
//! Brain reasons and returns a typed plan/decision. It does not call models,
//! execute tools, access the network, persist memory, or own policy. Those
//! capabilities remain injected adapters owned by existing monorepo systems.

#![forbid(unsafe_code)]

use std::collections::{BTreeMap, BTreeSet};
use std::time::Instant;

pub const CONTRACT_VERSION: &str = "termux-monorepo.brain.v1";

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum BrainStage {
    Intent,
    Decomposition,
    Strategy,
    ExecutionDesign,
    Validation,
    Optimization,
    Reflection,
}

impl BrainStage {
    fn optional(self) -> bool {
        matches!(self, Self::Optimization | Self::Reflection)
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum BrainMode {
    #[default]
    Adaptive,
    Fast,
    Standard,
    Deep,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Complexity {
    Simple,
    Moderate,
    Complex,
    Enterprise,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RunStatus {
    Completed,
    Degraded,
    Failed,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StageStatus {
    Completed,
    Degraded,
    Failed,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DecisionStatus {
    Ready,
    NeedsApproval,
    Blocked,
    NeedEvidence,
    NeedsReview,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ContextClassification {
    Public,
    Internal,
    Restricted,
    Secret,
    Unknown,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvidenceStatus {
    Verified,
    Observed,
    Candidate,
    Unknown,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RunIdentity {
    pub orchestration_id: String,
    pub cycle_id: String,
    pub attempt_id: String,
}

impl RunIdentity {
    fn validate(&self) -> Result<(), BrainError> {
        for (name, value) in [
            ("orchestration_id", self.orchestration_id.as_str()),
            ("cycle_id", self.cycle_id.as_str()),
            ("attempt_id", self.attempt_id.as_str()),
        ] {
            if value.trim().is_empty() {
                return Err(BrainError::MissingIdentityField(name));
            }
        }
        Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ContextItem {
    pub id: String,
    pub source_ref: String,
    pub content: String,
    /// Integer basis points, 0..=10,000; supplied by the retrieval adapter.
    pub relevance_bps: u16,
    /// Token estimate supplied by the owning tokenizer/provider adapter.
    pub estimated_tokens: usize,
    pub classification: ContextClassification,
    /// Candidate/observed material remains distinct from verified evidence.
    pub evidence: EvidenceStatus,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BrainInput {
    pub identity: RunIdentity,
    pub goal: String,
    pub mode: BrainMode,
    pub context: Vec<ContextItem>,
    pub context_budget_tokens: usize,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BrainConfig {
    pub max_context_tokens: usize,
    pub max_plan_steps: usize,
}

impl Default for BrainConfig {
    fn default() -> Self {
        Self {
            max_context_tokens: 8_192,
            max_plan_steps: 64,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ContextSelectionReport {
    pub selected_ids: Vec<String>,
    pub excluded_by_classification: Vec<String>,
    pub omitted_by_budget: Vec<String>,
    pub tokens_used: usize,
    pub token_budget: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct IntentAnalysis {
    pub intent: String,
    pub complexity: Complexity,
    pub confidence_bps: u16,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Subtask {
    pub id: String,
    pub goal: String,
    pub depends_on: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Decomposition {
    pub tasks: Vec<Subtask>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Strategy {
    pub approach: String,
    pub rationale: String,
    pub success_criteria: Vec<String>,
    pub constraints: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlanStep {
    pub id: String,
    pub title: String,
    pub description: String,
    pub depends_on: Vec<String>,
    pub agent_role: Option<String>,
    /// Capability identifiers only; the Brain never resolves or executes handlers.
    pub tool_ids: Vec<String>,
    pub expected_output: String,
    pub verification: Vec<String>,
    pub risk: RiskLevel,
    pub has_side_effects: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExecutionPlan {
    pub steps: Vec<PlanStep>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExecutionDesign {
    pub plan: ExecutionPlan,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationCheck {
    pub id: String,
    pub passed: bool,
    pub evidence_refs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ValidationReport {
    pub passed: bool,
    pub checks: Vec<ValidationCheck>,
    pub blocking_issues: Vec<String>,
    pub evidence_refs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct OptimizationReport {
    pub improvements: Vec<String>,
    pub tradeoffs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LearningCandidate {
    pub summary: String,
    pub confidence_bps: u16,
    pub evidence_refs: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ReflectionReport {
    pub lessons: Vec<String>,
    /// Suggestions only. A governed memory adapter decides whether to persist.
    pub learning_candidates: Vec<LearningCandidate>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum StageOutput {
    Intent(IntentAnalysis),
    Decomposition(Decomposition),
    Strategy(Strategy),
    ExecutionDesign(ExecutionDesign),
    Validation(ValidationReport),
    Optimization(OptimizationReport),
    Reflection(ReflectionReport),
}

impl StageOutput {
    pub fn stage(&self) -> BrainStage {
        match self {
            Self::Intent(_) => BrainStage::Intent,
            Self::Decomposition(_) => BrainStage::Decomposition,
            Self::Strategy(_) => BrainStage::Strategy,
            Self::ExecutionDesign(_) => BrainStage::ExecutionDesign,
            Self::Validation(_) => BrainStage::Validation,
            Self::Optimization(_) => BrainStage::Optimization,
            Self::Reflection(_) => BrainStage::Reflection,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StageExecution {
    pub output: StageOutput,
    pub provider_id: Option<String>,
    pub model_id: Option<String>,
    /// Fallback use is visible and marks the run degraded.
    pub fallback_used: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StageRecord {
    pub stage: BrainStage,
    pub status: StageStatus,
    pub duration_ms: u64,
    pub provider_id: Option<String>,
    pub model_id: Option<String>,
    pub fallback_used: bool,
    pub output: Option<StageOutput>,
    pub error: Option<String>,
}

pub struct StageInput<'a> {
    pub identity: &'a RunIdentity,
    pub goal: &'a str,
    pub selected_context: &'a [ContextItem],
    pub prior_stages: &'a [StageRecord],
}

/// Model/provider adapter. It may call an LLM or deterministic engine, but must
/// not execute tools or persist memory as a side effect of stage generation.
pub trait StageBackend {
    fn run_stage(
        &self,
        stage: BrainStage,
        input: &StageInput<'_>,
    ) -> Result<StageExecution, String>;
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlanValidationReport {
    pub valid: bool,
    pub issues: Vec<String>,
    /// Each group can run in parallel after all preceding groups complete.
    pub parallel_groups: Vec<Vec<String>>,
}

pub struct PolicyInput<'a> {
    pub identity: &'a RunIdentity,
    pub goal: &'a str,
    pub plan: Option<&'a ExecutionPlan>,
    pub plan_validation: Option<&'a PlanValidationReport>,
    pub context: &'a [ContextItem],
    pub context_report: &'a ContextSelectionReport,
    pub run_status: RunStatus,
    pub stages: &'a [StageRecord],
    pub validation: &'a ValidationReport,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PolicyDecision {
    pub status: DecisionStatus,
    pub reason: String,
    pub evidence_refs: Vec<String>,
}

/// Adapter to existing policy/capability/completion gates. No allow-all default
/// or replacement policy registry is provided by the Brain kernel.
pub trait PolicyGate {
    fn evaluate(&self, input: &PolicyInput<'_>) -> PolicyDecision;
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BrainBesult {
    pub contract_version: &'static str,
    pub identity: RunIdentity,
    pub run_status: RunStatus,
    pub decision: PolicyDecision,
    pub context: ContextSelectionReport,
    pub plan: Option<ExecutionPlan>,
    pub plan_validation: Option<PlanValidationReport>,
    pub stages: Vec<StageRecord>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum BrainError {
    EmptyGoal,
    MissingIdentityField(&'static str),
    DuplicateContextId(String),
    InvalidRelevanceScore(String),
}

impl std::fmt::Display for BrainError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::EmptyGoal => write!(f, "goal must not be empty"),
            Self::MissingIdentityField(name) => write!(f, "missing run identity field: {name}"),
            Self::DuplicateContextId(id) => write!(f, "duplicate context item id: {id}"),
            Self::InvalidRelevanceScore(id) => write!(
                f,
                "context relevance score exceeds 10,000 basis points: {id}"
            ),
        }
    }
}

impl std::error::Error for BrainError {}

pub struct Brain<B, P> {
    backend: B,
    policy: P,
    config: BrainConfig,
}

impl<B: StageBackend, P: PolicyGate> Brain<B, P> {
    pub fn new(backend: B, policy: P, config: BrainConfig) -> Self {
        Self {
            backend,
            policy,
            config,
        }
    }

    pub fn run(&self, input: BrainInput) -> Result<BrainResult, BrainError> {
        if input.goal.trim().is_empty() {
            return Err(BrainError::EmptyGoal);
        }
        input.identity.validate()?;

        let token_budget = input
            .context_budget_tokens
            .min(self.config.max_context_tokens);
        let (selected_context, context_report) = select_context(&input.context, token_budget)?;
        let mut stages = Vec::new();
        let mut run_status = RunStatus::Completed;
        let mut required_stage_failed = false;

        let mut stage_queue = stages_for_mode(input.mode);
        let mut stage_index = 0usize;
        while stage_index < stage_queue.len() {
            let stage = stage_queue[stage_index];
            stage_index += 1;
            let stage_input = StageInput {
                identity: &input.identity,
                goal: &input.goal,
                selected_context: &selected_context,
                prior_stages: &stages,
            };
            let started = Instant::now();
            let result = self.backend.run_stage(stage, &stage_input);
            let duration_ms = started.elapsed().as_millis() as u64;

            match result {
                Ok(execution) if execution.output.stage() == stage => {
                    let adaptive_tail = if input.mode == BrainMode::Adaptive
                        && stage == BrainStage::Intent
                    {
                        match &execution.output {
                            StageOutput::Intent(analysis) => adaptive_stages(analysis.complexity),
                            _ => Vec::new(),
                        }
                    } else {
                        Vec::new()
                    };
                    let status = if execution.fallback_used {
                        run_status = RunStatus::Degraded;
                        StageStatus::Degraded
                    } else {
                        StageStatus::Completed
                    };
                    stages.push(StageRecord {
                        stage,
                        status,
                        duration_ms,
                        provider_id: execution.provider_id,
                        model_id: execution.model_id,
                        fallback_used: execution.fallback_used,
                        output: Some(execution.output),
                        error: None,
                    });
                    stage_queue.extend(adaptive_tail);
                }
                Ok(execution) => {
                    stages.push(StageRecord {
                        stage,
                        status: StageStatus::Failed,
                        duration_ms,
                        provider_id: execution.provider_id,
                        model_id: execution.model_id,
                        fallback_used: execution.fallback_used,
                        output: None,
                        error: Some(format!(
                            "stage output mismatch: expected {:?}, received {:?}",
                            stage,
                            execution.output.stage()
                        )),
                    });
                    if stage.optional() {
                        run_status = RunStatus::Degraded;
                    } else {
                        run_status = RunStatus::Failed;
                        required_stage_failed = true;
                        break;
                    }
                }
                Err(error) => {
                    stages.push(StageRecord {
                        stage,
                        status: StageStatus::Failed,
                        duration_ms,
                        provider_id: None,
                        model_id: None,
                        fallback_used: false,
                        output: None,
                        error: Some(error),
                    });
                    if stage.optional() {
                        run_status = RunStatus::Degraded;
                    } else {
                        run_status = RunStatus::Failed;
                        required_stage_failed = true;
                        break;
                    }
                }
            }
        }

        let plan = stages.iter().find_map(|record| match &record.output {
            Some(StageOutput::ExecutionDesign(design)) => Some(design.plan.clone()),
            _ => None,
        });
        let validation = stages.iter().find_map(|record| match &record.output {
            Some(StageOutput::Validation(report)) => Some(report.clone()),
            _ => None,
        });
        let plan_validation = plan
            .as_ref()
            .map(|plan| validate_plan(plan, self.config.max_plan_steps));

        let decision = if required_stage_failed {
            PolicyDecision {
                status: DecisionStatus::NeedsReview,
                reason: "a required reasoning stage failed; no handoff is permitted".into(),
                evidence_refs: vec![],
            }
        } else if plan_validation.as_ref().is_some_and(|report| !report.valid) {
            PolicyDecision {
                status: DecisionStatus::NeedsReview,
                reason: "the proposed plan failed structural validation".into(),
                evidence_refs: vec![],
            }
        } else if validation.is_none() {
            PolicyDecision {
                status: DecisionStatus::NeedEvidence,
                reason: "a validation report is required before handoff".into(),
                evidence_refs: vec![],
            }
        } else if validation.as_ref().is_some_and(|report| {
            !report.passed
                || !report.blocking_issues.is_empty()
                || report.checks.iter().any(|check| !check.passed)
        }) {
            PolicyDecision {
                status: DecisionStatus::NeedsReview,
                reason: "validation reported a failure or blocking issue".into(),
                evidence_refs: validation
                    .as_ref()
                    .map(|report| report.evidence_refs.clone())
                    .unwrap_or_default(),
            }
        } else if validation
            .as_ref()
            .is_some_and(|report| report.evidence_refs.is_empty())
        {
            PolicyDecision {
                status: DecisionStatus::NeedEvidence,
                reason: "validation must reference canonical evidence before handoff".into(),
                evidence_refs: vec![],
            }
        } else {
            match validation.as_ref() {
                Some(validation) => self.policy.evaluate(&PolicyInput {
                    identity: &input.identity,
                    goal: &input.goal,
                    plan: plan.as_ref(),
                    plan_validation: plan_validation.as_ref(),
                    context: &selected_context,
                    context_report: &context_report,
                    run_status,
                    stages: &stages,
                    validation,
                }),
                None => PolicyDecision {
                    status: DecisionStatus::NeedEvidence,
                    reason: "a validation report is required before handoff".into(),
                    evidence_refs: vec![],
                },
            }
        };

        Ok(BrainResult {
            contract_version: CONTRACT_VERSION,
            identity: input.identity,
            run_status,
            decision,
            context: context_report,
            plan,
            plan_validation,
            stages,
        })
    }
}

fn stages_for_mode(mode: BrainMode) -> Vec<BrainStage> {
    use BrainStage::*;
    match mode {
        BrainMode::Adaptive => vec![Intent],
        BrainMode::Fast => vec![Intent, Strategy, Validation],
        BrainMode::Standard => vec![Intent, Decomposition, Strategy, ExecutionDesign, Validation],
        BrainMode::Deep => vec![
            Intent,
            Decomposition,
            Strategy,
            ExecutionDesign,
            Validation,
            Optimization,
            Reflection,
        ],
    }
}

fn adaptive_stages(complexity: Complexity) -> Vec<BrainStage> {
    use BrainStage::*;
    match complexity {
        Complexity::Simple => vec![Strategy, Validation],
        Complexity::Moderate => vec![Decomposition, Strategy, ExecutionDesign, Validation],
        Complexity::Complex | Complexity::Enterprise => {
            vec![
                Decomposition,
                Strategy,
                ExecutionDesign,
                Validation,
                Optimization,
                Reflection,
            ]
        }
    }
}

fn select_context(
    context: &[ContextItem],
    token_budget: usize,
) -> Result<(Vec<ContextItem>, ContextSelectionReport), BrainError> {
    let mut seen = BTreeSet::new();
    let mut candidates = Vec::new();
    let mut excluded = Vec::new();

    for item in context {
        if !seen.insert(item.id.as_str()) {
            return Err(BrainError::DuplicateContextId(item.id.clone()));
        }
        if item.relevance_bps > 10_000 {
            return Err(BrainError::InvalidRelevanceScore(item.id.clone()));
        }
        match item.classification {
            ContextClassification::Public | ContextClassification::Internal => {
                candidates.push(item)
            }
            ContextClassification::Restricted
            | ContextClassification::Secret
            | ContextClassification::Unknown => excluded.push(item.id.clone()),
        }
    }

    candidates.sort_by(|a, b| {
        b.relevance_bps
            .cmp(&a.relevance_bps)
            .then_with(|| a.id.cmp(&b.id))
    });
    let mut selected = Vec::new();
    let mut selected_ids = Vec::new();
    let mut omitted = Vec::new();
    let mut tokens_used = 0usize;

    for item in candidates {
        if tokens_used.saturating_add(item.estimated_tokens) <= token_budget {
            tokens_used = tokens_used.saturating_add(item.estimated_tokens);
            selected_ids.push(item.id.clone());
            selected.push(item.clone());
        } else {
            omitted.push(item.id.clone());
        }
    }

    Ok((
        selected,
        ContextSelectionReport {
            selected_ids,
            excluded_by_classification: excluded,
            omitted_by_budget: omitted,
            tokens_used,
            token_budget,
        },
    ))
}

/// Validate a plan as a bounded DAG and return deterministic parallel execution groups.
pub fn validate_plan(plan: &ExecutionPlan, max_steps: usize) -> PlanValidationReport {
    let mut issues = Vec::new();
    if plan.steps.is_empty() {
        issues.push("plan contains no steps".into());
    }
    if plan.steps.len() > max_steps {
        issues.push(format!(
            "plan has {} steps; configured maximum is {max_steps}",
            plan.steps.len()
        ));
    }

    let mut by_id: BTreeMap<String, &PlanStep> = BTreeMap::new();
    for step in &plan.steps {
        if step.id.trim().is_empty() {
            issues.push("plan contains a step with an empty id".into());
            continue;
        }
        if by_id.insert(step.id.clone(), step).is_some() {
            issues.push(format!("duplicate plan step id: {}", step.id));
        }
    }

    let mut indegree: BTreeMap<String, usize> = by_id.keys().map(|id| (id.clone(), 0)).collect();
    let mut dependents: BTreeMap<String, Vec<String>> =
        by_id.keys().map(|id| (id.clone(), Vec::new())).collect();

    for step in by_id.values() {
        let mut local_dependencies = BTreeSet::new();
        for dependency in &step.depends_on {
            if dependency == &step.id {
                issues.push(format!("step {} depends on itself", step.id));
            } else if !by_id.contains_key(dependency) {
                issues.push(format!(
                    "step {} references missing dependency {}",
                    step.id, dependency
                ));
            } else if local_dependencies.insert(dependency) {
                *indegree.get_mut(&step.id).expect("step id exists") += 1;
                dependents
                    .get_mut(dependency)
                    .expect("dependency id exists")
                    .push(step.id.clone());
            }
        }
    }

    for children in dependents.values_mut() {
        children.sort();
    }
    let mut ready: BTreeSet<String> = indegree
        .iter()
        .filter_map(|(id, degree)| (*degree == 0).then_some(id.clone()))
        .collect();
    let mut parallel_groups = Vec::new();
    let mut visited = 0usize;

    while !ready.is_empty() {
        let current: Vec<String> = ready.iter().cloned().collect();
        ready.clear();
        visited += current.len();
        for id in &current {
            if let Some(children) = dependents.get(id) {
                for child in children {
                    let degree = indegree.get_mut(child).expect("child id exists");
                    *degree -= 1;
                    if *degree == 0 {
                        ready.insert(child.clone());
                    }
                }
            }
        }
        parallel_groups.push(current);
    }

    if visited != by_id.len() {
        issues.push("plan dependency graph contains a cycle".into());
    }
    PlanValidationReport {
        valid: issues.is_empty(),
        issues,
        parallel_groups,
    }
}
