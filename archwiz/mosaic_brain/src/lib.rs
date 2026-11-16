//! MOSAIC: bounded, deterministic methodology intelligence.
//!
//! This crate owns methodology-specific types and recommendations. It uses the
//! shared Brain extension contract but does not own orchestration, evidence
//! persistence, graph construction, experiment dispatch or promotion authority.

#![forbid(unsafe_code)]

mod adapter;
mod brain;

pub use adapter::{MosaicBrain, MosaicRequest, MosaicResponse};
pub use brain::{
    recommend, validate_identity, EvidenceKind, EvidenceRef, EvaluationSnapshot,
    MethodIdentity, Recommendation, RecommendationOutcome, RecommendationReason,
    ReviewVerdict, ValidationError,
};
