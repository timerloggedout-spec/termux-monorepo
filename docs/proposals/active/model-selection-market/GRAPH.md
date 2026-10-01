# GRAPH (MSM-005 design)

## Total graph

Nodes:

- **Role** — triage | review | invoke | job:\<id\> | engine:\<id\>
- **Model** — free-eligible model_id
- **Card** — trading card (code + meta + optional opt_script)
- **Bet** — ledger entry (Itself | Others | Job)
- **Job** — lane/job class (help-wanted, dual-gate, review, …)

Edges:

- `admits` — role → model (equal-weight bootstrap)
- `samples` — model → ledger sample
- `owns` — owner → card
- `trades` — card → card (explicit share only)
- `stakes` — actor → bet → subject
- `settles` — bet → outcome → sample

```mermaid
flowchart LR
  subgraph roles
    T[triage]
    R[review]
    I[invoke]
    J[job:class]
  end
  subgraph models
    M1[model A]
    M2[model B]
  end
  subgraph market
    C1[card]
    B1[bet]
    L[ledger]
  end
  T -->|admits weight=1.0| M1
  R -->|admits| M2
  M1 -->|samples| L
  M2 -->|samples| L
  C1 -->|opt_script| M1
  B1 -->|stakes Itself| M1
  B1 -->|settles| L
  C1 -.->|trade explicit| C1
```

## Trading cards

Schema: `schemas/trading-card.schema.json`

- Negotiable share via `share` + `trade_log` only
- No secrets
- Per-role; no silent weight table copy across roles

## Bets

Schema: `schemas/bet-ledger.schema.json`

| Actor | Meaning |
|-------|--------|
| Itself | model/engine card stakes own next outcome |
| Others | peer card |
| Job | lane/job class outcome |

Observational until two observe cycles + #192-class decision. Free-only. Settlement does **not** bypass dual-gate.

## Ops surface (future)

- Read-only graph export under `docs/ops/generated/` (observatory pattern)
- No Class 3/4 artifacts
