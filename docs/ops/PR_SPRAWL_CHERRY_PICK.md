# PR Sprawl Isolation & Cherry-Pick to Trunk

**Status:** ACTIVE operator policy  
**Aligned with:** issue #175 (prefer small/fat green PRs), Qoda limits, dual-gate spine  

## Problem

Many concurrent micro-PRs increase:

- Review and Actions quota burn
- Merge conflicts and dirty bases
- Overlapping file claims across agents
- Noise that blocks “perfect trunk” merges

## Policy

1. **Prefer one fat PR per coherent stream** — stack related commits on the same branch (example: Gemini maximization stayed on #273).
2. **Do not open parallel PRs** for the same lane or overlapping paths without an explicit extract plan.
3. **Dirty mega-PRs** — do not merge wholesale; **cherry-pick** only green, gated slices onto a clean branch from current `master` / `master-staging`.
4. **Supersede** stale PRs with a comment pointing at the replacement; close when the trunk slice lands.
5. **Cherry-pick recipe:**

```bash
git fetch origin
git switch -c extract/<topic> origin/master   # or master-staging per AGENTS.md
git cherry-pick -x <sha1> [<sha2> ...]       # only commits that pass local gates
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py
# open ONE PR for the extract; link Issues: / Supersedes:
```

6. **Agent claim markers** — before editing, scan open agent PRs; avoid claimed files.
7. **Wait** while peers are working — do not race half-finished branches into trunk.

## Isolation checklist (before opening a PR)

- [ ] Same topic already has an open PR? → stack there.
- [ ] Paths overlap another open agent PR? → coordinate or wait.
- [ ] Can this wait for a peer’s AvailableSets composition? → wait.
- [ ] Is the diff the minimum for a green trunk slice? → yes before open.

## Related

- `docs/LEGO_FORK_INTEGRATION.md` — composition / AvailableSets analogue
- `docs/ops/LANE_CONSOLIDATION_SSOT.md` — lane ownership
- issue #175 — operator priority matrix
