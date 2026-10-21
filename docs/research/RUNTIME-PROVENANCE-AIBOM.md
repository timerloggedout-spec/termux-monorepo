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

## Drift

A new observation is appended rather than overwriting an older observation.
Environment, model, tool, dependency, or artifact drift becomes explicit evidence.

## Security

Never store secrets, credentials, prompts, completions, or arbitrary tool payloads
in the canonical manifest. Dynamic capability admission must retain identity and
version/digest evidence.
