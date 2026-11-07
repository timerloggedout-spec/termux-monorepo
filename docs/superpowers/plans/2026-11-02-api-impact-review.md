# API Impact Review Lane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Termux-compatible API change detector, strict API Impact Mapper result normalizer, auditable PR report, and assistant-assisted review workflow.

**Architecture:** A standard-library Python CLI detects configured API-surface changes from git base/head refs, validates optional mapper JSON against a repository-owned schema/contract, and emits deterministic JSON/Markdown reports. GitHub Actions runs the detector in read-only observation mode; the connected ChatGPT mapper is invoked only by an assistant/human workflow and never by an invented CI endpoint.

**Tech Stack:** Python 3 standard library, unittest, GitHub Actions, JSON Schema (documentation contract), existing repository integration-event/proposal conventions.

**Spec:** [2026-11-02-api-impact-review-design.md](../specs/2026-11-02-api-impact-review-design.md)

## Global Constraints

- No third-party Python dependencies in the Termux-compatible CLI.
- GitHub Actions permissions remain read-only.
- Never capture raw prompts, completions, credentials, cookies, or full diffs in report output.
- Never claim external mapper analysis ran when no mapper result was supplied.
- `cannot_determine` remains unresolved and is never coerced into a non-breaking result.
- Reports are advisory; they do not approve, merge, deploy, or mutate source code.
- Do not add the new workflow to a required-check policy until a separate promotion review approves it.

## Review Focus

- A stale report must not be accepted for a different head SHA or PR.
- Duplicate change/impact IDs and dangling evidence references must be rejected.
- An unknown API file must not be treated as an API surface unless explicitly configured.
- Mapper output with unresolved classifications must remain partial, not green/complete.
- Paths containing traversal or absolute paths must be rejected before report serialization.

---

## File Structure

- Create `config/integrations/api-impact-paths.json` — reviewed API-surface path policy.
- Create `docs/integrations/schemas/api-impact-mapper-input.schema.json` — accepted provider-output envelope.
- Create `docs/integrations/schemas/api-impact-report.schema.json` — normalized report contract.
- Create `scripts/integrations/api_impact/__init__.py` and `report.py` — pure normalization/validation.
- Create `scripts/integrations/api_impact/cli.py` — git diff and file IO boundary.
- Create `tests/test_api_impact_report.py` — behavior and failure contracts.
- Create `.agents/skills/api-impact-review/SKILL.md` — assistant-assisted mapper workflow.
- Create `.github/workflows/api-impact-review.yml` — read-only PR report workflow.
- Create `docs/integrations/API-IMPACT-REVIEW.md` — operations, limits, and onboarding.
- Modify `docs/integrations/README.md`, `INTEGRATION-REGISTRY.md`, `registry.json`, `SKILLS.md`, `docs/ops/SKILLS-INVENTORY.md`, and `docs/proposals/registry.yaml`.

## Task 1 — Define the report behavior (TDD)

- [ ] Write tests for deterministic not-applicable output, configured path detection, and analysis-required state.
- [ ] Run tests and confirm they fail because the report module is missing.
- [ ] Implement only the pure path-policy and report-state functions.
- [ ] Re-run tests; then add and test path traversal rejection.

## Task 2 — Normalize API Impact Mapper output (TDD)

- [ ] Add fixtures for valid extraction/classification/impact output, partial output, duplicate IDs, dangling evidence, unknown change IDs, and `cannot_determine`.
- [ ] Write tests before the normalizer.
- [ ] Run tests and observe expected failures.
- [ ] Implement strict parsing and validation without rewriting provider facts.
- [ ] Verify complete and partial valid fixtures pass; malformed and privacy-unsafe fixtures fail.

## Task 3 — Build CLI and report output (TDD)

- [ ] Test command behavior using temporary git repositories or injected changed-file lists.
- [ ] Implement `--base`, `--head`, `--pr-number`, `--mapper-input`, `--output-json`, and `--output-markdown`.
- [ ] Ensure no API changes produce `not_applicable`; API changes without mapper output produce `analysis_required`.
- [ ] Ensure mapper input is bound to the exact repository/head/PR identity.
- [ ] Test deterministic serialization and nonzero exit for invalid mapper input.

## Task 4 — GitHub Actions integration

- [ ] Add a pull_request workflow with read-only permissions and bounded timeout.
- [ ] Checkout full history, resolve base/head from trusted event fields, and invoke the CLI.
- [ ] Upload JSON and Markdown reports as artifacts.
- [ ] Fail only on malformed/stale supplied mapper reports; do not make missing provider analysis block merges during observation rollout.
- [ ] Validate workflow YAML and ensure it does not request secrets or write scopes.

## Task 5 — Assistant workflow + docs + registry

- [ ] Add the `api-impact-review` skill with exact tool call sequence: extract → classify → impact map.
- [ ] Require source quotes/evidence IDs and explicit missing-fields/limitations in the report.
- [ ] Update integration registry and skill navigation.
- [ ] Register APIII-001 proposal and link the implementation branch.
- [ ] Document how to attach a mapper result to a PR and what the CI status means.

## Task 6 — Verification and delivery

- [ ] Run focused tests, repository gate, Termux smoke, skill quality lane, and proposal lifecycle validator in CI.
- [ ] Inspect the complete diff for permissions, privacy, false-positive surface matching, and source-of-truth drift.
- [ ] Request fresh review (subagent unavailable in this session; record self-review if necessary).
- [ ] Open PR against `master` because `master-staging` is 10,502 commits behind and diverged from current `master`; record this governance deviation.
- [ ] Re-fetch PR head and all checks; require both repository gate and Termux smoke on the same immutable head SHA.
- [ ] Do not merge until the repository's applicable promotion policy is satisfied.

## Operating Loop

`RECON → PLAN → TEST (RED) → IMPLEMENT → TEST (GREEN) → REVIEW → COMMIT → WAIT → WATCH → RE-FETCH → COMPARE → RECORD → REPEAT`
