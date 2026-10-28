# Lane matrix status (2026-10-28T17:10:00Z)

- Master: `35eaed34b23a3cd5e9289c5b7e42f99b62c4e147`
- Open PRs: **~80+** (full sweep recommended; recon sample of recent 20+)
- Oldest: #47 (ancient) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count (approx from recon) |
|------|------:|
| CANDIDATE | ~30 |
| EXTRACT | 1 |
| NEED_EVIDENCE | ~25 |
| SUPERSEDE | ~25 |

| Age bucket | Count |
|------------|------:|
| ancient | ~12 |
| fresh | ~50 |
| mid | ~5 |
| stale | ~15 |

## Tip lanes (current tip base candidates)

| PR | Base tip | Lane | Notes | Title |
|---:|----------|------|-------|-------|
| #2053 | yes (35eaed34) | CANDIDATE | mergeable unstable; no dual-gate runs visible | chore(delphi): refresh delphi-ledger-feed.json |
| #1965 | yes (35eaed34) | CANDIDATE | mergeable clean; dual-gate not evidenced on checks | chore(delphi): refresh delphi-rfp-feed.json |
| #1966 | lagging | NEED_EVIDENCE | ops matrix | ops(matrix): delphi 403 resilience + live Actions matrix refresh |
| #2015 | lagging | NEED_EVIDENCE | secrets doc | docs(secrets): phantom-secret remediation map |

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

Recon: no dual-gate SUCCESS + clean mergeable on current-SHA tip for auto-promote this cycle. Next: regenerate full matrix via operator-matrix workflow or advance portability ratchet.
