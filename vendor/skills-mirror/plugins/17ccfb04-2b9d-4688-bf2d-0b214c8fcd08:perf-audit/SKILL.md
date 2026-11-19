---
description: Scan a project for known performance anti-patterns (N+1 queries, hot-path blockers, memory hazards) and surface the right framework-specific profiler invocation. Implements the `performance_optimization` body-hint contract. Run before optimising — measure first, then act.
argument-hint: "--project <dir> [--severity info|warning] [--json] [--strict]"
allowed-tools: Bash
destructive: false
read-only: true
---

Scan + report:

!`python "${CLAUDE_PLUGIN_ROOT}/skills/one-shot-generator/scripts/perf_audit.py" $ARGUMENTS`

## What it detects

**Warning severity** (likely production hazard):
- `n_plus_one_django` — QuerySet inside a for-loop without prefetch/select_related
- `n_plus_one_sqlalchemy` — Query inside a for-loop without joinedload/selectinload
- `n_plus_one_sequelize` — findAll/findOne inside a for-loop without `include`
- `bcrypt_sync_in_hot_path` — synchronous bcrypt blocks event loop / GIL
- `sync_http_in_async` — requests/urllib inside async function

**Info severity** (style smells worth addressing):
- `select_star_raw_sql` — SELECT * forces planner to fetch every column
- `unbounded_file_read` — `.read()` with no size cap
- `len_on_queryset` — `len()` materialises rows; use `.count()`

## Output

Plus the **right profiler for your framework**:

| Framework | Tools surfaced |
|---|---|
| FastAPI | py-spy, scalene, EXPLAIN ANALYZE |
| Django | django-silk, django-debug-toolbar, py-spy |
| Spring Boot | JMH, Micrometer + Actuator, async-profiler |
| NestJS | clinic.js, autocannon, @nestjs/terminus |
| Go | pprof, `go test -bench` |
| Node.js | clinic.js flame, autocannon, --inspect |

## Examples

```bash
/perf-audit --project .                          # show everything
/perf-audit --project . --severity warning       # only the dangerous ones
/perf-audit --project . --json                   # for CI / piping
/perf-audit --project . --strict                 # exit 2 if any warnings (CI gate)
```

## When to run

- **Before optimising anything** — confirms the bottleneck isn't a known anti-pattern your eyes missed
- **In CI on the main branch** — `--strict` prevents new warnings landing
- **Right before `/ship-check`** — catches perf issues at the same gate as security / migrations
