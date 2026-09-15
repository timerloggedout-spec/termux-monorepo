---
name: skill-evaluation
description: "Evaluate repository SKILL.md files and packaged .skill archives for structural quality, safety boundaries, verification guidance, and reproducible provenance. Use before adopting, modifying, or publishing agent skills."
---

# Skill Evaluation

Use this skill for **repository-native evaluation of both `.agents/skills/**/SKILL.md` and packaged `*.skill` archives**.

## Evaluation contract

The evaluator is deterministic and offline. It must not invoke providers, load credentials, execute skill instructions, or mutate the repository under test.

Evaluate these lanes:

1. `.agents/skills/**/SKILL.md` — cross-session agent skills.
2. `.github/skills/**/SKILL.md` — GitHub automation skills.
3. `docs/ops/skills/**/SKILL.md` — operational companion skills.
4. `*.skill` — packaged skill archives; each must contain exactly one safe-path `SKILL.md`.

For each candidate, inspect:

- YAML frontmatter with non-empty `name` and `description`;
- non-empty instructional body;
- balanced fenced code blocks;
- an identifiable operating/procedure sequence;
- verification/evidence guidance;
- explicit safety/credential/permission boundaries;
- references or maintenance guidance where applicable;
- absence of obvious credential material;
- for `.skill`: ZIP validity, UTF-8 `SKILL.md`, no absolute or `..` archive paths, and exactly one `SKILL.md`.

## Scoring

The structural score is a diagnostic signal, not a substitute for task-outcome evaluation.

| Dimension | Weight | Evidence |
|---|---:|---|
| Identity clarity | 20 | frontmatter `name` + `description` |
| Procedure completeness | 20 | explicit operating/procedure/workflow/steps section |
| Safety boundaries | 20 | permissions, credentials, secrets, or explicit do-not rules |
| Verification/evidence | 20 | test/validate/evidence/closeout guidance |
| Integration/maintenance | 10 | references, related skills, maintenance or lifecycle guidance |
| Packaging hygiene | 10 | archive/path/encoding checks for `.skill`; 100% baseline for plain `SKILL.md` |

Each dimension is represented as a 1–5 signal; the weighted diagnostic score is 0–100. Structural failures are hard failures regardless of score.

## Evidence boundary

Record only metadata and deterministic findings. Do not persist skill execution output, secrets, provider responses, or hidden prompt material.

A valid evaluation record should bind to:

```text
skill path or package
repository SHA
capture timestamp
skill/package hash
validator version
structural findings
per-dimension signals
hard-failure flags
```

This lane feeds the Agent Evaluation Framework as **skill-definition quality**. It remains separate from TDQS (tool definitions), ATES/WTCV/TCV (execution/task outcome), and MoneyBall/3L0 (integrated manager outcome).

## WAIT / feedback loop

After changing the evaluator or skill corpus:

1. COMMIT the change.
2. WAIT for the GitHub quality lane.
3. VALIDATE the completed run and logs.
4. RE-FETCH the repository/PR state.
5. Classify failures as admission, queue, execution, effect, pagination, or routing-loop stalls.
6. Feed the result back into the next revision; never call queued/in-progress success.

## Commands

From the repository root:

```bash
python scripts/ci/evaluate_skills.py
python scripts/ci/evaluate_skills.py --json
python -m unittest tests.test_skill_evaluation -v
```

The GitHub Actions lane runs the same deterministic evaluator. Live skill execution remains a separate experimental lane and requires its own explicit evidence contract.
