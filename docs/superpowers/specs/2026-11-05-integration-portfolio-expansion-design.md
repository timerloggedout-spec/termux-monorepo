# Integration Portfolio Expansion — Design

**Status:** Approved for implementation by the operator directive to maintain and provision the named integrations  
**Date:** 2026-11-05  
**Proposal:** [integration-portfolio-expansion](../../proposals/active/integration-portfolio-expansion/MANIFEST.md)

## Intent

Expand the existing Integration Intelligence foundation from its original eight-provider baseline to a complete, evidence-backed inventory of the additional tools named by the operator. Maintain one canonical registry, one human-readable portfolio, and one published documentation navigation surface. Preserve each provider's distinct capabilities and trust boundaries.

## Goals

1. Register 24 additional integration surfaces, including separate records for public DeepWiki.com and private DEVINdeepWiki.
2. Distinguish connected tools, installed skills, user-reported provisioning, implemented repository workflows, plan blockers, and validated runtime behavior.
3. Record current evidence and next validation step for each integration.
4. Publish the portfolio through the existing Mintlify site without creating a parallel documentation platform.
5. Convert Agent Ready findings into source-level remediation work without patching generated HTML blindly.
6. Preserve the existing normalized integration event schema and adapter contract.

## Non-goals

- Implement all provider-specific adapters in one PR.
- Treat a connector exposed in this assistant session as available to Actions, Termux, or production.
- Read or store secret values, private session transcripts, or personal data.
- Upgrade paid plans, create accounts, change billing, or provision identity infrastructure without an explicit supported flow.
- Create calendar events, trigger external research spend, or perform unrelated provider mutations.
- Bypass the assigned builder/evaluator separation on DeepWiki refresh issue #3346.
- Publish directly to Mintlify or merge the PR as part of this change.

## Architecture

Repository-owned `docs/integrations/registry.json` remains the machine-readable source. `INTEGRATION-REGISTRY.md` provides the prioritized human-readable catalog, while `INTEGRATION-PORTFOLIO.md` records time-bound session evidence and provisioning blockers. The existing adapter contract and integration-event JSON Schema remain canonical interfaces.

Mintlify reads the same repository and `docs.json`. The new portfolio pages are added to the existing Documentation tab. External providers remain bounded observation or operation surfaces; Git history, source code, proposal records, and CI are authoritative for repository state.

## Capability vocabulary

Use the existing vocabulary without adding an ambiguous `integrated` boolean:

- `discovered`
- `tool_connected_in_session`
- `skill_installed_in_session`
- `not_exposed_in_session`
- `repo_adapter_planned`
- `repo_adapter_implemented`
- `validated`
- `promoted`

User-reported secret provisioning is recorded in `session_evidence` as reported and unverified until a successful runtime run proves it.

## Priority lanes

| Priority | Lane | Integrations |
|---|---|---|
| P0 | Documentation and engineering quality | Context7, Mintlify, Agent Ready, AI Task Brief Builder; Superpowers and API Impact Mapper remain existing P0 entries |
| P1 | Wiki, research, orchestration, collaboration, design | Devin AI / DEVINdeepWiki, DeepWiki.com, Mermaid Chart, Engram, Context.dev, Consensus, Opscotch, Temporal, SiteTriage, Product Design, Flow, TinyFish, Manus |
| P2 | Specialized, account-gated, or sensitive | Ahrefs, Soracom Knowledge, Inductive Bio, Google Calendar, Precise Special Functions, Sixtyfour Intelligence, WorkOS |

Priorities indicate expected compounding value, not current readiness or entitlement.

## Observed session evidence

- Mintlify deployment `diasporic3lee7` is connected to `timerloggedout-spec/termux-monorepo` on `master`.
- Agent Ready scan `m2cu05sDfw` returned Vercel 73, llms.txt 87, accessibility 88.
- DeepWiki.com reported last indexed 2026-08-20 at `ed3db046`; issue #3346 is the existing refresh campaign.
- Mermaid Chart is authenticated but has no saved diagrams.
- Ahrefs usage inspection is plan-blocked.
- WorkOS login is authenticated but no dashboard account exists.
- Inductive Bio model discovery returned public LogD and pKa models.
- Opscotch root guidance was retrieved.
- Temporal and Product Design skills are installed in this assistant environment.
- Devin indexing code exists; secret provisioning is user-reported and not independently verified here.

## Security and governance

- Keep credentials names-only in repository documentation; never read or emit values.
- Default to read-only; require explicit authorization for writes, billing, deployment, calendar mutations, external research spend, and identity changes.
- Treat provider output as untrusted, non-canonical evidence.
- Preserve immutable repository SHA, provider/source identity, timestamps, and idempotency.
- Never promote based on connector visibility or provider claims alone.
- Keep DeepWiki.com, DEVINdeepWiki, and deepwiki-rs credential families separate.

## Acceptance criteria

- The machine-readable registry contains 32 unique integration IDs: the existing eight plus 24 requested entries.
- Every new entry declares priority, discovery state, session evidence, repository adapter state, authority, write boundary, next step, and sensitivity.
- The human-readable catalog and portfolio agree with the machine registry.
- Mintlify navigation exposes the new pages without removing existing entries.
- The design and plan explicitly preserve the current event schema and adapter contract.
- JSON parsing and unique-ID checks pass; CI validates the repository gates on the PR head.
- No secret values, personal calendar data, provider prompts, or private transcripts are committed.
