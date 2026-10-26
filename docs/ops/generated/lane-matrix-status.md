# Lane matrix status (STALE — last generated 2026-10-23T17:01:55Z on e60c1698)

**Current master tip observed 2026-10-26:** `7bdabc5a00e15fc576c8de1fa232d8235133cc2b`

- Open PRs: bases lagging tip (e.g. #143 base d1cdb355, #1556 base 2ee07881). No dual-gate SUCCESS + mergeable CANDIDATE on live tip.
- Observer budget classifies many as HOLD. Dual-gate remains sole promote authority.

## Historical snapshot (do not use for promote)

- Master: `e60c16986ddc2daab83a3d5a316dfeeefae2b1e0`
- Open PRs: **60**
- Oldest: #47 (79.05d) — feat(refTemplates): restore metadata-only skeleton (Option B recovery)

| Lane | Count |
|------|------:|
| CANDIDATE | 24 |
| EXTRACT | 1 |
| NEED_EVIDENCE | 19 |
| SUPERSEDE | 16 |

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

Next: regenerate full matrix on current tip via lane workflow or extract high-signal PRs to tip for dual-gate.
