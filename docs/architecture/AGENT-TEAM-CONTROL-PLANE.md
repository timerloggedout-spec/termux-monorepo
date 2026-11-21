# Agent Team Control Plane

**Status:** canonical architecture description
**Owner/lane:** Agent Team Control Plane
**Canonical for:** the agent-team operating loop and control-plane shape

The canonical compact architecture chart is [`AGENT-TEAM-CONTROL-PLANE.mmd`](./AGENT-TEAM-CONTROL-PLANE.mmd).

## Operating loop

```text
BROAD
  ↓
INTEGRATE
  ↓
VALIDATE
  ↓
DEVELOP
  ↓
LEARN
  └────────────────→ BROAD (improved baseline)
```

**BIUDL = Broad → Integrate → Validate → Develop → Learn.**

BIUDL is the repository's compounding development motion: a broad system view selects a focused lane; the lane is integrated and validated with attributable evidence; proven work is developed into production code; learning is synthesized back into the broad baseline.

## Control-plane chart

```text
SCOUT POPULATION
  │
  ├── provider/model research
  ├── code reconnaissance
  ├── performance evaluation
  ├── oversight/security evaluation
  └── regression scouting
  │
  ▼
TEAM CANDIDATES
  │
  ├── OX-ALPHA
  ├── DEEPSEEK
  └── GEMINI / future providers
  │
  ▼
MVT / DOE
  │
  └── provider × model × prompt × manager × cohort × sequencing
  │
  ▼
WORKSPACE / EXECUTION
  │
  ├── shared read-only investigation
  ├── coordinated shared workspace
  ├── isolated Git worktrees
  └── container / remote executor
  │
  ▼
TELEMETRY
  │
  └── SHA → run → job → step → logs → artifacts
  │
  ▼
BILATERAL REVIEW
  ├── RETAIN / PROMOTE
  └── CULL / QUARANTINE (preserve provenance)
  │
  ▼
MONEYBALL / 3L0
  │
  ▼
TEAM ADMISSION
  │
  ▼
SKILL / SSOT SYNTHESIS
  │
  ▼
BIUDL
  │
  └──────────────────────→ next Scout cycle
```

## Lane ownership

| Lane | Function | Evidence output |
|---|---|---|
| Scout | discover and normalize provider/model/task candidates | candidate roster |
| Builder | smallest useful implementation in an explicitly declared workspace | commit/SHA |
| Recon | correlate prior art and context | provenance graph |
| Experiment | DOE/MVT treatments and performance requests | request/run records |
| Workspace | enforce actual isolation and write ownership | sanitized workspace evidence |
| Telemetry | collect and reduce runtime evidence | run/job/step/artifact records |
| Review | bilateral critique and regression detection | review disposition |
| MoneyBall | score observed performance | ranking/treatment score |
| Synthesis | promote reusable knowledge | skill/SSOT revision |

## Promotion rule

The system must not equate activity with success. A green workflow, HTTP 200, reviewer acknowledgement, low latency, or large response can be an observation, but **task outcome remains separately classified** as `PASS`, `FAIL`, `UNKNOWN`, or other documented state.

Correctness has priority over latency. Resource/quota state is a capacity signal, not a quality score.

## Dynamic population

Scout discovers candidates from observed provider/model/task evidence. OX-Alpha and DeepSeek are current priority admission lanes, but neither is permanently privileged. Additional models and providers can enter through the same evidence-backed pipeline.

Scout proposals do not grant routing authority. Managers/MoneyBall/3L0 make promotion decisions from observed evidence.

## Workspace and isolation policy

Workspace isolation is a treatment dimension, not a product-specific assumption. Shared read-only investigation is the default for reconnaissance; independent mutable tasks should use isolated Git worktrees when available. Multiple writers in one checkout require explicit path ownership or serialization. Containers and remote workspaces must report their actual isolation boundary separately from Git isolation.

See [`docs/ops/AGENT-WORKTREE-ORCHESTRATION.md`](../ops/AGENT-WORKTREE-ORCHESTRATION.md) and the existing [native orchestration contracts](../ops/ORCHESTRATION-CONTRACTS.md). Kilo Agent Manager is a research reference, not a required dependency or proof of Termux runtime support.

## Agent lifecycle and culling

Culling is a state transition, not deletion. Preserve agent identity, attempts, scores, contribution lineage, reviews, and provenance so later analysis can distinguish failure, cooldown, capacity exhaustion, and genuine underperformance. Any future wallet/reward/community-pot accounting must consume this contribution ledger rather than altering performance evidence.

## Evidence lineage

A node transition is not proof of success. Promotion requires attributable evidence. The telemetry lineage is:

`SHA → workflow run → job → step → logs/artifacts → outcome → review → promotion decision`.

## Research and oversight cohorts

Scout missions can propose work across provider research, code reconnaissance, performance testing, regression investigation, and oversight/security evaluation. Examples include bug-bounty, Help Wanted, CTF, developer-skill, security-skill, and other validation cohorts. These are evaluation populations and task sources, not automatic trust grants.

## Related systems

- `.agents/skills/evidence-led-monorepo-ops/SKILL.md`
- `.agents/skills/review-loop/SKILL.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- `.agents/skills/context-relationship-graph/SKILL.md`
- `.agents/skills/gemini-performance-psychology/SKILL.md`
- `.agents/skills/multivariate-doe/SKILL.md`
- `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md`
- `docs/ops/SCOUT-MISSIONS.md`
- `docs/ops/SCOUT-ROSTER.md`
- `docs/ops/ACTIONS-METRICS-INTEGRATION.md`
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.mmd`
- `docs/architecture/SELF-HEALING-ENGINE-ROADMAP.md`
