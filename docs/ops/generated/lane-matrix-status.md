# Lane matrix status (2026-10-26T01:15:00Z)

- Master: `7bdabc5a00e15fc576c8de1fa232d8235133cc2b`
- Open PRs: ~160+ (observer budget classifies most as HOLD/stale)
- No dual-gate SUCCESS + mergeable CANDIDATE observed on current tip.
- Recent push dual-gate on ancestor SUCCESS.
- Lane matrix previously stale (2026-10-23, tip e60c1698).

| Lane | Count |
|------|------:|
| CANDIDATE | 0 observed on live tip |
| EXTRACT | residual |
| NEED_EVIDENCE | majority |
| SUPERSEDE | residual |

Writer only: does not merge. Dual-gate remains promote authority. HOLD/WAIT/OBSERVE are invalid parking. Age alone ≠ promote.

Next: rebase high-signal lagging PRs onto tip for dual-gate reconfirm.
