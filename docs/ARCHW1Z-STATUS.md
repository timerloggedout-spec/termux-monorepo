# ArchW1z Status Board

> Living recon. Updated as gates land and PRs resolve.
> Sources: ChatGPT Critical-Eval, ChatGPT-initial, ChatGPT_droidApp, live branch/PR inventory.

**Last update:** 2026-08-09 — peer routing live; OpenRouter matrix pending merge

---

## Gate spine (LIVE on master-staging / master)

| Gate | Status | Command |
|------|--------|--------|
| **repo-gate** | ✅ LIVE | `python3 scripts/ci/repo_gate.py` |
| **termux-smoke** | ✅ LIVE | `python3 scripts/ci/termux_smoke.py` |
| language / provider | ⏳ later | — |

```
repo-gate → termux-smoke → language/provider → master
```

---

## Routing spine (2026-08-09)

| Layer | Status | Notes |
|-------|--------|-------|
| model-router peers | ✅ LIVE | Omni ↔ OpenRouter first; Gemini residual |
| http-llm-invoke | ✅ LIVE | HTTPS + host allow-list; `:free` only on OR |
| after-peers second pass | ✅ LIVE | #102 |
| free model matrix + fallback loop | ⏳ PR #104 | Approved; merge to close RL-05 |
| fail-fast sequential fallback | ⏳ PR #105 | Rebase after #104 |
| quota-gate on default branch | ⏳ PR #81 | RL-10 |

---

## Specs landed

| Doc | Purpose |
|------|--------|
| `docs/ARCHW1Z-GATE.md` | Two-gate spine |
| `docs/TERMUX-SMOKE.md` | Smoke gate details |
| `docs/ARCHW1Z-STATUS.md` | This board |
| `docs/CONSENSUS.md` | Tiers, merit, CRDT, Raft-strict |
| `docs/schemas/session-ssot.md` | TER-10 Session SSOT |
| `docs/schemas/provider-capabilities.md` | Capability registry |
| `docs/schemas/llm-leaderboard-matrix.yaml` | Role preferred free models |
| `docs/SECURITY-REMEDIATION.md` | PR #3 A+B+C checklist |

---

## Merge rule

1. Target **`master-staging`** for integration code; workflows that must fire from default branch promote to **`master`**
2. **repo-gate** + **termux-smoke** green
3. No unresolved critical review threads
4. Security: A + B + C
5. Process docs may promote to **`master`** for discoverability

Signed-off-by: Grok <grok@x.ai>
