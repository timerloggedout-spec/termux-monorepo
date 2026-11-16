//! Cargo facade for the repository-root brain.rs source of truth.

#[path = "../../brain.rs"]
mod shared_brain;

pub use shared_brain::*;

pub mod extensions;
pub use extensions::{
    BrainExtension, ExtensionContext, ExtensionContractError, ExtensionDescriptor,
    ExtensionInvocationError, BRAIN_EXTENSION_CONTRACT_VERSION,
};
