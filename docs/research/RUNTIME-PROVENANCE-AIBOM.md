# Runtime Provenance / AIBOM Contract

## Purpose

Extend static SBOM thinking into execution provenance for agentic workloads.

The repository must be able to answer: what executed, from which artifacts, under
which environment, using which tools, and producing which result?

## Runtime manifest

A run manifest records run ID, source SHA, environment digest, runtime/version,
model digest, model quantization, tool inventory, MCP servers, A2A peers,
dependency snapshot, artifact digests, execution-event stream digest, result digest,
and generated_at.

## Standards alignment

The manifest is compatible with SBOM/provenance ecosystems such as SPDX, CycloneDX
and SLSA, but remains a repository-level open JSON contract.

Build provenance for the manifest is an attestation problem, not a logging
problem: the recorded engine option is Witness (in-toto), which wraps the
build command and emits signed attestations of command, materials, and
products that a CI verify step can gate on. It is recorded in the
supply-chain-provenance category of
`docs/ops/FOSS-FORESIGHT-PROCUREMENT-REGISTRY.json` and wired as
`witness-attestation` in `config/agent_stack_integrations.json`. Attestations
complement this manifest; they do not replace the repository-owned evidence
envelope as the canonical evidence record.

## Drift

A new observation is appended rather than overwriting an older observation.
Environment, model, tool, dependency, or artifact drift becomes explicit evidence.

## Security

Never store secrets, credentials, prompts, completions, or arbitrary tool payloads
in the canonical manifest. Dynamic capability admission must retain identity and
version/digest evidence.
