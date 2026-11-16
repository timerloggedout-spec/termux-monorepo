use mosaic_brain::{
    recommend, validate_identity, EvidenceKind, EvidenceRef, EvaluationSnapshot, MethodIdentity,
    RecommendationOutcome, RecommendationReason, ReviewVerdict, ValidationError, MosaicBrain,
    MosaicRequest,
};
use termux_brain::{BrainExtension, ExtensionContext, RunIdentity};

fn identity() -> MethodIdentity {
    MethodIdentity {
        method_id: "methodology.factorial-design".into(),
        version: "1.0.0".into(),
        owner_id: "doe-owner".into(),
        scope_id: "methodology_intelligence".into(),
        source_commit: "0123456789abcdef0123456789abcdef01234567".into(),
        artifact_sha256: "a".repeat(64),
    }
}

fn evidence() -> EvidenceRef {
    EvidenceRef {
        source_id: "experiment:run-17".into(),
        source_uri: "repo://docs/ops/corpus/EXPERIMENT.schema.json#run-17".into(),
        kind: EvidenceKind::ExperimentRecord,
    }
}

fn snapshot() -> EvaluationSnapshot {
    EvaluationSnapshot {
        evaluator_id: "independent-reviewer".into(),
        method_owner_id: "doe-owner".into(),
        review_verdict: ReviewVerdict::Verified,
        evidence: vec![evidence()],
        practical_gain: Some(true),
        critical_regression: Some(false),
        required_gates_passed: Some(true),
        rollback_ready: Some(true),
    }
}

#[test]
fn valid_method_identity_passes() {
    assert_eq!(validate_identity(&identity()), Ok(()));
}

#[test]
fn empty_method_identity_field_is_rejected() {
    let mut invalid = identity();
    invalid.method_id.clear();
    assert_eq!(
        validate_identity(&invalid),
        Err(ValidationError::EmptyField("method_id"))
    );
}

#[test]
fn malformed_source_commit_is_rejected() {
    let mut invalid = identity();
    invalid.source_commit = "not-a-commit".into();
    assert_eq!(
        validate_identity(&invalid),
        Err(ValidationError::InvalidSourceCommit)
    );
}

#[test]
fn malformed_artifact_hash_is_rejected() {
    let mut invalid = identity();
    invalid.artifact_sha256 = "xyz".into();
    assert_eq!(
        validate_identity(&invalid),
        Err(ValidationError::InvalidArtifactSha256)
    );
}

#[test]
fn complete_independent_evidence_yields_promotion_candidate() {
    let result = recommend(&identity(), &snapshot()).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::PromotionCandidate);
    assert_eq!(
        result.reasons,
        vec![RecommendationReason::AllPromotionConditionsSatisfied]
    );
}

#[test]
fn same_owner_evaluation_is_held() {
    let mut input = snapshot();
    input.evaluator_id = "doe-owner".into();
    let result = recommend(&identity(), &input).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::Hold);
    assert!(result.reasons.contains(&RecommendationReason::EvaluatorNotIndependent));
}

#[test]
fn owner_identity_mismatch_is_held() {
    let mut input = snapshot();
    input.method_owner_id = "other-owner".into();
    let result = recommend(&identity(), &input).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::Hold);
    assert!(result.reasons.contains(&RecommendationReason::MethodOwnerMismatch));
}

#[test]
fn missing_evidence_is_held() {
    let mut input = snapshot();
    input.evidence.clear();
    let result = recommend(&identity(), &input).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::Hold);
    assert!(result.reasons.contains(&RecommendationReason::EvidenceMissing));
}

#[test]
fn malformed_evidence_reference_is_held() {
    let mut input = snapshot();
    input.evidence[0].source_uri.clear();
    let result = recommend(&identity(), &input).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::Hold);
    assert!(result.reasons.contains(&RecommendationReason::EvidenceReferenceInvalid));
}

#[test]
fn incomplete_review_is_held() {
    for verdict in [ReviewVerdict::Partial, ReviewVerdict::Pending, ReviewVerdict::Unknown] {
        let mut input = snapshot();
        input.review_verdict = verdict;
        let result = recommend(&identity(), &input).unwrap();
        assert_eq!(result.outcome, RecommendationOutcome::Hold);
    }
}

#[test]
fn unknown_or_negative_practical_gain_is_held() {
    for gain in [None, Some(false)] {
        let mut input = snapshot();
        input.practical_gain = gain;
        assert_eq!(
            recommend(&identity(), &input).unwrap().outcome,
            RecommendationOutcome::Hold
        );
    }
}

#[test]
fn unknown_regression_status_is_held() {
    let mut input = snapshot();
    input.critical_regression = None;
    assert_eq!(
        recommend(&identity(), &input).unwrap().outcome,
        RecommendationOutcome::Hold
    );
}

#[test]
fn failed_or_unknown_required_gates_are_held() {
    for gates in [None, Some(false)] {
        let mut input = snapshot();
        input.required_gates_passed = gates;
        assert_eq!(
            recommend(&identity(), &input).unwrap().outcome,
            RecommendationOutcome::Hold
        );
    }
}

#[test]
fn false_or_unknown_rollback_readiness_is_held() {
    for rollback in [None, Some(false)] {
        let mut input = snapshot();
        input.rollback_ready = rollback;
        assert_eq!(
            recommend(&identity(), &input).unwrap().outcome,
            RecommendationOutcome::Hold
        );
    }
}

#[test]
fn critical_regression_precedes_other_missing_evidence_and_yields_revise() {
    let mut input = snapshot();
    input.evidence.clear();
    input.critical_regression = Some(true);
    let result = recommend(&identity(), &input).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::Revise);
    assert_eq!(result.reasons, vec![RecommendationReason::CriticalRegression]);
}

#[test]
fn refuted_review_yields_revise() {
    let mut input = snapshot();
    input.review_verdict = ReviewVerdict::Refuted;
    let result = recommend(&identity(), &input).unwrap();
    assert_eq!(result.outcome, RecommendationOutcome::Revise);
    assert_eq!(result.reasons, vec![RecommendationReason::ReviewRefuted]);
}

#[test]
fn root_brain_invokes_mosaic_through_the_shared_extension_contract() {
    let extension = MosaicBrain;
    let context = ExtensionContext {
        identity: RunIdentity {
            orchestration_id: "orch-7".into(),
            cycle_id: "cycle-4".into(),
            attempt_id: "attempt-2".into(),
        },
        domain_id: "methodology_intelligence".into(),
    };
    let expected_identity = context.identity.clone();
    let request = MosaicRequest {
        method: identity(),
        snapshot: snapshot(),
    };

    let response = extension.invoke(&context, &request).unwrap();

    assert_eq!(response.identity, expected_identity);
    assert_eq!(
        response.recommendation.outcome,
        RecommendationOutcome::PromotionCandidate
    );
}
