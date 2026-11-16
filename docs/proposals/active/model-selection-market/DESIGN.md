# DESIGN — model-selection-market

**Status:** posted proposal SSOT (docs only). Runtime code lands under MSM-001..005 thin extracts.
**Policy:** BIUDL · FA-ADE · free-first · dual-gate · AVOID HITL YOLO YEET AUTOAPPROVE.

## 1. Control plane

```text
                    ┌─────────────────────────────────────┐
                    │  TOTAL GRAPH (role × model × job)   │
                    │  nodes = trading cards (code+meta)  │
                    └──────────────┬──────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
   SELECTION CHAIN            PERFORMANCE LEDGER        MARKET (Bets)
   series|parallel|concurrent  3L0 / ELO++ / DSPy-DoE    Itself|Others|Job
         │                         │                         │
         └──────────── model_router / MoneyBall ◄────────────┘
```

## 2. Equal-weight bootstrap → evidence weights

On admit of an eligible free model into a role:

- `weight[role][model] = 1.0`
- Public leaderboard ranks are **features only** (`llm-leaderboard-matrix.yaml`)
- After N observed outcomes on required success-matrix dimensions, weight updates via 3L0 / ELO++
- Promotion of active-routing weight changes requires:
  1. two controlled observe cycles
  2. Issue #192-class ledger decision
  3. dual-gate green on the implementing PR

Hard eligibility unchanged: declared capability, free rule (`:free` or zero pricing), quota, SHA when required, policy_enabled.

## 3. Selection modes

| Mode | Default? | Behavior |
|------|----------|----------|
| **series** | yes (production) | soft budgets → primary → free peer fallback |
| **parallel** | canary / valley hunt | sample k free models same prompt; score after |
| **concurrent** | multi-role jobs | triage ∥ review ∥ invoke independent cards; join on Canny/done |

3L0 / MoneyBall scoring runs **after** admission success. Never sole gate.

Selector is a **decision_engines peer** (System-1 / schema), not an LLM provider.

## 4. Performance ledger (MSM-002)

Reuse `model-success-matrix.yaml` dimensions and provenance:

- Required dimensions: correctness_gate_pass, substantive_review_resolution, duplicate_noise_avoidance, time_to_safe_feedback, cooldown_queue_efficiency, resource_cost, coordinated_async_completion
- Required provenance fields already listed in success-matrix SSOT
- Confidence rules: no_samples → 0.0; historic prior only → 0.2; insufficient → report low confidence without promoting specialist
- Retention: bounded metadata + aggregates only; **never** raw issue/PR/review bodies

## 5. DSPy as DoE-MVT consideration lane (MSM-004)

- Affinity: Approxination A/B/C/D + MoneyBall evidence
- Role: multivariate prompt/optimizer experiments
- Output: signatures + metrics → trading cards / success-matrix samples
- **Not** required for default agent path
- Free-first; dual-gate before promote of any optimizer artifact
- Item APPROX-006 remains the formal A/B/C/D smoke gate; DSPy arms feed that path

## 6. Bets | Wagers | Bids {Itself | Others | Job} (MSM-005)

| Actor | Stake | Optimization | Learning |
|-------|-------|--------------|----------|
| **Itself** | model card on own next outcome | own opt script (DSPy / local) | own ELO slice |
| **Others** | peer model / engine card | shared read of ledger | cross-card only via explicit trade |
| **Job** | lane/job class | job-scoped opt | job graph edge weights |

Rules:

- Ledgered + observational until two observe cycles + ledger decision
- No auto paid spend; free-only
- Optimization scripts live as **trading cards** (versioned, role-scoped)
- Graph records: who, what, outcome, card hash, SHA

## 7. Trading card schema (sketch)

```yaml
card_id: <hash>
role: [triage|review|invoke|job:<id>|engine:<id>]
owner: <agent|model|collaborator>
artifact: path|blob_sha
opt_script: path|none
metrics:
  elo: number
  n: integer
  last_sha: string
  confidence: number
share: [private|role|public]
trade_log: []
```

Negotiable sharing = `share` + explicit `trade_log` entry. No silent copy into another role’s weight table. No secrets.

## 8. Implementation order

MSM-000 (this packet) → MSM-001 → MSM-002 → MSM-003; MSM-004 parallel under Approxination; MSM-005 after MSM-002/003.

## 9. Related SSOT (do not fork authority)

| Doc | Role |
|-----|------|
| `docs/schemas/model-rotation.yaml` | soft budgets + roles |
| `docs/schemas/llm-leaderboard-matrix.yaml` | public features |
| `docs/schemas/model-success-matrix.yaml` | 3L0 labels |
| `docs/ops/ROUTING-LOGIC-CHAIN.md` | live catalog → router |
| `docs/ops/DECISION-ENGINES.md` | System-1 comparative |
| `docs/ops/APPROXINATION-LANE.md` | A/B/C/D DoE |
| `CLAUDE.md` | FA-ADE entry |

Agent-Identity: Grok (Administrator)
