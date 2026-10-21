# Agent Team Development Lanes

> Operational synthesis for the agentic development environment. This document complements `review-loop`, `adaptive-feedback-cycle`, `evidence-led-monorepo-ops`, `context-relationship-graph`, and `gemini-performance-psychology`.

## Objective

Turn a growing provider/model/agent population into a measurable development team without allowing concurrency to become collision, duplication, or unverified activity.

## Lanes

| Lane | Primary function | Typical evidence |
|---|---|---|
| Builder | focused implementation | commit, tests, diff |
| Review | correctness/security/regression critique | review, findings, disposition |
| Recon | history/context/provider/skill discovery | sources, relationships, candidates |
| Experiment | controlled MVT treatment | cohort/run/attempt/result |
| Telemetry | workflow/provider evidence correlation | SHA↔run↔job↔step↔artifact |
| Synthesis | promote reusable knowledge | skill/SSOT/spec revision |

Lanes should prefer disjoint files and explicit ownership claims when overlap is unavoidable.

## BIUDL

Use the broad-to-narrow-to-broad development cycle:

```text
Broad objective
      ↓
Identify useful development lane
      ↓
Isolate thin slice
      ↓
Implement
      ↓
Validate repeatedly
      ↓
Integrate learning
      ↓
Broaden / synthesize
      ↓
Next cycle
```

A large PR can remain a reference/integration surface while narrow slices establish stronger evidence. Useful prior commits, comments, reviews, templates, proposals, and branches should be cherry-picked conceptually or technically when provenance permits.

## Provider/model admission

Scout discovers candidates; the manager selects treatments. A candidate progresses through:

```text
DISCOVERED → CATALOG_VERIFIED → CREDENTIAL_AVAILABLE
→ REQUEST_PROBE → TASK_PROBE → REPEATED_SUCCESS
→ TEAM_ELIGIBLE → MONEYBALL_SCORED → ACTIVE
```

Failure produces an evidence-bearing state such as `COOLDOWN`, `UNAVAILABLE`, `BLOCKED`, or `REGRESSION`; it does not erase the candidate.

For the current development population, prioritize proving operational lanes for OX Alpha and DeepSeek, then expand the roster from live provider catalogs and other available libraries. `$0`/free is a resource classification, not a quality score or hardcoded identity.

## MVT treatment identity

The minimum treatment matrix is:

`provider × model × prompt × manager × cohort × sequencing`

Extend only when a new factor is experimentally justified, such as task, scope, context strategy, command stack, or validation class.

## Performance psychology

Maintain momentum through short evidence-bearing cycles, progressive challenge, immediate state feedback, and visible next actions. Do not reward activity itself. Green workflows, HTTP 200, low latency, high token count, or many commits are not substitutes for verified task outcome.

Correctness remains higher priority than latency unless latency is the explicit experimental factor.

## Bilateral critique

For consequential changes, obtain two perspectives where possible:

1. implementation-side critique — what is incorrect, incomplete, unsafe, or regressive?
2. adversarial/alternative critique — what assumptions, counterexamples, provider behavior, or external prior art may have been missed?

Disagreement becomes a hypothesis. Evidence and experiments resolve it.

## Evidence contract

Every material run should be joinable where available:

`cycle → experiment → cohort → run → attempt → request → provider/model → SHA → workflow → job → step → log/artifact → outcome`

Preserve unsuccessful attempts. Do not rewrite history to make the winning path appear inevitable.

## Loop termination

The team continues:

1. current GitHub state
2. recent agent changes
3. historical SSOT/decision/cooldown evidence
4. current provider/skill knowledge
5. SHA↔run correlation
6. smallest evidence-backed change
7. commit
8. adaptive wait
9. jobs → steps → logs → artifacts
10. proven vs unproven classification
11. update skills/SSOTs
12. **repeat until desired outcome confirmed**

A missing run, stale catalog, quota cooldown, or provider outage is an evidence state to route around—not permission to declare success.

## Security boundary

Credentials, cookies, browser profiles, session stores, and tokens never enter prompts, artifacts, logs, skills, or committed reports. Agent/provider output is untrusted data and must not silently become executable instructions.
