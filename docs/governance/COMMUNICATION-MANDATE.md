# Repo-Wide Communication Mandate and Siglary Registry

**Status:** proposed governance contract  
**Snapshot:** 2026-11-18  
**Scope:** persisted repository communication and assistant/operator handoffs

## Purpose

Make every repository interaction easy to parse, review, route, validate, and audit. Communication carries either a state change or an oversight checkpoint. Every directive uses a positive DO statement and a fixed positional frame.

## Core contract

`⌖scope → ▶action → ⊗constraint → ⤵output → ~state`

| Slot | Meaning | Required content |
|---|---|---|
| `⌖scope` | Scope key | Issue, PR, branch, subsystem, file, or task |
| `▶action` | Action | Positive imperative describing the requested change |
| `⊗constraint` | Constraint | Evidence, policy, compatibility, security, or quality bound |
| `⤵output` | Output | Artifact, commit, test, report, or decision expected |
| `~state` | State | proposed, active, blocked, passed, failed, or closed |

A message carries a state change or an oversight checkpoint. Each statement carries one fact or one action. Updates carry changed facts only. Every message declares a scope key; out-of-scope material enters a triage log.

## Communication modes

| Mode | Purpose | Required shape |
|---|---|---|
| `STATE-CHANGE` | Change code, docs, configuration, issue/PR state, or a decision | Scope frame + action + output + resulting state |
| `OVERSIGHT` | Verify work, inspect evidence, assess risk, or report progress | Scope frame + evidence + status + next checkpoint |
| `BLOCKED` | Record a dependency that prevents progress | Scope frame + blocking dependency + owner/action + resume condition |

The conversation carries decisions and oversight. Execution routes to the repository workflow, QUE, or the designated machinery. Chat reports the resulting evidence and state.

## Positive-form language

- Directives use `DO` statements.
- The controlled avoidance set is `⊘ = {No, Not, Don't, Never}`.
- Rephrase directive language into positive actions, explicit outcomes, and observable conditions.
- Keep quoted source text, code, legal language, historical evidence, and the avoidance-set registry verbatim when fidelity requires it.
- The linter targets authored directive prose; source quotations and code examples remain evidence.

## Force tiers

Project-local force tiers:

| Token | Force | Interpretation |
|---|---|---|
| `DO` | Requirement | Required project action |
| `DEFAULT` | Overridable preference | Apply unless an explicit reason and owner-approved exception are recorded |
| Unmarked statement | Observation | Descriptive information without directive force |

For standards-style normative requirements, use the IETF BCP 14 vocabulary only with its defined uppercase semantics. RFC 8174 clarifies that the special meanings apply when the keywords appear in uppercase. The project-local `DO` and `DEFAULT` tiers remain separate from BCP 14.

## Operator families

Each glyph has one project-defined role in the Siglary. Role labels accompany glyphs in registry tables, diagrams, and machine-readable records. The project convention assigns zero implicit precedence across families; expressions with multiple operators use explicit grouping or named fields.

| Family | Glyph | Project meaning |
|---|---|---|
| Logic | `∧` | conjunction |
| Logic | `∨` | disjunction |
| Logic | `¬` | logical negation |
| Logic | `⇒` | implication |
| Logic | `⇔` | equivalence |
| Logic | `∈` | membership |
| Logic | `∉` | non-membership |
| Logic | `∀` | universal quantification |
| Logic | `∃` | existential quantification |
| Logic | `∅` | empty set |
| Logic | `≠` | inequality |
| Logic | `≡` | definitional/structural identity |
| Logic | `≈` | approximate equivalence |
| Logic | `≤` | less-than-or-equal |
| Logic | `≥` | greater-than-or-equal |
| Logic | `∝` | proportionality |
| Evidence | `⊢` | proven / derivable in the declared system |
| Evidence | `⊬` | unproven in the declared system |
| Evidence | `⊩` | assertion accompanied by traceable evidence |
| Evidence | `≟` | disputed / unresolved claim |
| Evidence | `∎` | review or proof closure |
| Flow | `⤴` | route / offload |
| Flow | `↳` | child / subordinate item |
| Flow | `⤵` | land / deliver output |
| Flow | `↻` | cadence cycle |
| Flow | `⊕` | combine |
| Flow | `⊗` | constrained combine |
| Flow | `⋈` | join |
| State | `⏸` | hold |
| State | `▶` | execute |
| State | `✓` | pass |
| State | `✗` | fail |
| State | `⧖` | pending |
| State | `⚡` | immediate |
| State | `Δ` | change |
| State | `§` | rule reference |
| Scope | `⌖` | scope key |

