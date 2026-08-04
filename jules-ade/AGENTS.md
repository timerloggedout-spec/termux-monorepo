# AGENTS.md — jules-ade package

Contract for any agent working under `jules-ade/`.

## Scope

This package builds the **Jules + Antigravity ADE surface** inside HOME (`termux-monorepo`). It does **not** replace archwiz, deepcli, or the gate scripts.

## Branch policy

| Branch | Use |
|--------|-----|
| `feature/jules-ade` | Default integration branch for this package (multi-agent) |
| `feature/jules-ade-*` | Optional sub-slices (one concern each) |
| `master-staging` | PR target when a slice is gate-ready |
| `master` | Cherry-pick only after staging + smoke |

## Read order

1. Root `AGENTS.md`
2. `jules-ade/README.md` + this file
3. `jules-ade/roster.yaml`
4. `jules-ade/research/*`
5. `docs/ARCHW1Z-GATE.md` + `docs/proposals/PROCESS.md`

## Hard rules

- **No secrets** in tree (`JULES_API_KEY`, tokens, session stores).
- **No full clones** of scavenger forks into this package — metadata + sparse pointers only.
- Prefer **stdlib** for `scripts/doctor.py` and bridge probes that run on Termux CI.
- Cite `Implements: JULES-ADE-<id>` or Linear TER-* on commits/PRs.
- Do not assign routine tasks to Operator.

## Work claim protocol

1. Pick an open task under `jules-ade/tasks/` with `status: todo`.
2. Set `status: doing` + `owner: <agent-id>` in the same PR/commit when possible.
3. Implement on `feature/jules-ade` (or a slice branch).
4. Run `python3 jules-ade/scripts/doctor.py`.
5. Open PR → `master-staging` when slice is complete; keep package branch alive for parallel agents.

## Priority slices (impact order)

| ID | Slice |
|----|-------|
| JULES-ADE-01 | Research + roster (this scaffold) |
| JULES-ADE-02 | Bridge config + env contract (no network in doctor) |
| JULES-ADE-03 | Task YAML schema + example dispatches for Jules API |
| JULES-ADE-04 | MCP wiring notes ↔ Termux MCP + official `@google/jules-mcp` |
| JULES-ADE-05 | Scavenge pass: skill/dispatch patterns from forks (metadata) |
| JULES-ADE-06 | Optional thin CLI wrapper (Termux) to create Jules sessions |
