# Decision Matrix cue & queue (Actions)

## Mandate

The Decision Matrix is not only manually edited. A **cue + queue** from GitHub Actions must be able to **propose** rows/updates from:

- `docs/proposals/` (active MANIFEST / registry)
- Open issues & PRs (labels: priority, production, jules, bug)
- Debate logs (`DEBATE.md`, Review log entries)
- Gap findings (bot evidence classified as gaps, not disposition)

**OPERATOR or Tier-3 social path** still **commits** score changes to `DECISION-MATRIX.md` (clean data file). The queue posts **proposals**; it does not silent-LWW the matrix (`docs/CONSENSUS.md`).

## Cue markers

```text
<!-- matrix-queue -->
<!-- matrix-proposal -->
```

## Queue workflow

See `.github/workflows/agent-matrix-queue.yml`:

- schedule + `workflow_dispatch`
- scans open P0/priority issues & PRs
- posts a single debounced summary comment on a tracking issue (or creates matrix-proposal comments)
- never writes secrets; never auto-edits DECISION-MATRIX.md without OPERATOR signature path

## Debate participation

Agents with OPERATOR or roster roles **must** participate in Debate when:

- matrix band is P0/High and score is changing
- disposition on ops/security PRs is contested
- Delphi round is open for a subject

Silence after a clear ask may count as no-objection only at Tier 2 (`CONSENSUS.md`) — not for P0 matrix commits.

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-matrix-queue
