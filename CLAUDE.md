<!-- LinguistProjection: generated; source=CLAUDE.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# §05§.md

§05§ (and Claude-compatible) §02§: follow **[`§02§.md`](AGENTS.md)**.

## Quick pointers

| Need | §14§ |
|------|------|
| Active work | `docs/proposals/registry.yaml` |
| How to §1a§ / close | `docs/proposals/§17§.md` |
| Gates | `docs/ARCHW1Z-GATE.md` |
| Status | `docs/ARCHW1Z-STATUS.md` |
| Permissions / §0e§ edges | `docs/proposals/AGENTIC-PERMISSIONS.md` |
| Session SSOT | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Communication law | `docs/ops/COMMUNICATION-LAW.md` |
| Siglary operators | `docs/ops/SIGLARY-OPERATOR-REGISTRY.md` |

## Communication law

- `CHAT := STATE-CHANGE ∨ OVERSIGHT`.
- Lead authored prose with `DO`: action + owner/scope + condition + expected state.
- Apply CAVEMAN-6: actor → action → object → evidence → next state; keep ≤4±1 live items.
- Use the stable Siglary operator registry; one glyph = one meaning, with explicit grouping and no implied precedence.
- Comments explain intent, invariant, boundary, trade-off, or non-obvious behavior.
- Commits use imperative, outcome-led subjects and record rationale, §1d§, and `Implements: TER-N`.
- PR/§1a§ text uses evidence → impact → requested action → acceptance condition.
- Prefer affirmative statements; preserve exact technical meaning for safety, §1b§, contracts, and diagnostics.
- Edit canonical `*.hum.md` sources; regenerate projections with `scripts/cedrlang/render_contact_projections.py` and §1f§ with `--check`.

## Defaults

- Base §04§ for PRs: **`master-staging`**
- Run before claiming done: `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`
- Merge only GO-approved PRs; exclude NO-GO PRs (#2, #6 wholesale).
- Record debate in MANIFEST §1a§ log or `DEBATE.md` as durable evidence.
