# CLAUDE.md

Claude (and Claude-compatible) agents: follow **[`AGENTS.md`](AGENTS.md)**.

## Quick pointers

| Need | Path |
|------|------|
| Active work | `docs/proposals/registry.yaml` |
| How to review / close | `docs/proposals/PROCESS.md` |
| Gates | `docs/ARCHW1Z-GATE.md` |
| Status | `docs/ARCHW1Z-STATUS.md` |
| Permissions / human edges | `docs/proposals/AGENTIC-PERMISSIONS.md` |
| Session SSOT | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Communication law | `docs/ops/COMMUNICATION-LAW.md` |
| Siglary operators | `docs/ops/SIGLARY-OPERATOR-REGISTRY.md` |

## Communication law

- `CHAT := STATE-CHANGE ∨ OVERSIGHT`.
- Lead authored prose with `DO`: action + owner/scope + condition + expected state.
- Apply CAVEMAN-6: actor → action → object → evidence → next state; keep ≤4±1 live items.
- Use the stable Siglary operator registry; one glyph = one meaning, with explicit grouping; precedence remains undefined.
- Comments explain intent, invariant, boundary, trade-off, or non-obvious behavior.
- Commits use imperative, outcome-led subjects and record rationale, validation, and `Implements: TER-N`.
- PR/review text uses evidence → impact → requested action → acceptance condition.
- Prefer affirmative statements; preserve exact technical meaning for safety, security, contracts, and diagnostics.
- Edit canonical `*.hum.md` sources; regenerate projections with `scripts/cedrlang/render_contact_projections.py` and verify with `--check`.

## Defaults

- Base branch for PRs: **`master-staging`**
- Run before claiming done: `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`
- Merge only GO-approved PRs; exclude NO-GO PRs (#2, #6 wholesale).
- Record debate in MANIFEST Review log or `DEBATE.md` as durable evidence.
