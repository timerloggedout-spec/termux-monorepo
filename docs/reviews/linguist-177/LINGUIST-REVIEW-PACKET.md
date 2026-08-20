# Linguist Review Packet — PR #177 and Related Work

**Review date:** 2026-08-20 UTC

**Repository evidence revision:** `933d65d0e2c49e28079f300f5a516932330c60e7`

**Implementation branch:** `feature/cedrlang-grimoire-a2a` from `master-staging` at `d33842a`

**Review status:** **Conditional / not merge-ready**

## Executive Assessment

The Linguist workstream contains a useful performance-oriented public document translator, but its present implementation does not substantiate the requested internal-mapper, measured-70%, clean-transmission, or Agent2Agent protocol claims. The current regex codec, tracked CEDARscript pointer index, and public Grimoire diction sources represent separate concerns that have drifted into one role. The two open focal pull requests are both broad, dirty stacks and are unsuitable targets for incremental repair. The evidence-supported disposition is to preserve only isolated value in a clean, governed successor branch rather than amend or force-merge those stacks. [1] [2]

A bounded implementation has been added on the successor branch. It introduces a deterministic, non-executing CIR codec, bijective synthetic mapper contract, integrity digest, measurable eligible-token coverage report, and local A2A envelope validator. It deliberately excludes private mapper contents, CEDARscript/CID execution, public transformed postings, workflow changes, external installation, and any migration of root agent contact files. The work remains **conditional** because the repository gate and full proposal-registry validator have inherited baseline blockers, and proposal acceptance/non-author review remain pending.

| Disposition | Rationale |
|---|---|
| **Do not amend or merge PR #177** | Public metadata reports an open, dirty, non-rebaseable stack with 161 changed files and substantial unrelated scope. [1] |
| **Do not amend or merge PR #154** | Public metadata reports an open 165-file stack; its inspected owner guidance is recorded only by permalink and directs a small reconstructed hygiene-passed change rather than re-landing the stack. [2] |
| **Keep #196, #208, #218, and #228 as historical optimization evidence** | Each is merged and narrowly touches the public translator/tests; shared-file history is a candidate link, not proof that its design decisions solve the mapper or A2A requirements. [1] |
| **Implement a clean successor foundation** | The new proposal and `LGA-01` contract isolate deterministic codec/A2A behavior from CEDARscript pointers and expose explicit tests/evidence. [3] [4] |

## Title-Complete Linguist Inventory

The authenticated GitHub CLI could not be used because its configured credential returned an authentication error. Collection therefore used the public GitHub read API for title discovery and pull-request metadata, plus the repository’s current local graph index. The title search returned **seven pull requests and no issues** whose title contains `Linguist`; it is the all-state collection bound for this packet. [1]

