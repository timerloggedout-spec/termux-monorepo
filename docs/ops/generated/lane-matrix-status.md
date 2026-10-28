# Lane matrix status (2026-10-28T03:10:00Z)

- Master: `f19a6a9be808abf772914b22b9831c00a19b9eed` (sweep accountability receipt)
- Open PRs: **~85** (bases lagging current tip; no dual-gate SUCCESS + mergeable on live tip observed)
- Oldest: #47 / #48 (ancient, wrong-base master-staging)

| Lane | Count |
|------|------:|
| CANDIDATE | observed stale |
| EXTRACT | 1 |
| NEED_EVIDENCE | observed |
| SUPERSEDE | observed |

| Age bucket | Count |
|------------|------:|
| ancient | high |
| fresh | recent refresh PRs |
| mid | |
| stale | high |

## Tip lanes (EXTRACT / CANDIDATE / NEED_EVIDENCE first)

No CANDIDATE on current tip `f19a6a9be808abf772914b22b9831c00a19b9eed`. Recent open PRs (e.g. #1883, #1872, #1869) have lagging bases. Dual-gate remains promote authority.

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

**Recon 2026-10-28 03:10 UTC:** Tip advanced via sweep receipt. Portability Class D remains 0. Session-store (Class E) and space paths (Class F) remain the highest remaining ratchet targets. Ghost workflow 37655538554 still queued on disabled id. #184 names-only. #903 HOLD. Do not pulse #175.
