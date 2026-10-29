# Lane matrix status (2026-10-29T00:11:00Z)

- Master: `907a2c8084b7e8103348c9040c1ecf4f5cb501fe`
- Open PRs: **101**
- Oldest: #47 (approx 83d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| CANDIDATE | ~30 (observer budget classifies most as HOLD) |
| EXTRACT | 1 |
| NEED_EVIDENCE | ~22 |
| SUPERSEDE | ~26 |

| Age bucket | Count |
|------------|------:|
| ancient | ~12 |
| fresh | ~60 |
| mid | ~5 |
| stale | ~24 |

## Tip lanes (EXTRACT / CANDIDATE / NEED_EVIDENCE first)

No dual-gate SUCCESS + mergeable CANDIDATE on live tip observed. Bases lagging (e.g. #1966 base abbdb100). Dual-gate remains sole promote authority. HOLD/WAIT/OBSERVE invalid parking. Age alone ≠ promote.

Writer only: does not merge. 

Agent-Identity: Grok (Administrator)