| PR | State at collection | Changed files | Relationship classification | Review disposition |
|---:|---|---:|---|---|
| [#126](https://github.com/timerloggedout-spec/termux-monorepo/pull/126) | Closed, not merged | 9 | **Verified** predecessor; graph records a `MENTIONS` edge to issue #117. | Treat as the earliest A2A/compression design reference only. |
| [#154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154) | Open | 165 | **Verified** predecessor through exact owner reference, common reviewed files, and graph evidence. | Do not revive the dirty stack; reconstruct unique safe value only. |
| [#177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177) | Open, dirty | 161 | **Verified** review root. | Do not amend; use this packet and successor foundation instead. |
| [#196](https://github.com/timerloggedout-spec/termux-monorepo/pull/196) | Merged | 5 | **Candidate** relation through shared translator/history. | Retain its narrow compilation improvements as optional regression context. |
| [#208](https://github.com/timerloggedout-spec/termux-monorepo/pull/208) | Merged | 3 | **Candidate** relation through shared translator/history. | Retain as optimization history, not a protocol design source. |
| [#218](https://github.com/timerloggedout-spec/termux-monorepo/pull/218) | Merged | 2 | **Candidate** relation through shared translator/history. | Retain as optimization history, not a protocol design source. |
| [#228](https://github.com/timerloggedout-spec/termux-monorepo/pull/228) | Merged | 2 | **Candidate** relation through shared translator/history. | Retain as optimization history, not a protocol design source. |

## Context Relationship Graph

The generated graph used the exact root `pr:177`, depth `2`, and a 25-node limit. It contains verified commit, review, review-comment, issue-comment, and source-file relationships. The canonical index is current to 2026-08-19 but has a retained **partial** GitHub history window with `next_start_page: 2`; this packet therefore does not claim complete historical graph coverage. [5] [6]

![Curated Linguist relationship summary](linguist-relationship-summary.png)

The Mermaid source for both the generated raw graph and the concise evidence summary is committed under this directory. The PNG render artifacts remain intentionally ignored by the repository and are supplied as task attachments. The raw graph, rendering validation, evidence bounds, and candidate separation are documented in `context-pr177.md`, `context-pr177.mmd`, `linguist-relationship-summary.mmd`, and `diagram-validation.md`.

| Verified relationship | Evidence |
|---|---|
| PR #126 `MENTIONS` issue #117, *Agent2Agent Comms Proposal*. | Generated exact-root query [`context-pr126.md`](context-pr126.md); [#126](https://github.com/timerloggedout-spec/termux-monorepo/pull/126); [#117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117). |
| PR #154 and PR #177 have verified review/file relationships to `workspace/compression_sandbox/cedrlang/cedrlang.py` and agent instruction surfaces. | Generated exact-root queries [`context-pr154.md`](context-pr154.md) and [`context-pr177.md`](context-pr177.md). |
| Exact owner comment on #177 references #126 and #154. | [Exact permalink](https://github.com/timerloggedout-spec/termux-monorepo/pull/177#issuecomment-5273315069). The comment body is intentionally not copied into this packet. |
| Historical CEDARscript is an execution-capable code-transformation system, distinct from document encoding. | [CEDARScript organization](https://github.com/CEDARScript); [CEDARScript Editor](https://github.com/CEDARScript/cedarscript-editor-python). |

## Design Findings

| ID | Severity | Finding | Evidence-backed conclusion |
|---|---|---|---|
| L-01 | **Blocking** | The public codec does not implement an authorized private mapper. | `cedrlang.py` uses in-repository regex/dictionary substitutions; tracked `.cedar` and Grimoire files are not an access-controlled mapper. The implementation must not claim private lossless reconstruction until an approved external custody interface exists. [7] |
| L-02 | **Blocking** | Literal one-way/lossy representation conflicts with perfect reconstruction. | Perfect reconstruction requires a defined canonical form, versioned bijection, authorized mapper, and integrity check. The clean foundation encodes this distinction instead of treating obfuscation as a security primitive. [3] |
| L-03 | **Blocking** | `cid.py` scope is CEDARscript command-pointer registration, not generic CEDRlang decoding. | It writes home-directory command pointers and enumerates code-editing operations; local patch routing can execute CEDARscript, `sed`, or generated Python. CEDRlang must not call this surface. [7] [8] |
| L-04 | **Required** | Existing tests prove selected formatting round trips but not mapper collision safety, 70% measurement, canonical digest, version handling, or A2A behavior. | New tests cover each omitted control while retaining the historical 11-test translation suite. [9] |
| L-05 | **Required** | No local A2A contract existed. | Issue #117 is a verified related proposal, but its historical workflow example includes remote installation/external service behavior. The successor implements local-only envelope validation without that side effect. [10] |
| L-06 | **Required** | Instruction surfaces lack a reproducible canonical/projection policy. | `AGENTS.md`, `AGENTS.hum.md`, and `CLAUDE.md` must remain readable until a later approved migration defines source ownership and drift checks. Existing root/ICM branch guidance also needs separate governance reconciliation. [11] |

## Successor Implementation

The new work is registered as proposal `cedrlang-grimoire-a2a` and its first work item, `LGA-01`. The proposal remains **draft** pending required non-author review and formal acceptance; the feature branch is a Tier-0 implementation/research artifact, not a merge request or an institutional acceptance claim.

| Delivered component | What it does | What it deliberately does not do |
|---|---|---|
| `protocol.py` | Canonical record normalization, deterministic serialization, SHA-256 digest, mapper collision validation, segment-safe encode/decode, coverage report, strict serialized A2A object parsing, and A2A TTL/state/replay validation. | No filesystem writes, subprocesses, network, external service, CID, CEDARscript, or patch routing. |
| `test_cedrlang_protocol.py` | Seven focused tests for deterministic round trips, collisions, literal handles, coverage enforcement, tamper failure, strict serialized-envelope rejection, and A2A TTL/state/replay behavior. | No real/private mapper test data. |
| `CEDRLANG-GRIMOIRE-A2A.md` | Public specification of canonical source, mapper boundary, 70% coverage definition, local A2A schema, and CEDARscript separation. | No private mapper custody instructions or operational automation. |
| Proposal and review evidence | Item ledger, decision record, source inventory, graph outputs, external-boundary record, and review packet. | No PR comment, approval, merge, external workflow, secret, or repository configuration write. |

## Validation Evidence

| Validation | Result | Notes |
|---|---|---|
| `python3 -m pytest tests/test_cedrlang.py tests/test_cedrlang_protocol.py -q` | **Pass: 18 tests** | 11 historical translator tests plus 7 new foundation tests passed. |
| `python3 -m compileall -q workspace/compression_sandbox/cedrlang/protocol.py tests/test_cedrlang_protocol.py` | **Pass** | New implementation and tests compile. |
| `ruff check --select F,E9 …` | **Pass** | Compatibility-focused linting is clean. The repository’s global Ruff defaults suggest modern typing rewrites that are not adopted because the documented Python floor is 3.9. |
| Dependency boundary scan | **Pass** | No execution, network, CID, or CEDARscript import/invocation pattern exists in `protocol.py`. |
| Scoped credential-signature scan | **Pass** | No credential signatures or private mapper contents were found in new implementation/docs/evidence files. |
| `git diff --cached --check` | **Pass** | No staged whitespace error remains. |
| `python3 scripts/ci/termux_smoke.py` | **Pass** | Smoke gate passed on Linux with Python 3.12.3; Termux-specific checks were reported as non-blocking environment notes. |
| `python3 scripts/ci/repo_gate.py` | **Blocked by inherited failure** | Fails on pre-existing `archwiz/linear_sync.py:237` syntax, outside the scoped diff. The gate compares to `origin/master`, so it also sees inherited `master-staging` divergence. |
| `python3 scripts/proposals/validate_registry.py` | **Blocked by inherited failure** | Full YAML validation reports existing orphan active directories: `actions-refinements`, `icm-architect-integration`, and `kimi-cloud-offload`; none are part of the staged change. |

## Unposted Draft Review for PR #177

> **Status: 🔴 NO-GO for the current stack.** The PR is dirty and contains a broad 161-file scope that mixes the Linguist codec with unrelated workflows, dependencies, ICM, and runtime material. The current public regex mapping, tracked pointer index, and Grimoire dictionaries do not constitute a private authorized mapper, and the diff does not establish the requested 70% metric, canonical digest, mapper version/collision policy, or A2A envelope contract. Do not force-merge or rebase this stack to regain mergeability. Preserve only isolated, tested translator improvements through the successor proposal `cedrlang-grimoire-a2a` (`LGA-01`), which adds a deterministic non-executing codec and local A2A validator while keeping CEDARscript/CID execution separate. Repository integration remains conditional on a non-author proposal review, accepted status, and resolution or explicit baseline disposition for the current gate/registry blockers. [2] [3] [7]

This full text remains the review packet's canonical draft. A concise, evidence-linked disposition summary was posted to [PR #177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177#issuecomment-5361408055), [PR #154](https://github.com/timerloggedout-spec/termux-monorepo/pull/154#issuecomment-5361406746), [issue #117](https://github.com/timerloggedout-spec/termux-monorepo/issues/117#issuecomment-5361410703), and [issue #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175#issuecomment-5361403327). The complete evidence bundle and subtasks are published in [issue #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274). None of those cross-references is an approval, formal review verdict, merge, or private-mapper authorization.

## Required Next Decisions

The next safe step is a non-author review of proposal `cedrlang-grimoire-a2a`, recorded through [issue #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274) and `RESEARCH.md`. If accepted, it can be advanced through the ordinary feature-branch gate process. A later separate proposal must choose an approved private-mapper custody service, define access/rotation/audit behavior, and decide whether any canonical agent document should generate a machine projection. No migration of `AGENTS.md`, `CLAUDE.md`, ICM files, README, CID, CEDARscript, or workflows should proceed from this review alone. Agents repeating or improving this evidence process should follow the linked [context-relationship graph reuse case study](context-relationship-graph-reuse.md).

## References

1. [GitHub title search and public PR metadata for `Linguist`](https://api.github.com/search/issues?q=repo%3Atimerloggedout-spec%2Ftermux-monorepo%20in%3Atitle%20Linguist&per_page=100)
2. [PR #177](https://github.com/timerloggedout-spec/termux-monorepo/pull/177)
3. [CEDRlang / Grimoire / A2A decision record](../../proposals/active/cedrlang-grimoire-a2a/source.md)
4. [CEDRlang / Grimoire / A2A public contract](../../CEDRLANG-GRIMOIRE-A2A.md)
5. [PR #177 exact context graph query](context-pr177.md)
6. [Context relationship index manifest](../../../workspace/llm_map/context_relationships/manifest.json)
7. [Agent-contact inventory and drift assessment](agent-contact-inventory.md)
8. [External CEDARScript boundary](external-cedarscript-boundary.md)
9. [Existing CedrLang tests](../../../tests/test_cedrlang.py) and [new protocol tests](../../../tests/test_cedrlang_protocol.py)
10. [Issue #117 — Agent2Agent Comms Proposal](https://github.com/timerloggedout-spec/termux-monorepo/issues/117)
11. [Root AGENTS.md](../../../AGENTS.md), [root CLAUDE.md](../../../CLAUDE.md), and [ICM change process](../../icm/processes/change-and-validate.md)
12. [Context-relationship graph reuse case study](context-relationship-graph-reuse.md)
13. [Linguist publication and subtask tracker, issue #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274)
