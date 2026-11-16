use termux_brain::{
    BrainExtension, ExtensionContext, ExtensionContractError, ExtensionDescriptor,
    ExtensionInvocationError, RunIdentity, BRAIN_EXTENSION_CONTRACT_VERSION,
};

struct EchoExtension {
    descriptor: ExtensionDescriptor,
    fail: bool,
}

impl BrainExtension for EchoExtension {
    type Request = String;
    type Response = (RunIdentity, String);
    type Error = &'static str;

    fn descriptor(&self) -> ExtensionDescriptor {
        self.descriptor
    }

    fn evaluate(
        &self,
        context: &ExtensionContext,
        request: &Self::Request,
    ) -> Result<Self::Response, Self::Error> {
        if self.fail {
            return Err("specialist fixture failure");
        }
        Ok((context.identity.clone(), request.clone()))
    }
}

fn descriptor() -> ExtensionDescriptor {
    ExtensionDescriptor {
        extension_id: "org.termux.test.echo",
        domain_id: "test_echo",
        owner: "test-owner",
        contract_version: BRAIN_EXTENSION_CONTRACT_VERSION,
    }
}

fn context() -> ExtensionContext {
    ExtensionContext {
        identity: RunIdentity {
            orchestration_id: "orch-1".into(),
            cycle_id: "cycle-2".into(),
            attempt_id: "attempt-3".into(),
        },
        domain_id: "test_echo".into(),
    }
}

#[test]
fn valid_descriptor_passes_contract_validation() {
    assert_eq!(descriptor().validate(), Ok(()));
}

#[test]
fn empty_descriptor_fields_are_rejected() {
    let invalid = ExtensionDescriptor {
        extension_id: " ",
        ..descriptor()
    };
    assert_eq!(
        invalid.validate(),
        Err(ExtensionContractError::EmptyField("extension_id"))
    );
}

#[test]
fn unsupported_contract_version_is_rejected() {
    let invalid = ExtensionDescriptor {
        contract_version: "termux-monorepo.brain-extension.v99",
        ..descriptor()
    };
    assert!(matches!(
        invalid.validate(),
        Err(ExtensionContractError::UnsupportedContractVersion { .. })
    ));
}

#[test]
fn invocation_rejects_missing_run_identity_before_evaluation() {
    let extension = EchoExtension {
        descriptor: descriptor(),
        fail: true,
    };
    let mut invalid = context();
    invalid.identity.attempt_id.clear();

    assert_eq!(
        extension.invoke(&invalid, &"request".into()),
        Err(ExtensionInvocationError::Contract(
            ExtensionContractError::MissingIdentityField("attempt_id")
        ))
    );
}

#[test]
fn invocation_rejects_domain_mismatch_before_evaluation() {
    let extension = EchoExtension {
        descriptor: descriptor(),
        fail: true,
    };
    let mut invalid = context();
    invalid.domain_id = "another_domain".into();

    assert_eq!(
        extension.invoke(&invalid, &"request".into()),
        Err(ExtensionInvocationError::Contract(
            ExtensionContractError::DomainMismatch {
                expected: "test_echo",
                actual: "another_domain".into(),
            }
        ))
    );
}

#[test]
fn invocation_preserves_orchestration_cycle_and_attempt_identity() {
    let extension = EchoExtension {
        descriptor: descriptor(),
        fail: false,
    };
    let expected = context().identity;

    let (identity, response) = extension.invoke(&context(), &"hello".into()).unwrap();

    assert_eq!(identity, expected);
    assert_eq!(response, "hello");
}

#[test]
fn specialist_errors_remain_distinct_from_contract_errors() {
    let extension = EchoExtension {
        descriptor: descriptor(),
        fail: true,
    };

    assert_eq!(
        extension.invoke(&context(), &"hello".into()),
        Err(ExtensionInvocationError::Evaluation(
            "specialist fixture failure"
        ))
    );
}
