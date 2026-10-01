# Cohort — Approxination A/B/C/D tool-layer evaluation

**Family:** Oversight / tool-augmentation (AEF)
**Implements:** APPROX-001 … APPROX-004 (see proposal ITEMS)
**Reference treatments (user-owned forks):**

| Fork | Role | Default branch pin policy |
|------|------|---------------------------|
| [Approxination-Benchmark_fork](https://github.com/timerloggedout-spec/Approxination-Benchmark_fork) | 67-task bench, modes A–D, LLM judge, ELO | Pin SHA in experiment record; advance via PR |
| [Inverse-Arena_fork](https://github.com/timerloggedout-spec/Inverse-Arena_fork) | Execution-evidence ranking engine | Reference only; hosted arena is operational surface |

## Arms

| Treatment ID | Surface | Notes |
|--------------|---------|-------|
| A | Cold (no tools) | Baseline |
| B | Approx CLI + Brave | Skill library under test |
| C | Vercel skills.sh + Brave | Public directory control |
| D | Brave only | Web-search baseline |
| E+ | Custom | Via upstream contribution on benchmark fork |

## Admission

- Solver and judge models recorded (prefer different families).
- Blind pairwise judge; no arm names in judge system prompt.
- Artifact layout: `runs_llm/<task_id>/mode_{a,b,c,d}/` + judge reports + `ELO_REPORT.md`.
- Cost, tokens, tool-call counts secondary to correctness / completeness.

## Relationship to MoneyBall / 3L0

After evidence freeze and (optional) unblinding, scores and pairwise preferences feed MoneyBall/3L0 as **evidence records**. Skill-search rankings from Inverse Arena are a separate population signal (execution-backed ELO), not a substitute for this fixed-task cohort.

## Out of scope for this cohort card

- Copying benchmark Python into monorepo runtime
- Automatic CI that spends OpenRouter/Brave budget without dispatch
- Treating hosted approxination.com as a monorepo dependency for dual-gate

## Related

- `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md`
- `docs/architecture/AGENT-SELECTION-BLIND-EVALUATION.md`
- `.agents/skills/approxination-lane/SKILL.md`
- `.agents/skills/blind-agent-evaluation/SKILL.md`
