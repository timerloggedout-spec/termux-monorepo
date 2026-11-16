//! A small, typed seam for domain-specific Brain extensions.
//!
//! The shared kernel defines this contract; domain crates implement it. The
//! host composes both crates. This is intentionally static and dependency-free:
//! it is not a dynamic plugin loader, capability registry, scheduler or policy
//! authority.

use crate::RunIdentity;

/// Version of the shared specialist-extension contract.
pub const BRAIN_EXTENSION_CONTRACT_VERSION: &str = "termux-monorepo.brain-extension.v1";

/// Stable metadata describing one specialist implementation.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ExtensionDescriptor {
    /// Stable, repository-scoped identifier for this implementation.
    pub extension_id: &'static str,
    /// Domain routed to this specialist, e.g. `methodology_intelligence`.
    pub domain_id: &'static str,
    /// Canonical owner of the specialist implementation.
    pub owner: &'static str,
    /// Version of this shared contract, independent of the specialist's own version.
    pub contract_version: &'static str,
}

impl ExtensionDescriptor {
    /// Validate stable identity and exact contract compatibility.
    pub fn validate(&self) -> Result<(), ExtensionContractError> {
        for (field, value) in [
            ("extension_id", self.extension_id),
            ("domain_id", self.domain_id),
            ("owner", self.owner),
        ] {
            if value.trim().is_empty() {
                return Err(ExtensionContractError::EmptyField(field));
            }
        }

        if self.contract_version != BRAIN_EXTENSION_CONTRACT_VERSION {
            return Err(ExtensionContractError::UnsupportedContractVersion {
                expected: BRAIN_EXTENSION_CONTRACT_VERSION,
                actual: self.contract_version,
            });
        }

        Ok(())
    }
}

/// Invocation metadata shared across the host/kernel/specialist boundary.
///
/// The identity is copied from the existing orchestration contract. Extensions
/// must not create a parallel task, cycle or attempt identity.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExtensionContext {
    pub identity: RunIdentity,
    pub domain_id: String,
}

impl ExtensionContext {
    fn validate(&self) -> Result<(), ExtensionContractError> {
        for (field, value) in [
            ("orchestration_id", self.identity.orchestration_id.as_str()),
            ("cycle_id", self.identity.cycle_id.as_str()),
            ("attempt_id", self.identity.attempt_id.as_str()),
        ] {
            if value.trim().is_empty() {
                return Err(ExtensionContractError::MissingIdentityField(field));
            }
        }

        if self.domain_id.trim().is_empty() {
            return Err(ExtensionContractError::EmptyField("domain_id"));
        }

        Ok(())
    }
}

/// Fail-closed contract validation errors.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ExtensionContractError {
    EmptyField(&'static str),
    MissingIdentityField(&'static str),
    UnsupportedContractVersion {
        expected: &'static str,
        actual: &'static str,
    },
    DomainMismatch {
        expected: &'static str,
        actual: String,
    },
}

impl std::fmt::Display for ExtensionContractError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::EmptyField(field) => write!(f, "extension field must not be empty: {field}"),
            Self::MissingIdentityField(field) => {
                write!(f, "missing run identity field: {field}")
            }
            Self::UnsupportedContractVersion { expected, actual } => write!(
                f,
                "unsupported Brain extension contract version: expected {expected}, got {actual}"
            ),
            Self::DomainMismatch { expected, actual } => write!(
                f,
                "extension domain mismatch: expected {expected}, got {actual}"
            ),
        }
    }
}

impl std::error::Error for ExtensionContractError {}

/// Error boundary that distinguishes invalid invocation from specialist failure.
#[derive(Debug, PartialEq, Eq)]
pub enum ExtensionInvocationError<E> {
    Contract(ExtensionContractError),
    Evaluation(E),
}

/// Statically typed specialist interface implemented by domain-owned crates.
///
/// The host owns composition and routing. The root Brain crate owns only this
/// contract; it never imports or depends on a concrete specialist crate.
pub trait BrainExtension {
    type Request;
    type Response;
    type Error;

    /// Return stable identity and compatibility metadata.
    fn descriptor(&self) -> ExtensionDescriptor;

    /// Evaluate a domain request without taking over host orchestration.
    fn evaluate(
        &self,
        context: &ExtensionContext,
        request: &Self::Request,
    ) -> Result<Self::Response, Self::Error>;

    /// Validate the descriptor, run identity and requested domain before calling
    /// the specialist. Invalid context never reaches domain evaluation.
    fn invoke(
        &self,
        context: &ExtensionContext,
        request: &Self::Request,
    ) -> Result<Self::Response, ExtensionInvocationError<Self::Error>> {
        let descriptor = self.descriptor();
        descriptor
            .validate()
            .map_err(ExtensionInvocationError::Contract)?;
        context
            .validate()
            .map_err(ExtensionInvocationError::Contract)?;

        if context.domain_id != descriptor.domain_id {
            return Err(ExtensionInvocationError::Contract(
                ExtensionContractError::DomainMismatch {
                    expected: descriptor.domain_id,
                    actual: context.domain_id.clone(),
                },
            ));
        }

        self.evaluate(context, request)
            .map_err(ExtensionInvocationError::Evaluation)
    }
}
