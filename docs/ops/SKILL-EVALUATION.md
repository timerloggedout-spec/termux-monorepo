# Skill evaluation lane

**Status:** active CI contract on `ops/skill-quality-lane`; promotion target is `master`.

## Scope

This lane evaluates both source-form and packaged skills:

- `.agents/skills/**/SKILL.md` — cross-session agent skills;
- `.github/skills/**/SKILL.md` — GitHub automation skills;
- `docs/ops/skills/**/SKILL.md` — operational companions;
- `*.skill` — packaged archives containing a `SKILL.md`.

A `.skill` archive is treated as a package, not as an opaque binary. The evaluator verifies ZIP integrity, UTF-8 decoding, exactly one `SKILL.md`, and safe archive paths before evaluating the contained skill.

## Deterministic rubric

The evaluator (`scripts/ci/evaluate_skills.py`) emits six 1–5 diagnostic dimensions and a weighted 0–100 score:

| Dimension | Weight | What is observed |
|---|---:|---|
| Identity clarity | 20% | frontmatter `name` and `description` |
| Procedure completeness | 20% | operating/procedure/workflow/steps guidance |
| Safety boundaries | 20% | credential, permission, secret, and explicit prohibition guidance |
| Verification/evidence | 20% | validate/test/evidence/closeout guidance |
| Integration/maintenance | 10% | references, related skills, maintenance/lifecycle guidance |
| Packaging hygiene | 10% | safe archive + balanced fences + secret scan |

The score is diagnostic. Hard structural failures make the candidate invalid regardless of score.

## Evidence and provenance

CI produces `skill-evaluation.json` as a workflow artifact. Each record binds to the skill path/package, evaluator version, SHA-256 of the evaluated `SKILL.md` content where available, dimension signals, deterministic checks, and hard-failure flags.

No skill is executed by this lane. No provider call, credential lookup, prompt execution, or external mutation is permitted.

## Relationship to other evaluation lanes

```text
SKILL.md / .skill
       │
       ▼
Skill-definition quality
       │
       ├── AEF evidence
       │
       └── skill lifecycle / maintenance

MCP tool definition ──► TDQS
Agent execution ──────► ATES / WTCV / TCV
Integrated manager ───► MoneyBall / 3L0
Task outcome ─────────► promotion gate
```

These signals are intentionally separate. A structurally strong skill does not prove that an agent using it completes a task correctly.

## Adaptive WAIT contract

Every change to the skill evaluator or skill corpus follows:

**COMMIT → WAIT → VALIDATE → RE-FETCH → CLASSIFY → RECORD**

`queued` and `in_progress` are not success states. A failed run is retained as evidence and used to refine the next revision.

## Adoption rule

A skill may be copied from an external source for research, but repository adoption requires inspection plus a successful deterministic quality-lane run. External source reputation or package presence is not evidence of runtime safety or task effectiveness.
