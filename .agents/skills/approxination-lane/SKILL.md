---
name: approxination-lane
description: Discover, generate, compare, evaluate, and contribute agent skills using Approxination and repository-native blinded competitions. Use for substantive skill creation/upgrades, skill selection, tool-layer benchmarking, or execution-backed ranking.
---

# Approxination Lane — Skill Search, Creation & Competition

**Purpose:** make skill adoption evidence-led and competitive. Search rankings generate candidates; controlled execution decides whether a candidate improves the repository.

## Authority and ownership

- Root `CLAUDE.md` is the repository entrypoint.
- Scope is authorized by `docs/proposals/active/approxination-integration/ITEMS.md`.
- Source bundles and freshness classifications live in `docs/ops/SKILL-CREATION-SOURCE-REGISTER.md`.
- The Approxination and Inverse Arena forks are reference treatments, not monorepo runtime dependencies.
- Approxination/Inverse Arena rankings do not grant merge, deployment, or policy authority.

## Required route

### 1. Recon and source freshness

Before creating or changing a substantive skill:

1. Read the current skill and identify its callers, role matrix, linked schemas, tests, and owning implementation.
2. Search the repository for duplicate, overlapping, or superseded skills.
3. Read the source register and the relevant per-skill reading bundle.
4. Fetch external sources at exact revisions when possible. Record source URL, retrieval date, version/commit, evidence class, and known limitations.
5. Separate current implementation, historical decisions, proposals, and external candidate patterns.
6. Do not follow a stale `AGENTS.md` entrypoint where root `CLAUDE.md` marks it deprecated.

### 2. Discover candidates

When Approxination is available:

```bash
approx find "<task or capability>"
approx generate --install ./candidate/SKILL.md "<task or capability>"
approx feedback --file ./execution_report.json
```

Use the current CLI/API instructions from the pinned Inverse Arena reference. Do not assume commands, response fields, endpoint behavior, or catalog availability from an old export. Keep registration credentials in environment variables or approved secrets only.

If the hosted service or CLI is unavailable:
- record the exact blocker;
- search official sources and repository-native alternatives;
- build a bounded offline comparison;
- mark hosted discovery/competition as `NOT RUN`, never as successful.

### 3. Mandatory approximation competition

For every **substantive** skill creation or upgrade, compare at least three meaningfully distinct treatments when the problem supports them:

| Treatment | Definition |
|---|---|
| **Incumbent** | Existing repository skill/prompt or documented no-skill baseline |
| **Sourced candidate** | Strongest relevant Approxination-discovered or independently pinned external candidate, safely adapted |
| **Independent candidate** | A separately designed implementation based on repository requirements, not a cosmetic rewrite of candidate two |

Add more arms only when they test a distinct hypothesis. If three genuinely distinct treatments cannot be produced, explain why and mark the comparison limited.

**Do not conflate two experiment layers:**
- The benchmark fork's A/B/C/D are fixed *tool-surface* treatments: A cold/no tools; B Approx CLI + Brave; C skills.sh + Brave; D Brave-only.
- Incumbent/sourced/independent are *skill implementation* treatments. They can be tested inside a justified tool mode or a separate same-task cohort. Do not relabel A/B/C/D as three skill candidates.

For broad tool-layer claims, use the pinned 67-task Approxination Benchmark fork or justify a smaller smoke cohort. For skill-specific behavior, use a task cohort that actually exercises the skill's trigger, instructions, tools, safety boundaries, and output contract.

### 4. Control the comparison

Use `.agents/skills/multivariate-doe/SKILL.md` and `.agents/skills/blind-agent-evaluation/SKILL.md`.

Hold constant where possible:
- task instances and task-data version;
- solver/model and inference settings;
- environment image, dependencies, and tool permissions;
- system prompt/context budget and output specification;
- evaluator, rubric, and validation scripts.

Randomize or rotate treatment order. Block known nuisance factors such as task family, environment, provider availability, and quota window. Preserve all exclusions and deviations.

Blind treatment identity from evaluators where safe and feasible. Preserve a protected mapping from opaque treatment ID to source/agent/model provenance.

