---
description: Run production-readiness gates against a project before --apply. Verifies tests pass, no secrets in diff, no unresolved TODOs, migration is reversible, env vars are documented, health endpoints exist, feature flags are wired, rollback path is present, canary plan is documented. Inspired by Addy Osmani's shipping-and-launch skill.
argument-hint: "--project <dir> [--strict]"
allowed-tools: Bash
destructive: true
read-only: false
---

Run the 10-gate production-readiness checklist:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/ship_gates.py" $ARGUMENTS`

## Verdict

- **READY** — all gates PASS or SKIP. Safe to `/one-shot --apply`.
- **READY_WITH_WARN** — at least one WARN. Safe to apply but the
  flagged items should be addressed within the same week (TODO debt,
  missing canary plan, etc.).
- **BLOCKED** — at least one FAIL. Do NOT apply until resolved.

## Gates (10 total)

**Code & Security**
- `tests_pass` — pytest exits 0
- `no_secrets_in_diff` — grep for AWS / Google / GitHub / Slack tokens + RSA keys
- `no_TODO_or_FIXME` — open TODOs in generated files signal incomplete scope
- `migration_reversible` — Alembic / Django migration has a real downgrade

**Infrastructure & Docs**
- `env_vars_documented` — `.env.example` exists, code references env reads
- `health_endpoint_exists` — `/livez`, `/readyz`, or `/healthz` route
- `openapi_doc_generated` — FastAPI / NestJS / springdoc detected

**Rollout Readiness**
- `feature_flag_present` — code references a flag library / function
- `rollback_path` — `.osp.bak` files from the wirer are in place
- `canary_plan` — `ROLLOUT.md` documents ramp percentages + halt conditions

## Strict mode

Pass `--strict` to promote WARN to FAIL — recommended for production
deploys; default is suitable for staging.

```bash
/ship-check --project . --strict
```
