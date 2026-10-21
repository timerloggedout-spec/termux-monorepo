# Paper2Agent Scientific Factory — Proposal Manifest

Status: proposed / bounded design lane
Priority: P1
Source issue: #621
Related implementation: merged PR #695 (bounded evolutionary replay + Paper2Agent integration)
Canonical architecture: docs/ops/INTEGRATION-GRAPH-MATRIX.md
Evidence substrate: docs/ops/AGENT-EVIDENCE-SUBSTRATE.md

## Purpose

Define the missing middle between a research paper and a routable, scientifically validated agent:

Paper → Manifest → Claim/Method Graph → Environment → Capability Extraction → MCP Tools + Resources + Prompts → Reference Reproduction → Scientific Validation → Acceptance Certificate → Scientific Agent Registry → Hierarchical Router → MoneyBall/3L0

This is a specification/proposal surface. It does not claim scientific reproduction, certificate issuance, or scientific routing are implemented.

## Scope

In scope: content-addressed paper manifest; claim/method/result relationships; paper-scoped MCP resource/tool/prompt descriptors; reference-result reproduction; scientific-agent acceptance certificate; registry record; provenance/environment binding; untrusted-code security boundary.

Out of scope: automatic production ingestion; arbitrary repository execution on GitHub runners; autonomous scientific claims; treating ATES/3L0 as scientific validity; replacing the existing router or phase engine; making any provider/model the scientific authority.

## Promotion rule

The proposal remains non-authoritative until schemas, validators, bounded fixtures, and CI evidence are implemented and reviewed. No scientific agent may be treated as VALIDATED from documentation alone.
