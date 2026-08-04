# AGENTS.md — skyhook

## Scope

Build **Jules delegation from Termux / Actions** into HOME. Do **not** spend cycles on Antigravity integration in this phase.

## Branch

| Branch | Use |
|--------|-----|
| `feature/skyhook` | Package integration (multi-agent) |
| `feature/skyhook-*` | Optional single-concern slices |
| `master-staging` | PR target when a slice is gate-ready |

## Read order

1. Root `AGENTS.md`
2. `skyhook/README.md` + this file
3. `skyhook/roster.yaml`
4. `skyhook/research/GOLD_FORK_RECON.md`
5. `docs/ARCHW1Z-GATE.md`

## Hard rules

- **Jules-first.** Antigravity = deferred notes only.
- **No secrets** in tree.
- **No full clones** of forks — metadata / sparse scavenge only.
- Stdlib for doctor + bridge probes that run in CI/Termux.
- Cite `Implements: SKYHOOK-<id>` or Linear TER-*.
- Operator is not the assignee for routine work.

## Claim protocol

1. Pick `skyhook/tasks/queue/*.yaml` with `status: todo`
2. Set `doing` + `owner: <agent-id>`
3. Implement on `feature/skyhook`
4. `python3 skyhook/scripts/doctor.py`
5. Focused PR → `master-staging` when slice complete
