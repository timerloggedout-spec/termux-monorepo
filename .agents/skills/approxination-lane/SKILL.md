---
name: approxination-lane
description: Approxination skill search, generation, contribution feedback, and A/B/C/D tool-layer evaluation. Load with help-wanted-lane + multivariate-doe + blind-agent-evaluation for oversight cohorts.
---

# Skill: approxination-lane

**Owner:** Grok Administrator / Oversight Scout + Evaluation population.

**Canonical paths:**
- `.agents/skills/approxination-lane/SKILL.md`
- `docs/ops/APPROXINATION-LANE.md`
- `docs/evaluations/approxination/COHORT.md`
- `docs/proposals/active/approxination-integration/`

**Pinned forks (reference treatments — not runtime control plane):**
- `timerloggedout-spec/Approxination-Benchmark_fork` — 67-task A/B/C/D tool-call bench + LLM judge + ELO
- `timerloggedout-spec/Inverse-Arena_fork` — pairwise execution-evidence skill ranking + fuzzy + ELO

## INTENT

1. **Skill search** — find ranked skills for a task (approx find / arena query).
2. **Skill creation** — generate a custom skill grounded in top-ranked references (approx generate).
3. **Contribution** — submit execution feedback into Inverse Arena; optionally add Mode E/F or tasks upstream on the benchmark fork.
4. **Evaluation** — run or interpret A/B/C/D arms as AEF oversight treatments for MoneyBall / 3L0.

## CLI surface (Approxination)

```bash
# One-time (requires registration key from approxination.com when using hosted arena)
npx approx init <registration_key>

# Search ranked skills for a task
approx find "send transactional email via mailchimp"

# Generate a custom skill from top refs
approx generate --install ./SKILL.md "send transactional email via mailchimp"

# After agent run: contribute execution evidence
approx feedback --file ./execution_report.json
```

HTTP alternative: `POST https://api.approxination.com/skills/execution-report` with Bearer token (see Inverse-Arena README).

## A/B/C/D evaluation arms (benchmark fork)

| Mode | Tool surface | Role in AEF |
|------|----------------|-------------|
| **A** | No tools | Cold baseline treatment |
| **B** | Approx CLI + Brave web_search | Skill-library treatment |
| **C** | Vercel skills.sh + Brave | Public directory control |
| **D** | Brave web_search only | Pure-web baseline |

Runner (on the fork, not monorepo runtime):

```bash
python3 scripts/run_llm_ab.py --model <openrouter-model> --mode all
# pairwise judge pairs: a,b a,c a,d b,c b,d c,d
python3 scripts/run_judge.py --judge-model <judge> --pair a,b
python3 scripts/judge_report_3way.py
python3 scripts/elo_ranking.py --by-category
```

## Contribution paths

| Path | Where | When |
|------|--------|------|
| Execution feedback | Inverse Arena / approx CLI | After any real skill use |
| New Mode E/F | Approxination-Benchmark_fork PR | Own tool layer to compare |
| New task | Approxination-Benchmark_fork `tasks/` | Extend corpus (SCHEMA.md) |
| Monorepo cohort evidence | `docs/evaluations/approxination/` | Pin revision + report digest |

Upstream PRs on foreign repos: use **help-wanted-execute** (MCP 403 on foreign comment/PR).

## Operating loop (agent)

1. Task arrives → `approx find` (or document offline ranking if no key).
2. Optionally `approx generate` → install skill locally under project skills path.
3. Execute work with skill; capture objective fields (steps, errors, outcome, tokens, latency).
4. `approx feedback` → feeds ELO.
5. For formal AEF runs: pin benchmark fork SHA, run A/B/C/D (or subset), freeze judge + ELO artifacts, link in cohort card.
6. MoneyBall / 3L0 consumes evidence records — not brand reputation.

## Blindness

Follow `.agents/skills/blind-agent-evaluation/SKILL.md`. Mode labels A–D are treatment IDs; do not leak vendor names into judge prompts (benchmark already anonymizes tool transcripts).

## Guards

- No Class 3/4 secrets in git. Registration keys / API tokens stay in env / Actions secrets.
- Do not wholesale-merge benchmark source into monorepo; pin as reference treatment.
- Gitlink under `refTemplates/smods/` only after ITEMS APPROX-005 decision + dual-gate.
- Dual-gate required for monorepo merges.

## Related

- `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md` — Oversight family
- `docs/architecture/AGENT-SELECTION-BLIND-EVALUATION.md` — A/B/C… candidates
- `.agents/skills/help-wanted-lane/SKILL.md` — external upstream PR delivery
- `.agents/skills/multivariate-doe/SKILL.md` — DOE factors
- `.agents/skills/find-skills/SKILL.md` — general skills.sh CLI (complementary, not replacement)

BIUDL. Agent-Identity: Grok (Administrator)
