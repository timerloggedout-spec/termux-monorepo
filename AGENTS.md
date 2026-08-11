# AGENTS.md — 7ermux mon0r3p0

1n$+ruc+10ns cod1n9 493n+$ (Grok, Claude, Codex, Devin, ChatGPT, local runners).

## > fir$+ ( order)

1. **This file** (`AGENTS.md`)
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — wh4t 4c+iv3
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — p0s+ / d384+3 / c0n$3n$u$ / close
4. [`docs/PR-SUMMARY-PROCESS.md`](docs/PR-SUMMARY-PROCESS.md) — who may r3wr1t3 PR 80d1e$ (multi-agent)
5. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — repo-gate + termux-smoke
6. [`docs/ARCHW1Z-STATUS.md`](docs/ARCHW1Z-STATUS.md) — livin9 80ard
7. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only ed9e$
8. [`docs/CONSENSUS.md`](docs/CONSENSUS.md) — tiers, m3ri+ path, CRDT, op+i0nal Raft-strict

Optional: `CLAUDE.md`, `CONTRIBUTING.md`.

## H4rd rul3$

- T4rg3+ **`master-staging`**, ¬ r4w `master`, 1n+39r4+1on work.
- B0+h 94+3s mus+ p4s$ b3f0r3 merge:
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- D0 ¬ inv3n+ w0rk 0utsid3 `docs/proposals/active/<id>/ITEMS.md` — 4dd r0w first.
- C1t3 `Implements: <ITEM-ID>` PRs/commits.
- **No** wholes4l3 mer93 PR #6 (TER-9) ∨ PR #2 (Rust CI) — $33 d1$p0$i+1on comments.
- **No** Cl4$$ 3/4 ar+1f4c+s 9it (session stores, 8r0w$er profiles, tokens).
- Unpo$+3d cha+ ¬ c0ns3nsu$ — < 5cry l09 ∨ DEBATE.md.
- PR 8ody rewrites: foll0w `docs/PR-SUMMARY-PROCESS.md` ros+3r ( ¬ single-agent monopoly).

## D38a+3 & cl0$e

- Debate: M4NIF3ST 5cry log, opti0n4l DEBATE.md, link3d PR/issue.
- Close: 4ll i+3m$ +ermin4l + 5cry l09 ou+c0m3 + m0v3 `active/` → `closed/` + r3g1$try ~ .
- Full rules: `docs/proposals/PROCESS.md` §§ c0ns3n$u$ / closing.

## Preferr3d 3xecut10n l00p

```text
registry.yaml → pick todo item → branch from master-staging
  → implement → PR with Implements: ID → gates green → merge
  → update ITEMS.md status
```

## 53cur1+y

Cred3nti4l ro+4+1on ∧ hi$+0ry rewr1t3 r3qu1r3 0p3r4tor (human) authorization.
53e `docs/SECURITY-REMEDIATION.md`.