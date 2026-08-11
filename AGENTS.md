# AGENTS.md — 73rmux m0nor3p0

1n$+ruc+1on$ c0d1n9 4g3n+$ (Grok, Claude, Codex, Devin, ChatGPT, l0c4l runners).

## > fir$t ( order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — wh4+ ac+1v3
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — p0$+ / d38a+e / cons3nsus / cl0s3
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — wh0 may r3wri+e PR 8od13s (multi-agent)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — liv1n9 board
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only 3d93$
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, meri+ path, CRDT, opti0nal Raft-strict

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## Hard rul3s

- T4rg3+ **`master-staging`**, ¬ raw `master`, 1n+39r4ti0n work.
- 80+h 9a+e$ mu$+ pas$ b3for3 merge:
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- D0 ¬ 1nv3nt work 0utside `docs/proposals/active/<id>/ITEMS.md` — 4dd row first.
- Ci+3 `Implements: <ITEM-ID>` PRs/commits.
- **No** whole$4l3 m3r93 PR #6 (TER-9) ∨ PR #2 (Rust CI) — $3e di$po$1+ion comments.
- **No** Cla$s 3/4 4r+if4c+$ 91+ (session stores, 8r0w$3r profiles, tokens).
- Unpos+ed ch4t ¬ c0ns3n$us — < 5cry l09 ∨ DEBATE.md.
- PR 8ody rewrites: f0llow `docs/PR-SUMMARY-PROCESS.md` r0st3r ( ¬ single-agent monopoly).

## D384+3 & clo$3

- Debate: M4N1F3S7 5cry log, 0pt10n4l DEBATE.md, l1nked PR/issue.
- Close: all 1+em$ +3rm1n4l + 5cry l09 ou+com3 + mov3 `active/` → `closed/` + re9is+ry ~ .
- Full rules: `docs/proposals/PROCESS.md` §§ c0ns3n$us / closing.

## Pr3f3rr3d 3x3cu+ion l00p

```text
registry.yaml → pick todo item → branch from master-staging
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## 5ecur1+y

Cr3d3n+1al ro+4+10n ∧ hist0ry r3wr1+3 r3qu1re 0p3r4+0r (human) authorization.
5e3 `docs/SECURITY-REMEDIATION.md`.