# ITEMS — demo-portal

| ID | Item | Tier (CONSENSUS.md) | Status | Notes |
|----|------|------|--------|-------|
| DP-001 | Phase 1: record real `archwiz.py` / `deepcli-tui` terminal sessions (asciinema or equivalent) and embed playback on the `demo-portal/public` Vercel lane | 1-2 (Driver/Light) | proposed, not built | No execution surface - pure static content. Next concrete build step. |
| DP-002 | Phase 2: client-side sandboxed execution of scoped example scripts via an in-browser WASM runtime (e.g. Pyodide) - no server-side execution | 2 (Light) | proposed, directional | Needs a scoped list of "safe" examples agreed before building - not just archwiz.py wholesale. |
| DP-003 | Phase 3: real ephemeral sandboxed containers on Render for full interactive shells | 3 (Quorum) - re-propose separately | not started, not approved | Deliberately not approved by this proposal. Needs its own security review (isolation model, rate limits, network egress restrictions, abuse handling) before it is built, given this repo's credential-exposure history and the public attack surface a real shell represents. |
| DP-004 | Root README showcase section: link visitors to the landing page (timerloggedout-spec.github.io), the WIP Vercel preview portal, and the CellCog invitation | 1 (Driver) | done | Docs-only. Requested by Marketing (Chloe), approved by Operator in chat 2026-09-08. |
| DP-005 | Move the README showcase to the top as a four-badge partner banner (shields.io) and add `docs/PARTNERS.md` as the registry for future developer affiliate lanes | 1 (Driver) | done | Docs-only. Requested by Marketing (Chloe) per Operator guidance 2026-09-08. |
| DP-006 | Consolidate the referrals list (issue #574) into `docs/PARTNERS.md` — active tracked links, pipeline partners without a link yet, wallets pending addresses, the no-programme rule — and add an "Ecosystem partners" grid to the landing page | 1 (Driver) | done | Docs-only in this repo. Requested by Operator + Marketing (Chloe) in channel 2026-09-20. Banner cap later lifted (DP-007). |
| DP-007 | Expand the root README partner banner from four badges to one badge per active lane, two rows of three (CellCog · Manus AI · Polsia / Grafana · preview portal · landing page) | 1 (Driver) | done | Docs-only. Operator ruling in channel 2026-09-20 00:49: "badges stay at 4 seems like a stale perspective"; layout by Marketing (Chloe). |

## Implements tags

- DP-004: root README showcase section (PR #467, Rowan, 2026-09-08).
- DP-005: README partner banner + docs/PARTNERS.md (Rowan, 2026-09-08).
- DP-006: consolidated `docs/PARTNERS.md` from #574 + landing "Ecosystem partners" grid (Rowan, 2026-09-20).
- DP-007: README banner → six badges in two rows (Rowan, 2026-09-20).

DP-001's implementing commit will cite `Implements: DP-001` when built.
