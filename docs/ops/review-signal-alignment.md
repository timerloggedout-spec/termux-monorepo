# Review signal alignment — disposition is source of truth

**Issue:** #146

## Artifact matrix

| Artifact | What it is | Actionability |
|----------|------------|---------------|
| **Analysis chain script** | Probe tooling (`gh pr view`, `fd`, `ast-grep`, …) | Internal evidence only — **not** a decision, **not** a fix |
| **Review disposition** | Judgment of diff vs requirements | **The product** — required fixes, scope splits |
| **Continuous-ops / auto-jules markers** | Debounced advance instructions | Operational triggers — must cite disposition, not scripts |
| **Peer-review-ready markers** | Gate status | Downstream signal only |

## Policy

1. Disposition is the single source of actionable signal for agent PRs.
2. Workflows must classify bot comments: disposition | probe | checklist | autofix-status.
3. Piped `@jules` instructions must reference disposition items or resolved thread IDs — never “implement the script.”
4. Optional markers: `<!-- disposition -->`, `<!-- probe -->` for machine parse.

## Implementation status

- `agent-review-auto-jules.yml` (PR #148): probe detection + disposition-first + context_key
- `agent-continuous-ops.yml` (PR #148 branch): context_key + disposition-first + continue-session
- Living matrix: [`DECISION-MATRIX.md`](DECISION-MATRIX.md) (clean data)
- Signatures: [`OPERATOR-SIGNING.md`](OPERATOR-SIGNING.md)

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-signal-align-doc
