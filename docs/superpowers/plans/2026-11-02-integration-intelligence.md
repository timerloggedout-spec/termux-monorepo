# Integration Intelligence — Implementation Plan

**Design:** [2026-11-02-integration-intelligence-design.md](../specs/2026-11-02-integration-intelligence-design.md)
**Proposal:** IIS-001
**Branch:** `feat/integration-intelligence-superpowers`

## Task 1 — Register the work

1. Add the proposal manifest and itemized acceptance criteria.
2. Register the proposal in `docs/proposals/registry.yaml`.
3. Verify the proposal path and item ID match exactly.

**Verification:** run `python scripts/proposals/validate_registry.py` in a full checkout.

## Task 2 — Publish the repository-native Superpowers skill

Create `.agents/skills/superpowers/SKILL.md` with:
- valid YAML frontmatter;
- workflow routing for brainstorming, design, worktrees, plans, TDD, debugging, parallel work, code review, verification, and branch finishing;
- repository-specific policy precedence and approval boundaries;
- commands and required evidence for local validation;
- official upstream repository and pinned reference metadata;
- installation/update instructions for common agent harnesses.

**Verification:** run `python scripts/ci/evaluate_skills.py --json` and `python -m unittest tests.test_skill_evaluation -v`.

## Task 3 — Define the Integration Intelligence contract

Create:
- `docs/integrations/README.md`;
- `docs/integrations/INTEGRATION-REGISTRY.md`;
- `docs/integrations/registry.json`;
- `docs/integrations/ADAPTER-CONTRACT.md`;
- `docs/integrations/schemas/integration-event.schema.json`.

Record each provider's priority, domain, current session capability evidence, repo adapter status, permitted data, write boundary, cost/consent boundary, and next validation step.

**Verification:** parse both JSON files; validate registry references and event examples against the schema; check no credential-shaped values or raw prompt/session content are present.

## Task 4 — Wire skill discovery

Update:
- `SKILLS.md`;
- `docs/ops/SKILLS-INVENTORY.md`;
- `CLAUDE.md`.

Add the skill to the role-load matrix and explain that Superpowers supplements but does not override repository governance.

**Verification:** every linked path exists; skill inventory includes the new directory exactly once; no existing skill entries are removed.

## Task 5 — Review and deliver

1. Run skill evaluation, proposal registry validation, repo gate, and Termux smoke in a full checkout.
2. Review the diff for scope, security, duplication, and source-of-truth violations.
3. Commit with `Implements: IIS-001`.
4. Open a PR to `master`.
5. WAIT for both gates; re-fetch checks and verify both passed on the same immutable head SHA.
6. Do not merge/promote while checks or reviews are pending.

**Current execution constraint:** this session has GitHub contents/branch operations but no local repository checkout or shell test runner. The GitHub API can create and re-fetch files/commits, but cannot substitute for the repo's executable validators. CI evidence must therefore be obtained from the PR before completion is claimed.

## Phased follow-on roadmap

| Phase | Lane | Deliverable | Exit evidence |
|---|---|---|---|
| A | Foundation | Registry, event schema, adapter contract, Superpowers skill | JSON/schema and skill-evaluation pass |
| B | Engineering | [API Impact Review lane](2026-11-02-api-impact-review.md) + Superpowers review/TDD adoption | SHA-bound report, mapper-result validator, focused tests, read-only PR workflow; advisory rollout |
| C | Research | EmpirioLabs + Domino experiment adapters | Reproducible run manifests, dataset/model provenance, cost caps |
| D | Efficiency | Cache Stats + ATES/WTCV measurement mapping | Cache/context metrics with privacy review and baseline comparison |
| E | Visual cockpit | tldraw workspace + D3/SVG/Mermaid source alignment | Source-linked diagram export and accessibility checks |
| F | Specialized research | Alloy robotics/edge evidence lane | Device/mission provenance and isolated data classification |
| G | Communications | Klaviyo opt-in release/research channel | Consent audit, unsubscribe handling, campaign measurement |

## Continuous operating loop

`RECON → PLAN → IMPLEMENT → TEST → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → RECORD → REPEAT`

Distinguish `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` in every status report.
