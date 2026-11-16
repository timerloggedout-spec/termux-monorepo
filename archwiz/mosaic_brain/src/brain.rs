use std::fmt;

/// Immutable identity for one version of a methodology.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MethodIdentity {
    pub method_id: String,
    pub version: String,
    pub owner_id: String,
    pub scope_id: String,
    /// Full 40-character Git commit SHA.
    pub source_commit: String,
    /// Full 64-character SHA-256 of the method artifact.
    pub artifact_sha256: String,
}

/// Evidence source class. Payloads remain in their canonical source systems.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum EvidenceKind {
    ExperimentRecord,
    PullRequest,
    Review,
    WorkflowRun,
    Commit,
    Other,
}

/// Pointer to canonical evidence; never an embedded source body.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EvidenceRef {
    pub source_id: String,
    pub source_uri: String,
    pub kind: EvidenceKind,
}

/// Independent-review state. Unknown and incomplete values remain explicit.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ReviewVerdict {
    Verified,
    Partial,
    Pending,
    Refuted,
    Unknown,
}

/// Bounded facts used to evaluate one immutable method version.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EvaluationSnapshot {
    pub evaluator_id: String,
    pub method_owner_id: String,
    pub review_verdict: ReviewVerdict,
    pub evidence: Vec<EvidenceRef>,
    pub practical_gain: Option<bool>,
    pub critical_regression: Option<bool>,
    pub required_gates_passed: Option<bool>,
    pub rollback_ready: Option<bool>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ValidationError {
    EmptyField(&'static str),
    InvalidSourceCommit,
    InvalidArtifactSha256,
}

impl fmt::Display for ValidationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::EmptyField(field) => write!(f, "method identity field must not be empty: {field}"),
            Self::InvalidSourceCommit => {
                write!(f, "source_commit must be exactly 40 hexadecimal characters")
            }
            Self::InvalidArtifactSha256 => {
                write!(f, "artifact_sha256 must be exactly 64 hexadecimal characters")
            }
        }
    }
}

impl std::error::Error for ValidationError {}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RecommendationOutcome {
    PromotionCandidate,
    Hold,
    Revise,
}

/// Stable reason codes make recommendations explainable and testable.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RecommendationReason {
    AllPromotionConditionsSatisfied,
    ReviewRefuted,
    CriticalRegression,
    EvaluatorNotIndependent,
    MethodOwnerMismatch,
    ReviewPartial,
    ReviewPending,
    ReviewUnknown,
    EvidenceMissing,
    EvidenceReferenceInvalid,
    PracticalGainNotEstablished,
    RegressionStatusUnknown,
    RequiredGatesNotPassed,
    RequiredGatesUnknown,
    RollbackNotReady,
    RollbackReadinessUnknown,
}

/// Advisory result only. This value does not mutate proposal or experiment state.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Recommendation {
    pub outcome: RecommendationOutcome,
    pub reasons: Vec<RecommendationReason>,
}

/// Validate immutable method identity. This checks shape and provenance fields;
/// it does not fetch or independently attest the referenced Git objects.
pub fn validate_identity(identity: &MethodIdentity) -> Result<(), ValidationError> {
    for (field, value) in [
        ("method_id", identity.method_id.as_str()),
        ("version", identity.version.as_str()),
        ("owner_id", identity.owner_id.as_str()),
        ("scope_id", identity.scope_id.as_str()),
    ] {
        if value.trim().is_empty() {
            return Err(ValidationError::EmptyField(field));
        }
    }

    if identity.source_commit.len() != 40
        || !identity.source_commit.bytes().all(|byte| byte.is_ascii_hexdigit())
    {
        return Err(ValidationError::InvalidSourceCommit);
    }

    if identity.artifact_sha256.len() != 64
        || !identity
            .artifact_sha256
            .bytes()
            .all(|byte| byte.is_ascii_hexdigit())
    {
        return Err(ValidationError::InvalidArtifactSha256);
    }

    Ok(())
}

fn evidence_is_valid(evidence: &EvidenceRef) -> bool {
    !evidence.source_id.trim().is_empty() && !evidence.source_uri.trim().is_empty()
}

/// Deterministically classify a method evaluation without performing side effects.
///
/// Precedence:
/// 1. Invalid method identity is an error.
/// 2. Refutation or a critical regression yields REVISE.
/// 3. Any missing, malformed, non-independent, unknown or non-positive required
///    fact yields HOLD.
/// 4. PromotionCandidate requires every positive condition to be explicit.
pub fn recommend(
    identity: &MethodIdentity,
    snapshot: &EvaluationSnapshot,
) -> Result<Recommendation, ValidationError> {
    validate_identity(identity)?;

    if snapshot.review_verdict == ReviewVerdict::Refuted {
        return Ok(Recommendation {
            outcome: RecommendationOutcome::Revise,
            reasons: vec![RecommendationReason::ReviewRefuted],
        });
    }

    if snapshot.critical_regression == Some(true) {
        return Ok(Recommendation {
            outcome: RecommendationOutcome::Revise,
            reasons: vec![RecommendationReason::CriticalRegression],
        });
    }

    let mut reasons = Vec::new();

    if snapshot.evaluator_id.trim().is_empty()
        || snapshot.evaluator_id == identity.owner_id
    {
        reasons.push(RecommendationReason::EvaluatorNotIndependent);
    }

    if snapshot.method_owner_id.trim().is_empty()
        || snapshot.method_owner_id != identity.owner_id
    {
        reasons.push(RecommendationReason::MethodOwnerMismatch);
    }

    match snapshot.review_verdict {
        ReviewVerdict::Verified => {}
        ReviewVerdict::Partial => reasons.push(RecommendationReason::ReviewPartial),
        ReviewVerdict::Pending => reasons.push(RecommendationReason::ReviewPending),
        ReviewVerdict::Unknown => reasons.push(RecommendationReason::ReviewUnknown),
        ReviewVerdict::Refuted => unreachable!("refuted review returned above"),
    }

    if snapshot.evidence.is_empty() {
        reasons.push(RecommendationReason::EvidenceMissing);
    } else if snapshot.evidence.iter().any(|item| !evidence_is_valid(item)) {
        reasons.push(RecommendationReason::EvidenceReferenceInvalid);
    }

    if snapshot.practical_gain != Some(true) {
        reasons.push(RecommendationReason::PracticalGainNotEstablished);
    }

    match snapshot.critical_regression {
        Some(false) => {}
        Some(true) => unreachable!("critical regression returned above"),
        None => reasons.push(RecommendationReason::RegressionStatusUnknown),
    }

    match snapshot.required_gates_passed {
        Some(true) => {}
        Some(false) => reasons.push(RecommendationReason::RequiredGatesNotPassed),
        None => reasons.push(RecommendationReason::RequiredGatesUnknown),
    }

    match snapshot.rollback_ready {
        Some(true) => {}
        Some(false) => reasons.push(RecommendationReason::RollbackNotReady),
        None => reasons.push(RecommendationReason::RollbackReadinessUnknown),
    }

    if reasons.is_empty() {
        Ok(Recommendation {
            outcome: RecommendationOutcome::PromotionCandidate,
            reasons: vec![RecommendationReason::AllPromotionConditionsSatisfied],
        })
    } else {
        Ok(Recommendation {
            outcome: RecommendationOutcome::Hold,
            reasons,
        })
    }
}
