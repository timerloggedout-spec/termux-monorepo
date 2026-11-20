# ArchW1z Status Board

> Living recon. Updated as gates land and PRs resolve.
> Sources: ChatGPT Critical-Eval, ChatGPT-initial, ChatGPT_droidApp, live branch/PR inventory.

**Last update:** 2026-08-04 — docs promotion to master in progress

---

## Gate spine (LIVE on master-staging)

| Gate | Status | Command |
|------|--------|--------|
| **repo-gate** | ✅ LIVE | `python3 scripts/ci/repo_gate.py` |
| **termux-smoke** | ✅ LIVE (#11 squash-merged) | `python3 scripts/ci/termux_smoke.py` |
| language / provider | ⏳ later | — |

```
repo-gate → termux-smoke → language/provider → master
```

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
| `docs/SECURITY-REMEDIATION.md` | PR #3 A+B+C checklist |

---

## Merge rule

1. Target **`master-staging`** for code
2. **repo-gate** + **termux-smoke** green
3. No unresolved critical review threads
4. Security: A + B + C
5. Process docs may promote to **`master`** for discoverability (this promotion)
