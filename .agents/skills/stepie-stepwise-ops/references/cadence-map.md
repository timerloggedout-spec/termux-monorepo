# Cadence map — Stepie vs other production loops

## Stepie (planning)

- Holds ordered milestones for goal 2087.
- Completion criteria + trigger cues + RECON notes.
- Does not run CI or merge.

## LANE-MATRIX (classification SSOT)

- Tip-first PROMOTE / WAIT / HOLD / EXTRACT / OBSERVE / SUPERSEDE.
- Rewritten every admin session.
- Source of truth for which PR is preferred extract.

## adaptive-wait (execution discipline)

- Dual-gate before promote.
- Stay busy on disjoint work (skill mirrors, SSOT, triage).
- No idle poll loops.

## evidence-led-monorepo-ops (session stamp)

- Session tip, mega policy, co-load list, Agent-Identity.
- Load every admin session with adaptive-wait.

## help-wanted-lane

- Foreign claim → PR → follow-up poll → dashboard receipts.
- Parallel to 2087; link by note, do not merge trees.

## Mayan / concurrent lattice (#631)

- Multi-phase parallel work in Actions + proposals.
- Stepie milestones express outcomes; lattice expresses concurrency.

## CI dual-gate

- `repo_gate` / hygiene+portability + `termux_smoke`.
- Only promote when both SUCCESS and extract (not mega) policy satisfied.
- Vercel rate-limit is non-gate.
