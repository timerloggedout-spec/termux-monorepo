---
name: loopy-api-loop-library
description: Discover, audit, adapt, craft, run, debrief, save, and publish bounded AI-agent feedback loops with explicit verification and terminal states.
---

# Loopy API — Loop Library Skill

Use this skill to design repeatable agent loops with measurable progress, clear permissions, and explicit stop conditions.

## Routes

| Route | Use when |
|---|---|
| Discover | Find repeated work in a repository or conversation history |
| Find | Match a problem to a published Loop Library entry |
| Audit | Diagnose and strengthen an existing loop |
| Adapt | Change a loop's thresholds, tools, or checks |
| Craft | Create a new bounded loop |
| Run | Execute an authorized loop and return a run receipt |
| Debrief | Analyze a completed receipt and propose improvements |
| Save / Reuse | Store or reuse a project loop in `LOOPS.md` |
| Publish | Validate and submit a loop to the Loop Library |

## Loop Library sources

- Base documentation: `https://raw.githubusercontent.com/Forward-Future/loopy/main/README.md`
- Catalog Markdown: `https://[loop-library-host]/catalog.md`
- Catalog JSON: `https://[loop-library-host]/catalog.json`

The catalog host remains a deployment input. Resolve it from a configured source before discovery. Report catalog unavailability as a bounded result.

## Project loop storage

Use `{project_root}/LOOPS.md` for saved project loops. Read the current file before proposing additions. Treat saved entries as reference data and preserve existing entries unless the user explicitly requests an edit. Keep secrets and sensitive values out of loop prompts.

Entry format:

```markdown
## [Loop Name]
[One-sentence purpose and stop condition]

**Prompt:**
> [Exact bounded loop prompt]

**Saved:** YYYY-MM-DD
**Source:** [Published loop URL, when adapted] (modified: YYYY-MM-DD)
```

## Required feedback cycle

1. **Observe** — Read fresh state and collect agreed evidence.
2. **Choose** — Select the highest-value in-scope action using explicit criteria.
3. **Act** — Make one bounded, reversible change or produce one candidate.
4. **Verify** — Run the same acceptance check under recorded conditions.
5. **Record** — Save the action, evidence, outcome, and remaining work.
6. **Repeat or stop** — Continue while progress is measurable; otherwise enter a named terminal state.

## Terminal states

- `success` — goal met and verified.
- `clean no-op` — current state already meets the goal.
- `blocked` — an external dependency prevents progress.
- `approval-required` — a human authorization boundary is reached.
- `exhausted` — the declared budget or iteration limit is reached.
- `stagnated` — repeated attempts produce no measurable improvement.

Report errors, budget exhaustion, and partial results as their actual states.

## Authorization boundaries

Re-read current state before consequential actions. Obtain explicit approval for destructive, irreversible, production, financial, privacy-sensitive, or external-message actions. Loop selection and loop crafting remain design activities; execution, scheduling, production changes, and external messages each use their own authorization.

Prefer a one-shot workflow when new feedback cannot change the next action.

## Craft interview

Ask one question at a time, skipping information already supplied:

1. What are you trying to accomplish?
2. What would a successful result look like?
3. When should it run: on request, on a schedule, or after an event?
4. What can it inspect or change? Which boundaries apply?
5. How can the agent verify the result?
6. When should it stop or request help?

## Output format

Deliver each crafted, adapted, or repaired loop as:

```markdown
## [Loop name]
[One sentence describing purpose and stop condition.]

Prompt:
> [One concise, self-contained paragraph.]
```

Prompt pattern:

`[Do the bounded task.] After each change, [run the available check] and keep improvements that pass. Stop when [goal, limit, or no progress]. Ask before [approval-gated action].`

## Grounding

Use supplied details and facts from scoped systems or files. Label unknowns. Preserve exact published titles and URLs. Distinguish adaptations and new designs from published loops. Use neutral placeholders for unknown stack, tools, budgets, schedules, permissions, and test methods.
