---
name: concept-briefing
description: Use as the first step on any new request, before design begins — locks a user-confirmed system profile (scale today and expected, users, trade-off priorities) and tiers the request to route it to the right amount of process, so mechanical work skips spec/plan entirely and layered work gets a phased roadmap instead of one giant plan.
---

# Concept Briefing

Two things before design starts, in this order:

- **Step 0 — System profile.** What kind of system is this? Scale, users, what
  wins when priorities collide. Persisted per project, **confirmed by the user**,
  reused by every later request. Architecture choices depend on it.
- **Step 1 — Tier and route.** How big is this request, and therefore **which
  steps of the arc actually run**? A measurement that changes nothing downstream
  is just ceremony.

## Step 0 — System Profile

File: `docs/system-profile.md` (no date in the name — it outlives any
one request). Template: [references/system-profile-template.md](references/system-profile-template.md).

**Exists and confirmed** → read it. Check for *observed contradictions*, not an
age threshold: the repo says otherwise (profile says "one instance is enough" but
a HPA just appeared), or this very request implies otherwise ("handle 10k
concurrent users" against a profile of 200 internal users). Contradiction → ask
one line about that line only. No contradiction → use it, ask nothing.

**Exists but unconfirmed** → finish the confirmation round; do not move on.

**Missing** → draft it from the repo: `README`, `CLAUDE.md`, compose/k8s
manifests, config files, migrations, CI config, package manifest, service count.
Mark every inferred line `~` — **except lines about the future, which are never
inferred at all** (see below). Then ask the user **in one batched message**: the
five mandatory lines below, plus any low-confidence draft lines. Write the file
as `ĐÃ CHỐT`, commit.

### The gate

Applies **from tier T2 up**. The profile exists to steer *choices between
approaches* — T0/T1 have no such choice to steer, so demanding one there is
exactly the rigidity this skill exists to remove.

| Tier | Profile |
|------|---------|
| T0 | exempt |
| T1 | suggest, never block |
| T2, T3 | **hard gate** — do not proceed with an unconfirmed profile |

At T2+, `concept-briefing` does not finish and **design does not start choosing
approaches** while the profile is `CHƯA CHỐT`. (On Claude Code the design step is
`superpowers:brainstorming`; elsewhere it's whatever you design with.)

**Five lines the user must answer directly** — never fill these in and call it
done: real user count today, **expected scale plus the horizon it applies to**,
scaling need, trade-off priority order, and what must never be traded away.
Everything else you draft and they confirm in a batch.

**The repo contains no future.** Every line about what the system will become —
growth, expected load, planned users — must be answered by the user. It may never
carry `~`, because a `~` there is not an inference from evidence, it is a guess
that freezes into "fact" and then propagates into every downstream prompt. That
is precisely what the `~`/`✓` markers exist to prevent. If the user cannot say
yet, the line is `CHƯA CHỐT` — an honest gap that stops an architecture decision
is cheaper than a confident invention that steers one.

Alongside it, the profile records **which horizon the system is being designed
for** — today's numbers or the expected ones. That choice is currently invisible,
so each session picks differently and the answers disagree without anyone
noticing.

How the team works — cadence, role limits, how detailed plans are — is not
profile material. It lives in the working agreement (`project-working-agreement`);
don't ask it here.

**Silence is not consent.** There is no "the user didn't object, so it's
confirmed" path. If they can't decide a line, mark that line `CHƯA CHỐT`, don't
stamp the whole file, and refuse to base architecture decisions on it — come back
and ask when the work reaches it.

## Step 1 — Tier and Route

Tier by **how many decisions must be made**, deliberately *not* by lines of code.
Changing 300 lines that repeat one pattern is still T1; changing 10 lines that
alter how a settled figure is computed is T3.

| Tier | Signal |
|------|--------|
| **T0 — mechanical** | No choice of approach at all: typo, constant, rename, version bump, comment |
| **T1 — small, obvious** | Exactly one obvious way; 1–3 files; no system boundary, no schema/data |
| **T2 — medium** | Two or more approaches worth weighing, or touches schema/API, or adds a component |
| **T3 — large / business-critical** | Touches money or settled figures, breaks a system boundary, or spans subsystems |

### What each tier runs

| Tier | profile | spec | plan file | executor | checkpoint-verification | convention-commit-gate | adversarial-review-to-go |
|---|---|---|---|---|---|---|---|
| T0 | exempt | no | no | no — do it yourself | no | **yes** | no |
| T1 | suggest | no | no — a few checklist lines in chat | yes | **yes** | **yes** | no |
| T2 | **gate** | short | yes | yes | **yes** | **yes** | only if it touches a risky area |
| T3 | **gate** | yes | yes | yes | **yes** | **yes** | **yes** |

`checkpoint-verification` and `convention-commit-gate` are never dropped when
real code gets written. Skipping paperwork is one thing; skipping verification is
another. T0 skips `checkpoint-verification` only because you wrote it yourself —
there is no handoff to verify.

### Confirm before skipping steps

**Never silently skip.** When the measurement lands on T0 or T1, stop and ask
**once, batching everything into one message**:

> "Tôi xếp việc này T1 (chỉ đổi format ngày ở 2 file, không có phương án nào
> khác) → đề xuất bỏ spec và file plan, làm thẳng qua executor rồi checkpoint.
> Project chưa có system-profile — T1 không bắt buộc, lập luôn hay để sau?"

Batch the tier question with the profile question so small work never costs
several round-trips — that is the failure being fixed. At T2/T3 (nothing
skipped), don't ask: the safe default costs the user nothing.

The user always beats the measurement. They can raise a tier; take it.

### Artifacts by tier

- **T0:** no file. State the tier in chat and move on.
- **T1:** no `concept-brief.md`. Tier and checklist live in the conversation.
  Writing a brief file for T1 work is precisely the ceremony being removed.
- **T2/T3:** write `docs/plans/YYYY-MM-DD-<topic>-concept-brief.md` —
  tier, business-criticality, the requester's expectation, which steps will run,
  and the depth implication for each. It references the profile; it never copies
  it. Pick the `<topic>` slug yourself and reuse it for the spec/plan filenames.

### Changing tier mid-flight

- **Up:** working at T1 and a real choice of approach appears, or schema/boundary
  gets touched → **stop now**, raise the tier, run what the new tier requires —
  including creating the profile if T2 is reached without one. "We're nearly done
  anyway" is not a reason to continue.
- **Down:** only with concrete evidence (the code shows the second approach isn't
  viable). Never to go faster.
- Either way, tell the user the reason in one line.

## Roadmap — Layered Planning for Large Work

**Trigger:** the work has **multiple dependent layers** — something must exist
before the next thing can be built, and the whole doesn't fit one plan. Signals:
a foundation to lay before any feature works; a dependency tree answering "what
unlocks what"; a usable milestone before the end; work clustering by area.

A roadmap is **a route from foundation to finished result**, each phase standing
on the one before — like building from the ground up, or learning step by step.
Not a flat list of tasks.

File: `docs/plans/YYYY-MM-DD-<topic>-roadmap.md`. Template and worked
example: [references/roadmap-template.md](references/roadmap-template.md).

**A phase is a meaningful layer**, satisfying all three:

1. **Stands on what's done and unlocks what's next.** It can state what it needs
   first and what it makes possible.
2. **Groups related work in one place.** Same module, same data model, or the
   same repeated shape (five endpoints of one kind) belong together — done in one
   stretch it's far faster than scattered, because the context is already loaded.
   Conversely, split work touching genuinely unrelated areas, however small each.
3. **Has an observable definition of done.** "Pod runs on dev, `/health` returns
   200, CI green" qualifies; "service skeleton finished" does not.

**Size is not a criterion.** A phase may span many sessions and many executor
rounds. Don't shred a meaningful layer because it's big — break it down *inside
that phase's detailed plan*, leaving the roadmap's layer structure intact.

**Order by foundation:** what must exist first, read straight off the dependency
tree. Among phases that are all unblocked, prefer the one removing the most
uncertainty, then the one that pulls the usable milestone earlier.

**Never analyze ahead.** No API design, no approach selection, no task breakdown
for phases whose turn hasn't come — understanding changes after each phase, so
early analysis is analysis that gets thrown away while still looking current. The
roadmap answers only: how many phases, what each achieves, what unlocks what.

**New phases appear mid-flight.** Insert at the right place in the dependency
tree rather than stuffing it into the running phase; record the date and why.

The roadmap holds **no progress state**. Where we are, what's half-done, what's
next belongs in the pointer — see `pointer-handoff`. Mixing them means the
roadmap gets rewritten for progress reasons and stable direction blurs into
per-session churn.

### The loop

```
step 0: profile → step 1: tier + detect layers
  → brainstorming at boundary level (split layers, order by foundation; no depth)
  → roadmap.md → CONFIRM WITH USER
  → per phase, in dependency order:
       re-tier that phase (may be just T1 → skip spec/plan)
       → detailed spec/plan written ONLY NOW, never in advance
       → executor → checkpoint-verification → convention-commit-gate
       → if a lesson changes direction, update the roadmap
  → adversarial-review-to-go (after each risky phase, or once at the end)
  → finish/merge the branch
```

Every phase is re-tiered independently. A large roadmap can be mostly T1 phases —
and those take the T1 shortcut; nobody writes a spec for each.

### When the system has several large areas

While profiling, note the services or large independent areas the repo shows. If
**two or more pass the lane test** in `multi-lane-coordination`, and the working
agreement has no coordination-mode line, ask the coordination-mode question from
`project-working-agreement` in the same batched message as the profile questions.
Fewer than two → ask nothing; the project stays single.

## Keeping It Current

- Reality diverges from the profile (turns out there are 50k users, not 200) →
  fix the file and the date without waiting to be asked.
- When a line changes, **proactively re-examine** architecture decisions that
  rested on the old value and report back. A profile that shifts mid-project can
  invalidate a chosen approach.
- User-edited lines keep `✓`; lines you revise from new observation drop back to
  `~` until confirmed.

## Handoff to the Rest of the Arc

- **The design step** reads both: the profile decides *which approach* (how thin
  is allowed), the tier decides *how deep to probe*. On Claude Code that step is
  `superpowers:brainstorming`.
- `orchestrating-executors` quotes from the profile in every handoff prompt: the
  trade-off priority order, the boundaries that must not break, the expected test
  level. This is where the profile pays off most — an external executor is blind
  to all of it.
- `adversarial-review-to-go` gets the profile so the reviewer can tell real risk
  from noise, and knows which boundaries are hard.
- `pointer-handoff` owns session-to-session continuity — what's half-done, what's
  next. Nothing this skill writes holds progress state.

## Red Flags

| Thought | Reality |
|---------|---------|
| "Obviously small, I'll start brainstorming" | Say the tier in one line first. An unstated assumption is what drifts. |
| "I'll infer the user count and scaling need myself" | Those are two of the four lines only the user can answer. Drafting them is fine; calling them settled is not. |
| "They didn't object, so the profile is confirmed" | Silence is not consent. Unconfirmed means unconfirmed. |
| "T1, but I'll skip spec/plan without asking" | Skipping steps is the user's call. Ask once, batched. |
| "Nearly done — I'll finish before raising the tier" | Stop now. That's how a schema change ships without a spec. |
| "This phase is huge, I'll cut it into three" | Size isn't a criterion. Break it down inside the phase's plan; keep the layer intact. |
| "Let me sketch phase 3's API while I'm here" | Never analyze ahead. Phase 1 will change what phase 3 needs. |
| "I'll track progress in the roadmap" | Progress belongs to the pointer skill. The roadmap holds direction. |
| "The profile's wrong but the plan's already approved" | Update the profile, then re-examine the decisions built on the old line. |
