---
name: research-implementation-recon
description: Evidence-first reconnaissance for existing repository capabilities, FOSS/AI tooling, integration overlap, license/provenance review, and safe incremental implementation. Use before adding dependencies or building parallel subsystems.
---

# Research & Implementation Recon Skill

## Mission

Find what already exists before creating more. Convert external research into repository-grounded, license-aware, testable implementation plans. Optimize for compounding value and minimal duplicate infrastructure.

## Required loop

`RECON → INVENTORY → TRIAGE → RESEARCH → LICENSE REVIEW → DESIGN → IMPLEMENT → TEST → WAIT → RE-FETCH → RECONCILE → DOCUMENT → REPEAT`

## Recon protocol

1. Freeze the exact repository, branch/ref, and immutable SHA. Record when the observation was made.
2. Inspect existing source, docs, workflows, scripts, schemas, skills, issues, PRs, comments, CI runs, and artifacts before proposing a new subsystem.
3. Search both paths and content. A filename/path search alone cannot prove absence. Report search limits explicitly.
4. Build a capability matrix with `EXISTS`, `PARTIAL`, `PROPOSED`, `BLOCKED`, or `RETIRED`; each claim needs a path, URL, test/run/artifact, or explicit `UNVERIFIED` state.
5. Research primary upstream sources first: canonical repo, official docs, release notes, license files, model cards and dataset terms. Treat directories, blog posts, mirrors, and search snippets as leads only.
6. Separate product code license, transitive dependencies, datasets, model weights, prompts/docs, hosted service terms, data retention, and security policy. Unknown means `REVIEW_REQUIRED`.
7. Prefer standards and narrow adapters over vendor-specific coupling. Never introduce two tools with overlapping roles without a measured reason and an explicit decision.
8. Define expected outcomes, failure modes, cost ceiling, privacy/redaction, provenance, rollback, and acceptance tests before implementation.
9. Implement the smallest reversible vertical slice. Do not silently change protected-branch, credential, deployment, merge, or autonomous-write authority.
10. Test locally where possible and in CI. Re-fetch the branch/PR after writes; verify exact head SHA, check runs, artifacts, comments and issue links.
11. Distinguish `COMMITTED`, `EXECUTED`, `VALIDATED`, `OBSERVED`, and `PROMOTED`. Never infer one state from another.
12. Update the source-of-truth document, machine-readable inventory, PR body, issue evidence and citations in the same workstream.

## Evidence envelope

For every important claim, preserve:
- claim ID and scope;
- exact source commit and changed paths;
- upstream source URL/revision and license-review state;
- test/run/job/artifact IDs and hashes;
- outcome `PASS`, `FAIL`, `PARTIAL`, `UNKNOWN`, or `ERROR`;
- timestamp, owner/reviewer, limitations, and superseding evidence.

A commit message is intent, not proof. A green workflow proves only the behavior it ran. Mock success proves wiring, not live inference. A reachable endpoint proves reachability, not task quality. A missing or rate-limited observation is not a model failure.

## FOSS integration rules

- Start from the capability gap, not a favorite tool.
- Compare at least one native/clean-room option against any third-party dependency.
- Pin immutable revisions in production workflows.
- Never copy code, datasets, model weights or prompts until their applicable terms are reviewed.
- Record attribution and license obligations even when integration is adapter-only.
- Keep external tools optional and advisory until value and operational burden are demonstrated.
- Do not let an external evaluator certify itself or authorize repository writes.

## Stop conditions

Stop and document instead of guessing when the source is inaccessible, license is unknown, evidence is stale, repository refs diverge, credentials are missing, scope is ambiguous, or a proposed action would require unapproved authority.
