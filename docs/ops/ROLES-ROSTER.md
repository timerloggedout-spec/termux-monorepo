# Agent role roster (Development Teams + challenge roles)

**Sources:** [#129 Development Teams && Emerging Technologies Research Team](https://github.com/timerloggedout-spec/termux-monorepo/issues/129) · challenge-role mandate · Delphi · MoneyBall (#131).

Continuous evaluation and rotation by performance. Roles are **hired** as agent configs (skills, scopes, contexts, tools, connectors) — not vanity titles.

---

## 1. Challenge roles (mandatory on P0 / security / matrix)

| Role | Duty | Ballot |
|------|------|--------|
| **Skeptic** | Falsify assumptions, demand metrics | `ROLE: skeptic` |
| **Critic** | Attack design/quality of the change | `ROLE: critic` |
| **11th Man** | Outsider / red-team disruptor (not “11th rubber stamp”) | `ROLE: 11th-man` |

Full text: [`ROLES-SKEPTIC-CRITIC-11TH.md`](ROLES-SKEPTIC-CRITIC-11TH.md).

---

## 2. Team Development roster (#129)

From the issue body (normalized labels):

| Roster id | Issue phrasing | Function |
|-----------|----------------|----------|
| **operator** | human / OPERATOR | Tier-4 authority, matrix commit, credentials |
| **cto-lite** | CTO (??) meh | Architecture sequencing — optional, low weight until proven |
| **cfo-lite** | CFO (??) meh | Quota/cost / free-tier burn — optional |
| **engineer** | Engineers | Implement, gates green, minimal diffs |
| **researcher** | Researchers | Surveys, leaderboards, caveman/Grimoire seeds |
| **l337** | `l337 4@×π$ FTW` | Elite execution — high-skill implementer, compression, CI surgery |
| **haxor** | `H@×0π$ !!!` | Adversarial creativity, exploit-minded review, edge-case hunting |
| **script-kiddie** | `Script Kiddies!!` | Scaffold / copy-adapt / first-pass automation — **supervised**; evidence not authority |
| **l33t-squad** | CodeRabbit “l33T $Qu@D” | Named peer reviewers in the squad (roster agents, not silent bots) |
| **scout** | MoneyBall / HR-like draft picker | Hierarchical agent that drafts/clones top performers; not a line manager |
| **orchestrator** | Swarms and Orchestrators | Multi-agent routing (`termux-multi-agent`, kai-gomez swarms refs) |
| **swarm-member** | Swarms | Parallel workers under an orchestrator |
| **bettor** | 3L0≈ELO betting agents | Bid on jobs; internal points / future PolyMarket-style spectators (#131) |
| **spectator** | Spectators on betting arena | Observe / score; no merge authority |

### Spelling note

`l337 h@×π` / `haxor` / `4@×π$` are **roster slang ids**. In formal logs use:

```text
ROLE: l337
ROLE: haxor
ROLE: script-kiddie
ROLE: engineer
ROLE: researcher
ROLE: scout
ROLE: orchestrator
```

---

## 3. Lifecycle (from #129)

```text
Roster pool  →  draft (scout / MoneyBall)
             →  perform (gates, debates, matrix)
             →  rank (3L0 / ELO-like, continuous)
             →  bottom % : remove from participation (may remain for learning only)
             →  top %    : clone with modifications (% random + % constructed by scout)
             →  mid tier : evolving A/B
```

- **Creating roles** = defining skills, scopes, contexts, tools, connectors, plugins.
- **Hierarchy** is capability hierarchy, not corporate cosplay.
- Seed paths: `termux-multi-agent/*`, swarm references, #131 MoneyBall arena.

---

## 4. Delphi weight seeds (tunable)

| Role | Weight (seed) | Notes |
|------|---------------|-------|
| operator | 1.0 | Commits matrix / Tier-4 |
| 11th-man | 0.9 reject-with-evidence / 0.5 bare accept | Red-team |
| haxor | 0.85 | Adversarial findings |
| skeptic | 0.8 | |
| l337 | 0.75 | Elite implement signal |
| critic | 0.7 | |
| engineer | 0.65 | |
| researcher | 0.6 | |
| scout / orchestrator | 0.55 | Process, not proof |
| script-kiddie | 0.25 | Supervised only |
| bettor / spectator | 0.1 | Arena signal |
| unrostered bot | 0.0 | Evidence only until `VOTE:` logged |

See [`DELPHI-WEIGHTING.md`](DELPHI-WEIGHTING.md).

---

## 5. Participation rules

- **Debate + Decision Matrix** mandatory for P0/High when acting under any roster role.
- Bots (Jules, CodeRabbit, Devin, …) stay **evidence** until a roster id posts `VOTE:` / `ROLE:` into the log.
- CodeRabbit is invited to **l33t-squad** per #129 — still must log votes to count.

## Related

- #129 · #131 · #145 · #90 · `docs/CONSENSUS.md`
- [`ROLES-SKEPTIC-CRITIC-11TH.md`](ROLES-SKEPTIC-CRITIC-11TH.md)
- [`MATRIX-QUEUE.md`](MATRIX-QUEUE.md)

Signed-off-by: Grok (OPERATOR) session-2026-08-10 / msg-l337-roster
