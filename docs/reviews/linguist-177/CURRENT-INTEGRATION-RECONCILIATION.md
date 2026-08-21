# Current Linguist / Grimiore / A2A Integration Reconciliation

**As of:** 2026-08-21 UTC

**Decision:** Use [PR #275](https://github.com/timerloggedout-spec/termux-monorepo/pull/275) as the **single reviewable integration candidate**. Do not merge, rebase, or append new implementation to the conflicted Jules stacks [PR #154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154) and [PR #177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177).

> This is a consolidation decision, not a merge authorization. The proposal is moved into formal review so independent reviewers can assess a bounded successor. Private-mapper custody, document-projection migration, and networked A2A transport remain excluded pending separate acceptance.

## Live PR Assessment

| PR | Live state | Scope signal | Integration disposition |
|---|---|---:|---|
| [#154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154) | Open; `DIRTY` and `CONFLICTING` | 165 files; 10,678 additions; 97 commits | Keep as historical/review context only. Its CEDRlang, Grimoire, and agent-contact content is inseparable from unrelated drift. |
| [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177) | Open; `DIRTY` and `CONFLICTING` | 161 files; 10,718 additions; 100 commits | Keep as the principal evidence root. Its live workflow and repository changes are not an integration source. |
| [#275](https://github.com/timerloggedout-spec/termux-monorepo/pull/275) | Open; non-draft; requested review changes pending | Bounded successor scope; current head is under review remediation | **Selected integration candidate.** It contains the deterministic codec, local A2A validation, bounded review evidence, and explicit non-goals; no integration claim is made until requested findings are resolved and review is accepted. |

The successor branch was refreshed onto current `master-staging` commit `21ac9e3`; its pre-review translator/protocol suite passed 18 tests with clean selected lint. PR #275 currently reports a failing external `ci/gitlab/gitlab.com` status and requested CodeRabbit changes. The external status is recorded for visibility rather than classified as repository-owned validation, and it does not waive any local or repository gate. The inherited syntax and registry blockers are now isolated in PRs #288 and #290 respectively; until those focused remediations are independently integrated, they remain baseline dependencies outside the successor diff.

## Bounded Relationship Context

| Root | Evidence class | Current interpretation |
|---|---|---|
| [Issue #182](https://github.com/timerloggedout-spec/termux-monorepo/issues/182) — `Grimiore, CID.py, <our>Lang[CEDR{rename,}]` | Verified title and direct `#177` reference | The explicit Grimiore naming/custody discussion root. Its visible body contains only the `#177` pointer; it does not authorize implementation or expose a mapper. |
| [Issue #117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117) — Agent2Agent Comms Proposal | Verified title and issue metadata | The protocol-design root. PR #275 preserves only local schema validation; no transport, remote mailbox, workflow, or install behavior is adopted. |
| [Issue #181](https://github.com/timerloggedout-spec/termux-monorepo/issues/181) — Compression & Security | Candidate, based on topic; no direct graph edge in the current partial index | Security-review destination for any future mapper custody or authenticated transport proposal, not a reason to extend #275. |
| [Issue #201](https://github.com/timerloggedout-spec/termux-monorepo/issues/201) — AGENTS.md | Candidate, based on the `Linguist` label; no direct graph edge in the current partial index | Tracks the eventual human/machine contact-point migration decision. It remains outside the current implementation. |
| [PR #153](https://github.com/timerloggedout-spec/termux-monorepo/pull/153) — Consolidate upgrades and timing quotas SSOT | Candidate, closed PR; no direct graph edge in the current partial index | A historical SSOT precedent, not a dependency of codec or A2A work. |

The repository-native index was queried at `pr:177`. The current manifest covers only history page 1 and reports `next_start_page: 2`; exact roots for #153, #181, #182, and #201 were absent. The relationships above therefore distinguish direct live GitHub evidence from candidates rather than inferring missing history.

## Integration Boundary

The only work proposed for review is the non-executing foundation in #275. It uses a typed canonical intermediate record, deterministic normalization, synthetic test mapper, integrity digest, measurable eligible-token coverage, strict local A2A-envelope parsing, TTL/state/replay validation, and no CID/CEDARscript or external-service dependency. The current required constraints are documented in [`CEDRLANG-GRIMOIRE-A2A.md`](../../CEDRLANG-GRIMOIRE-A2A.md) and the outstanding human decisions remain in [`RESEARCH.md`](../../proposals/active/cedrlang-grimoire-a2a/RESEARCH.md).

A later proposal, not PR #275, must decide private-mapper custody, canonical human source, generated instruction projections, AGENTS/CLAUDE/ICM/README migration, authenticated transport, and workflow integration. The controlled separation prevents the active Jules work from reintroducing the original document-code-workflow conflation.

## Required Review Path

The selected PR is non-draft and has requested CodeRabbit changes under resolution. Reviewers should assess the narrow implementation, the non-executing boundary, exact phrase/token coverage and lossless casing behavior, envelope isolation and time validation, the current graph bounds, the observed external GitLab status, and the separately scoped baseline remediations. They should not treat a review of #275 as approval for the unresolved custody, migration, or remote-transport decisions.

## References

1. [PR #154 live metadata](https://github.com/timerloggedout-spec/termux-monorepo/pull/154)
2. [PR #177 live metadata](https://github.com/timerloggedout-spec/termux-monorepo/pull/177)
3. [PR #275 selected successor](https://github.com/timerloggedout-spec/termux-monorepo/pull/275)
4. [Issue #182 Grimiore naming root](https://github.com/timerloggedout-spec/termux-monorepo/issues/182)
5. [Issue #117 Agent2Agent Comms Proposal](https://github.com/timerloggedout-spec/termux-monorepo/issues/117)
6. [Context-relationship graph method](../../../.agents/skills/context-relationship-graph/SKILL.md)
