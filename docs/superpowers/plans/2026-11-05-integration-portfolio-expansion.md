# Integration Portfolio Expansion Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Extend Integration Intelligence with a complete, evidence-backed portfolio of the requested tools and expose it through the existing Mintlify documentation site.

**Architecture:** Keep `registry.json` as the machine-readable source, pair it with a human-readable catalog and dated portfolio audit, and add both pages to the existing `docs.json` navigation. Preserve the current adapter contract and event schema; provider-specific runtime adapters remain separate follow-on proposals.

**Tech Stack:** JSON, Markdown/MDX, Mintlify `docs.json`, GitHub Git Data API, existing repository CI.

**Spec:** `docs/superpowers/specs/2026-11-05-integration-portfolio-expansion-design.md`

## Global Constraints

- Repository source and GitHub CI remain authoritative.
- Session connector visibility is not production availability.
- Keep secret values, personal data, prompts, and private session content out of the registry.
- Default external integrations to read-only.
- Do not change the normalized integration event schema.
- Do not publish Mintlify or merge the PR from this task.
- Preserve all existing navigation entries and proposal lifecycle rules.

## Review Focus

- Duplicate integration IDs or drift between JSON and Markdown inventory.
- Incorrectly upgrading a user-reported secret state to verified.
- Conflating public DeepWiki.com, private DEVINdeepWiki, and deepwiki-rs.
- Navigation rewrite accidentally dropping existing pages.
- Scanner recommendations applied to generated framework output instead of repository-owned source.

---

### Task 1: Extend the canonical registry

**Files:**
- Modify: `docs/integrations/registry.json`
- Modify: `docs/integrations/INTEGRATION-REGISTRY.md`

**Interfaces:**
- Consumes: existing registry fields and capability vocabulary.
- Produces: 32 unique integration records with stable IDs and explicit next steps.

- [ ] Add 24 entries for the named tools, separating DeepWiki.com from DEVINdeepWiki.
- [ ] Preserve the existing eight records.
- [ ] Run JSON parsing and assert 32 unique IDs.
- [ ] Verify every new entry contains the existing required fields.
- [ ] Update the Markdown catalog and verify each record is represented once.

### Task 2: Publish the evidence-backed portfolio audit

**Files:**
- Create: `docs/integrations/INTEGRATION-PORTFOLIO.md`
- Modify: `docs/integrations/README.md`

**Interfaces:**
- Consumes: Task 1 registry and verified session evidence.
- Produces: a dated human-readable audit of readiness, blockers, DeepWiki provenance, Agent Ready findings, and next actions.

- [ ] Record the Mintlify deployment and Agent Ready scan evidence.
- [ ] Record the stale public DeepWiki source ref and open issue #3346.
- [ ] Record Ahrefs and WorkOS blockers without attempting billing or account mutations.
- [ ] Record Devin secret provisioning as operator-reported and unverified.
- [ ] Document the phased adoption order and explicit no-write boundaries.

### Task 3: Expose the portfolio in Mintlify navigation

**Files:**
- Modify: `docs.json`

**Interfaces:**
- Consumes: Task 2 page paths.
- Produces: an Integrations group under the existing Documentation tab.

- [ ] Add the portfolio and registry page paths to a new Integrations group.
- [ ] Preserve every existing group and page.
- [ ] Parse `docs.json` and assert both new page paths are present exactly once.

### Task 4: Register the proposal and implementation plan

**Files:**
- Create: `docs/proposals/active/integration-portfolio-expansion/MANIFEST.md`
- Create: `docs/proposals/active/integration-portfolio-expansion/ITEMS.md`
- Modify: `docs/proposals/registry.yaml`
- Create: this design and plan pair.

**Interfaces:**
- Consumes: accepted operator directive and existing proposal schema.
- Produces: proposal ID `integration-portfolio-expansion`, work item `IPX-001`, and a durable review record.

- [ ] Register the proposal with P1 priority and required gates.
- [ ] Record operator authorization and scope boundaries.
- [ ] Keep provider adapter implementations as separate future work items.
- [ ] Verify manifest path and registry entry agree.

### Task 5: Validate and open the review

**Files:**
- Review all files changed in Tasks 1-4.

**Interfaces:**
- Consumes: completed docs branch.
- Produces: one PR targeting `master`, with CI evidence attached to the exact head SHA.

- [ ] Parse `registry.json` and `docs.json`.
- [ ] Check unique IDs and navigation path parity.
- [ ] Check for credential-shaped values and accidental private data.
- [ ] Re-fetch branch head and PR state.
- [ ] Wait for repo gate, Termux smoke, proposal lifecycle, and documentation checks to reach terminal states.
- [ ] Re-fetch the final checks on the exact head SHA; do not merge or publish in this task.

## Execution note

This session has GitHub repository APIs but no local checkout or shell test runner. Static JSON and inventory checks can be performed in the execution harness; repository-specific Python validators and gates must be run by CI on the PR branch. Report those as pending until observed.
