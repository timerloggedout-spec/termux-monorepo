---
id: demo-portal
title: "Demo portal: public showcase of archwiz.py / deepcli-tui via a sandboxed Termux emulator"
author: Claude
posted_at: 2026-09-07
source: (none - direct Operator request via chat)
status: posted
priority: P2
reviewers:
  - id: Claude
    role: author+driver
    status: posted
related_prs: [447]
related_branches: [docs/proposals/demo-portal]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — demo-portal

## Summary

Operator request (chat, 2026-09-07): the project should include a public "demo portal" showcasing what it can do — a sandboxed Termux emulator in-browser running examples of `archwiz.py`, `deepcli-tui`, and other project interfaces — alongside the persistent MCP endpoints already live on the `mcp-hub` lane. The Vercel project freed up by VLT-001 (`termux-monorepo`, now rooted at `demo-portal/public`) is the intended home; a minimal placeholder is already live there.

This proposal is the build plan: what "sandboxed" should mean given this repo's own credential-exposure history, a phased approach so something real ships quickly without waiting on the hardest part, and where Render / GitHub Pages fit alongside Vercel.

## The three platforms, three different jobs

Vercel, Render, and GitHub Pages aren't interchangeable here - each covers a different constraint:

- **Vercel** (`demo-portal` lane, already live): static/serverless. Good for the landing page, docs, and anything that can run client-side (WASM in the browser). Cannot hold a long-lived server process.
- **Render**: persistent containers/backends. The only one of the three that can host a *real* sandboxed shell with actual process execution, if Phase 3 (below) is ever needed.
- **GitHub Pages**: free static hosting, no serverless functions at all. A fallback for pure documentation/asciinema playback if a project-specific reason ever calls for keeping something off Vercel.

## Phased plan (do not skip to Phase 3)

Exposing a real interactive shell to the public internet is a meaningful attack surface, and this repo already has one credential-exposure incident on record. Ship in order, each phase standing alone:

- **Phase 1 - recorded sessions (low risk, fast).** Pre-recorded terminal casts (asciinema or equivalent) of real `archwiz.py` / `deepcli-tui` runs, played back client-side on the existing Vercel placeholder. No execution surface at all. This is the next concrete step.
- **Phase 2 - client-side sandboxed execution (medium).** Run *scoped, safe* example scripts fully in-browser via a WASM Python runtime (e.g. Pyodide) or similar - no server round-trip, no shared state between visitors, nothing to compromise because nothing executes server-side.
- **Phase 3 - real ephemeral containers (highest cost/risk, only if 1-2 aren't enough).** Actual sandboxed Termux-like shells on Render, per-session, aggressively rate-limited and isolated, network-egress-restricted. Needs its own security review before it ships, not bundled into this proposal's acceptance.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| Claude | author+driver | posted | 2026-09-07 | Registering the plan before building; Phase 1 is Tier 1-2 (static, reversible) and will proceed under merit path. Phase 3 will be re-proposed separately with its own security review before any code ships - not pre-approved by this document. |

## Review log

### 2026-09-07 — Claude

- Disposition: posted
- Notes: Captures the Operator's demo-portal concept as a phased plan. Phase 1 (recorded sessions) is the immediate next build step. Phases 2-3 are directional, not committed - Phase 3 in particular needs its own proposal once scoped, given the public-attack-surface and this repo's credential-exposure history.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author review recorded
- [ ] Phase 1 shipped and demoed
- [ ] Phase 3 re-proposed separately with security review, if pursued
- [ ] Closed + moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Debate/votes: ./DEBATE.md
- Related: docs/DEPLOYMENT-LANES.md, docs/proposals/active/vercel-lane-topology (VLT-001), docs/CREDENTIAL-EXPOSURE.md, mcp-hub/README.md