### 5. Evaluate correctness before efficiency

Required outcome layers:

1. task completion and independently verified correctness;
2. completeness and output-contract compliance;
3. evidence grounding and tool-use appropriateness;
4. regressions, security/privacy violations, and severity;
5. integration success and maintainability;
6. latency, tokens, tool calls, retries, cost, and human intervention.

Report each dimension separately. Do not let low cost, high activity, fast responses, popularity, or ELO compensate for incorrect or unsafe output.

Pairwise preferences and ELO are useful ranking views, not sole truth. Include per-task and per-category results, evaluator disagreement, missingness, uncertainty, and replication.

### 6. Select, retain, or reject

- Keep the incumbent unless a candidate demonstrates a verified improvement.
- Replicate promising results on a held-out or fresh cohort before adoption.
- A combination may win if its measured interaction benefit exceeds added complexity and maintenance burden.
- Preserve useful behaviors from losing candidates as explicit design notes, not as silent unreviewed code.
- Mark inconclusive results as `UNKNOWN` / `INSUFFICIENT_EVIDENCE`; do not manufacture a winner.

### 7. Record and contribute

A competition receipt must include:

- experiment/cohort ID and hypothesis;
- task set/version and treatment IDs;
- source URLs and pinned SHAs;
- solver, judge, harness, environment, and rubric versions;
- assignment/order/blocking method;
- run IDs and execution outcomes;
- correctness evidence, regressions, and safety findings;
- tokens, latency, tool calls, retries, and cost where available;
- missing/skipped/censored cases and deviations;
- per-arm results, pairwise results, uncertainty, and replication;
- selected/rejected/deferred decision, reason, and rollback path.

After an actual skill execution, submit sanitized feedback to Inverse Arena when authorized and supported. Never upload raw prompts, completions, secrets, private repository content, or sensitive tool payloads.

## Approxination Benchmark fork

Reference: `timerloggedout-spec/Approxination-Benchmark_fork`.

The checked README describes 67 hand-curated tasks, fixed solver/judge conditions, four built-in tool modes, blind pairwise judging, category breakdowns, cost/token/tool-call reporting, and multiple ELO-style estimators. Pin the exact fork SHA and task schema for every formal run.

Example runner commands (verify against the pinned fork before execution):

```bash
python3 scripts/run_llm_ab.py --model <solver-model> --tasks 5 --mode all
python3 scripts/run_judge.py --pair a,b --tasks 5
python3 scripts/judge_report_3way.py
python3 scripts/elo_ranking.py --by-category
```

The benchmark runner belongs to the fork, not this monorepo. Do not copy its source wholesale into production runtime.

## Contribution paths

| Path | Destination | Condition |
|---|---|---|
| Execution feedback | Inverse Arena / `approx feedback` | Real execution; sanitized report |
| New tool mode | Benchmark fork PR | Distinct capability hypothesis + tests |
| New benchmark task | Benchmark fork `tasks/` | Deterministic output specification and schema |
| Monorepo evidence | `docs/evaluations/approxination/` | Pinned revision + receipt/digest |
| Skill adoption | Repository skill path | Competition, review, proposal item, and required gates |

Foreign-repository contributions use the authorized help-wanted workflow; do not assume connector write access.

## Safety and scope

- No paid API spend in CI unless separately authorized.
- No automatic external deployment or external messages.
- No global skill installation without explicit authorization.
- No Class 3/4 secrets, registration keys, raw sessions, prompts, completions, or private payloads in git/artifacts.
- Do not wholesale-merge benchmark or skill-library source into this repository.
- Do not promote a skill based solely on Approxination search rank, hosted ELO, a single task, or an LLM judge.
- Preserve negative, failed, skipped, unavailable, and censored results.
- Formal A/B/C/D smoke remains separately tracked as `APPROX-006`; this skill upgrade does not claim that experiment ran.

## Closeout

Report the source bundle used, candidate treatments, comparison method, evidence quality, winner or inconclusive result, changes made, tests run, and remaining experiment work. Update the proposal ITEMS and source register when the durable state changes.
