# ArchW1z Status Board

> Living recon. Updated as gates land and PRs resolve.  
> Sources: ChatGPT Critical-Eval, ChatGPT-initial, ChatGPT_droidApp, live branch/PR inventory.

**Last update:** 2026-08-02 (Grok / ArchW1z agent)

---

## Gate spine (LIVE)

| Gate | Branch | Status | Command |
|------|--------|--------|--------|
| **repo-gate** | `master-staging` | ✅ LIVE | `python3 scripts/ci/repo_gate.py` |
| **termux-smoke** | merged into `master-staging` via #11 | ✅ LIVE | `python3 scripts/ci/termux_smoke.py` |
| language / provider | — | ⏳ later | — |

```
repo-gate → termux-smoke → language/provider → master
```

---

## Critical-Eval progress

| Item | Status | Notes |
|------|--------|-------|
| Promote repo-gate / make master-staging real | ✅ Done | Extracted from `termux-monorepo` branch |
| Termux smoke layer | ✅ Done | #11 merged |
| PR #2 Rust CI | 🔴 Parked | Broken heredoc + wrong abstraction; after gates |
| PR #3 session-store removal | 🔴 Incomplete | A only; need B (prevention) + C (history) |
| PR #5 dispatch logging | 🟡 Open | Good fix; still couple cache→dispatch |
| PR #6 TER-9 multi-AI | 🔴 NO-GO | Bug farm; mine fixes only |
| PR #9 DeepForge | 🟢/🟡 Best direction | Launcher/help defects remain |
| PR #10 curl_cffi fallback | 🟢 Useful | Retarget + explicit TLS capability preferred |
| Session SSOT | ⏳ Next | Schema draft landing |
| Provider capability contract | ⏳ Next | After SSOT |
| Event-sourced dispatch | ⏳ P1 | |
| Content-addressed store | ⏳ P1 | |
| Four planes | ⏳ P2 | Control / Dispatch / Execution / Evidence |
| Generated intel cockpit | ⏳ P2 | From ChatGPT-initial |
| ADRs | ⏳ P2 | `docs/adr/` |

---

## Open PR disposition

| PR | Verdict | Action |
|----|---------|--------|
| #2 | 🔴 NO-GO | Close or convert to draft; Rust after gates |
| #3 | 🔴 P0 incomplete | Finish history + rotation; keep draft |
| #5 | 🟡 | Decouple then merge via master-staging |
| #6 | 🔴 NO-GO | Do not merge; extract patches |
| #7 MCP | 🟡 | After security |
| #8 TER-11 | 🟡 | Prefer #9 line |
| #9 DeepForge | 🟢/🟡 | Fix launcher; retarget base |
| #10 curl_cffi | 🟢 | Retarget to master-staging; merge when green |
| #11 termux-smoke | ✅ Merged | — |

---

## Branch disposition (summary)

**Keep / active:** `master`, `master-staging`, `termux-smoke`, `timerloggedout/ter-12-*`, `timerloggedout/ter-13-*`, `timerloggedout/ter-5-*`, `agent/repository-hygiene`

**Preserve as design/recovery:** `critical-proposal`, `feature/recon-intel-and-nav`, `recreate/refTemplates-skeleton`, `termux-monorepo`

**Park / consolidate:** `timerloggedout/ter-9-*`, `vibe/mistralai-*`, `timerloggedout-spec-patch-1`

**Obsolete candidates:** `feature/ci-gate-and-docs` (identical to old master), older DeepForge predecessors once #9 stabilizes

---

## Merge rule (conversations / reviews)

1. Target **`master-staging`** (not raw `master`) for integration work.
2. Both **repo-gate** and **termux-smoke** must be green.
3. Unresolved **critical** review threads → no merge.
4. Security PRs need A (tree clean) + B (future prevention) + C (history remediated).
5. Large provider/multi-AI PRs wait for Provider contract + Session SSOT.

---

## Next execution queue

1. Session SSOT schema under `docs/schemas/` + `~/.archwiz/sessions/` layout
2. Retarget #10 → `master-staging`; merge if still clean
3. DeepForge launcher resolver fixes on #9 line
4. PR #3 history/credential remediation checklist as executable doc
5. Provider capability registry stub
6. Close or draft-mark #2 and #6 with explicit rationale comments
