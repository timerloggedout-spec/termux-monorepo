use termux_brain::{
    BrainExtension, ExtensionContext, ExtensionDescriptor, RunIdentity,
    BRAIN_EXTENSION_CONTRACT_VERSION,
};

use crate::{recommend, MethodIdentity, Recommendation, ValidationError, EvaluationSnapshot};

/// Stateless methodology specialist. The host decides when to invoke it.
#[derive(Debug, Clone, Copy, Default)]
pub struct MosaicBrain;

/// Domain input; evidence remains references to canonical repository records.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MosaicRequest {
    pub method: MethodIdentity,
    pub snapshot: EvaluationSnapshot,
}

/// Recommendation paired with the same orchestration identity that invoked it.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MosaicResponse {
    pub identity: RunIdentity,
    pub recommendation: Recommendation,
}

impl BrainExtension for MosaicBrain {
    type Request = MosaicRequest;
    type Response = MosaicResponse;
    type Error = ValidationError;

    fn descriptor(&self) -> ExtensionDescriptor {
        ExtensionDescriptor {
            extension_id: "org.termux.mosaic.methodology",
            domain_id: "methodology_intelligence",
            owner: "continuous-capability-evolution-lab",
            contract_version: BRAIN_EXTENSION_CONTRACT_VERSION,
        }
    }

    fn evaluate(
        &self,
        context: &ExtensionContext,
        request: &Self::Request,
    ) -> Result<Self::Response, Self::Error> {
        Ok(MosaicResponse {
            identity: context.identity.clone(),
            recommendation: recommend(&request.method, &request.snapshot)?,
        })
    }
}
