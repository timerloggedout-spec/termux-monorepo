//! Cargo facade for the repository-root brain.rs source of truth.

#[path = "../../brain.rs"]
mod shared_brain;

pub use shared_brain::*;
