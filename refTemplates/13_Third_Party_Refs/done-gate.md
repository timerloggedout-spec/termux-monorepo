# Done Gate — refTemplates entry (templated from AgentMon Live)

- **Concept source:** Codenotary AgentMon Live (free, open-source, 2026-11-09) — a live dashboard over a coding agent {activity - tool use - file changes - verification results} whose Done Gate flagged unfinished work 59 times in a two-day, nine-project trial, returning it to the agent before it could call the job done.
- **Fleet gen-0 (already live, 2026-11-18):** build-dispatch's completion-evidence check — a builder reporting SUCCESS with zero completion evidence is converted to FAILURE in-run (`build-dispatch-empty:v1`; fired on run 44347631446, QUE #5309). One gate, one surface.
- **Status (owner order 2026-11-18):** TEMPLATE + ADOPT — generalize gen-0 into the fleet Done Gate.

## The template
A done-claim passes only when ALL of these verify at the claim moment:
1. **Evidence per the item's own done-evidence list** — each criterion maps to a receipt (merged sha - published artifact - live state read); a criterion without a receipt = unmet, work returns.
2. **Completion clock present** (QUE #5306) — filed to done with stage timestamps; closed without it = incomplete.
3. **Landed-state verification** — the claimed artifact is read where it lives (master history - live page - store), never from the claimant's report.
4. **Live-activity trail** (the AgentMon half) — the run's activity record (ATES) exists and matches the claim's scope.

## Surfaces
- QUE completions (watchdog/executor verify step) - PR merges claiming a filing done - export publications - seat reports claiming completion.
- Failures return the work with the unmet criteria named; the gate never edits the claim to fit.

## DoE score + evolution
- Gate precision/recall scored per generation: false-done caught vs false-block friction, on ATES records.
- QUE #5552 regression suite carries the differential cases (gen-0 case: empty success).
