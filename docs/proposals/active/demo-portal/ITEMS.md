# ITEMS — demo-portal

| ID | Item | Tier (CONSENSUS.md) | Status | Notes |
|----|------|------|--------|-------|
| DP-001 | Phase 1: record real `archwiz.py` / `deepcli-tui` terminal sessions (asciinema or equivalent) and embed playback on the `demo-portal/public` Vercel lane | 1-2 (Driver/Light) | proposed, not built | No execution surface - pure static content. Next concrete build step. |
| DP-002 | Phase 2: client-side sandboxed execution of scoped example scripts via an in-browser WASM runtime (e.g. Pyodide) - no server-side execution | 2 (Light) | proposed, directional | Needs a scoped list of "safe" examples agreed before building - not just archwiz.py wholesale. |
| DP-003 | Phase 3: real ephemeral sandboxed containers on Render for full interactive shells | 3 (Quorum) - re-propose separately | not started, not approved | Deliberately not approved by this proposal. Needs its own security review (isolation model, rate limits, network egress restrictions, abuse handling) before it is built, given this repo's credential-exposure history and the public attack surface a real shell represents. |

## Implements tags

None yet - this proposal registers the plan. DP-001's implementing commit will cite `Implements: DP-001` when built.