### Collision and precedence discipline

The glyphs retain their established meanings in mathematical, programming-language, and domain-specific contexts. The Siglary meaning applies only inside explicitly marked project-governance contexts. The same glyph may have different meanings in another domain; each record carries a namespace and domain. The BQN language is a design reference for deliberate operator roles and compact expression design, while its own grammar and precedence rules remain BQN-specific. This project adopts explicit grouping and role labels as its own convention.

## Numbered rule registry

| Rule ID | Mandate | Enforcement surface |
|---|---|---|
| SG001 | Chat carries `STATE-CHANGE` or `OVERSIGHT` | Templates, review checklist |
| SG002 | Directives use positive `DO` statements; authored directive prose follows `⊘` vocabulary policy | Custom prose linter |
| SG003 | Use necessary facts, one statement per fact, and delta-only updates | Templates, review checklist |
| SG004 | Every message carries a scope key; out-of-scope material enters triage | Templates, issue/PR forms |
| SG005 | Route execution to QUE/machinery; chat reports execution evidence and state | Workflow documentation |
| SG006 | Catalogue every route; single-arm routes carry an explicit exception stamp | Route registry validation |
| SG007 | Claims carry inline evidence `⊩` or disputed status `≟` | Review checklist and evidence validator |
| SG008 | Enforce the mandate through lint, tests, and workflow checks | GitHub Actions |

## Reader-side performance budget

- Present at most four primary information chunks per message; split larger work into linked batches.
- Use categorical checkpoints: `STATE-CHANGE`, `OVERSIGHT`, and `BLOCKED`.
- Batch oversight at meaningful checkpoints.
- Limit concurrent work in progress and deliver small reviewable batches.
- Use compact, role-visible Siglary notation with plain-language expansion at first use.

The four-chunk ceiling is a project readability heuristic inspired by the cognitive-load repository. Its author explicitly describes the four-chunk figure as an informal simplification. Treat it as a design budget, not a universal cognitive-science law.

## Lint and enforcement surface

| Surface | Mechanism | Status |
|---|---|---|
| Markdown documents | Vale + markdownlint | CI configured by this proposal |
| Mandate-specific directive language | SG002 custom validator | CI configured by this proposal |
| Commit subjects | Conventional scope + imperative-positive review | Initial policy; automated commit validation is follow-on |
| Issue/PR templates | Fixed statement frame and scope field | Follow-on integration |
| PR/issue comments | Review checklist and comment-event workflow | Follow-on integration |
| Chat handoffs | Assistant/operator process using this contract | Process-level; repository CI cannot lint private chat transcripts |

A repo-wide claim applies only to surfaces with an installed enforcement path. The table records the current coverage and the remaining integration work explicitly.

## Oversight and stream complexity

Oversight uses batched checkpoints rather than continuous status drip. A checkpoint summarizes all completed work, current blockers, evidence, and the next action in one pass. The `O(1)` stream objective is a project engineering target for constant-size checkpoint summaries and bounded status metadata; it is not a claim that arbitrary event history can be processed in constant time.

The identifier `racc` is recorded as an unverified research lead. Its intended repository, package, and exact streaming semantics require a canonical source URL before implementation or performance claims.

## Evidence and provenance

- [BQN repository](https://github.com/mlochbaum/BQN) and [syntax overview](https://mlochbaum.github.io/BQN/doc/syntax.html): operator/function/modifier roles, explicit grammar, and language-specific precedence. Design precedent only.
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174): normative force words and uppercase interpretation.
- [Vale documentation](https://docs.vale.sh/): customizable prose linting and style consistency.
- [markdownlint](https://github.com/DavidAnson/markdownlint): Markdown style and structural lint rules.
- [Cognitive Load](https://github.com/zakirullin/cognitive-load): informal developer-facing four-chunk working-memory heuristic; repository text qualifies its scientific scope.
- [DORA](https://dora.dev/capabilities/): software delivery capabilities and continuous improvement. Small-batch/WIP practices are project operational choices informed by delivery research; this document does not attribute the exact four-chunk or O(1) claims to DORA.
- [Notation Sets #320](https://github.com/timerloggedout-spec/termux-monorepo/issues/320), [Domain Composition Matrix #1115](https://github.com/timerloggedout-spec/termux-monorepo/issues/1115), and [PR #1309](https://github.com/timerloggedout-spec/termux-monorepo/pull/1309): repository-local lineage and implementation context.

## Change control

Every new glyph, rule, alias, force tier, or exception receives a stable registry ID, owner, definition, scope, source/evidence, status, and validation fixture. Registry updates travel as small reviewable changes with tests and generated index updates.
