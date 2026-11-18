# MOSAIC Brain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build a bounded Rust subsystem that evaluates methodology identity and evidence, then returns explainable recommendations without side effects.

**Architecture:** Place a dedicated crate in \`archwiz/mosaic_brain/\`. Keep the Context Relationship Graph as the read-only evidence substrate and the existing proposal/FA-ADE process as the only promotion authority.

**Tech Stack:** Rust 2021, standard library only, Cargo, GitHub Actions, existing Python repository validators.

**Spec:** \`docs/superpowers/specs/2026-11-16-mosaic-brain-design.md\` and \`docs/proposals/active/continuous-capability-evolution-lab/MOSAIC-BRAIN-RFP.md\`.

## Global Constraints

- Keep the core pure, deterministic and free of network/filesystem side effects.
- Preserve method identity and artifact provenance.
- Use canonical DoE EXPERIMENT records; do not create a second run schema.
- Require an independent evaluator for promotion candidacy.
- Preserve unknown values as unknown; missing evidence cannot pass a gate.
- Keep actual state changes in existing proposal and FA-ADE governance.
- Keep the Context Relationship Rust accelerator dedicated to fragment fingerprinting and pointer-cost analysis.
- Keep Siglary notation definitions under Linguist custody.

## Review Focus

- Malformed or missing source commit and artifact hash: reject identity validation.
- Evaluator identity equals method owner: return HOLD.
- Unknown practical gain, gate state, regression state or rollback readiness: return HOLD.
- Critical regression or refuted review: return REVISE even if other fields are missing.
- Empty or malformed evidence reference: return HOLD and preserve the missing-evidence reason.

---

### MOS-001: Define the crate and identity contract

**Files:**
- Create: \`archwiz/mosaic_brain/Cargo.toml\`
- Create: \`archwiz/mosaic_brain/src/lib.rs\`
- Create: \`archwiz/mosaic_brain/src/brain.rs\`
- Test: \`archwiz/mosaic_brain/tests/brain_contract.rs\`

**Interfaces:**
- Produces \`MethodIdentity\`, \`EvidenceKind\`, \`EvidenceRef\`, \`ReviewVerdict\`, \`EvaluationSnapshot\`, \`Recommendation\`, \`ValidationError\`.
- Produces \`validate_identity(&MethodIdentity) -> Result<(), ValidationError>\`.

- [ ] Write failing tests for empty IDs, invalid 40-character source commit, invalid 64-character SHA-256 and a valid identity.
- [ ] Run \`cargo test --manifest-path archwiz/mosaic_brain/Cargo.toml\`; confirm the new tests fail before implementation.
- [ ] Implement the types and \`validate_identity\` using the standard library only.
- [ ] Run the focused Cargo tests; require all identity cases to pass.
- [ ] Commit the crate and tests with an imperative subject.

### MOS-002: Implement the pure recommendation function

**Files:**
- Modify: \`archwiz/mosaic_brain/src/brain.rs\`
- Test: \`archwiz/mosaic_brain/tests/brain_contract.rs\`

**Interfaces:**
- Consumes \`MethodIdentity\` and \`EvaluationSnapshot\`.
- Produces \`recommend(&MethodIdentity, &EvaluationSnapshot) -> Result<Recommendation, ValidationError>\`.

- [ ] Test that an independent VERIFIED review with evidence, practical gain, no critical regression, passing gates and rollback readiness yields PromotionCandidate.
- [ ] Test that same-owner review, empty evidence, malformed evidence, PARTIAL/PENDING review and unknown values yield HOLD.
- [ ] Test that REFUTED review or critical regression yields REVISE.
- [ ] Implement deterministic precedence: invalid identity is an error; refutation/regression yields REVISE; incomplete or non-independent evidence yields HOLD; only complete positive evidence yields PromotionCandidate.
- [ ] Run all Cargo tests and inspect the recommendation reasons for stable, actionable text.
- [ ] Commit the recommendation function and tests.

### MOS-003: Register the bounded context-graph scope

**Files:**
- Modify: \`config/context_relationships/scope_registry.json\`

**Interfaces:**
- Adds scope ID \`mosaic-brain\` for \`archwiz/mosaic_brain/**\` and the MOSAIC Brain design/RFP/plan/diagram sources.
- Leaves generated \`workspace/llm_map/context_relationships/**\` artifacts to the existing publisher.

- [ ] Add the scope entry with title, path globs, aliases and labels.
- [ ] Validate JSON parsing and scope-ID uniqueness.
- [ ] Run the existing context-relationship fixture tests and scope validator through repository CI.
- [ ] Record the existing graph manifest freshness and history-coverage limits.
- [ ] Commit the scope entry without manually editing generated graph artifacts.

### MOS-004: Add ICM navigation

**Files:**
- Create: \`docs/icm/objects/operations/mosaic-brain.md\`
- Modify: \`docs/icm/CLAUDE.md\`
- Modify: \`CLAUDE.md\`

**Interfaces:**
- Produces one route card describing the brain's location, scope, inputs, output and authority boundary.
- Adds one route row to the existing ICM catalog.

- [ ] Add the route card with source references and change-impact notes.
- [ ] Add the route row to the operations route table.
- [ ] Add the design and RFP paths to the collaborator entry.
- [ ] Re-fetch all changed files and verify the links resolve.
- [ ] Commit the ICM integration.

### MOS-005: Integrate SON through the Linguist lane

**Files:**
- Modify: \`docs/proposals/active/notation-sets/ITEMS.md\`
- Modify: \`docs/proposals/active/notation-sets/CAVEMAN-MICRO-DENSE-V2.md\`
- Create: \`docs/proposals/active/notation-sets/SIGLARY-SON-DO-STATEMENTS.md\`

**Interfaces:**
- Adds an NSE work item for the SON candidate profile.
- Preserves GLYPHS, CHORDS and OPERATORS as separate classes.
- Uses existing registered operators only until the Linguist rules.

- [ ] Register SON as a candidate with a named scope and explicit source links.
- [ ] Record the DO marker and punctuation as grammar delimiters rather than new operators.
- [ ] Verify that each displayed operator exists in the current Matrice.
- [ ] File the Linguist RFP and record its issue reference.
- [ ] Keep normative status pending until an independent Linguist ruling is recorded.
- [ ] Commit the notation proposal separately from the Rust implementation.

### MOS-006: Add focused CI and complete validation

**Files:**
- Create: \`.github/workflows/mosaic-brain.yml\`

**Interfaces:**
- Runs Rust formatting and tests when the crate or workflow changes.
- Uses read-only repository permissions.

- [ ] Add the focused workflow with pull-request path filters.
- [ ] Run Cargo formatting and all crate targets.
- [ ] Run proposal lifecycle, context-graph scope checks, repo-gate and Termux smoke on the same PR head.
- [ ] Re-fetch workflow runs and job logs until terminal.
- [ ] Record each result as PASS, FAIL, CANCELLED or PENDING with the exact head SHA.
- [ ] Commit the workflow and final validation record.
