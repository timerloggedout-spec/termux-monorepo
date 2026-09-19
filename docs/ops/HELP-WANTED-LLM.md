# Help-wanted + models (honest split)

## What runs without an LLM today

| Step | Engine |
|------|--------|
| Scout / claim / open stake PR / followup poll / status refresh | Deterministic Python + OPERATOR PAT on GHA |

That is why “no models did foreign PRs” was true: the lane optimized for **reliable write access**, not model quality.

## Where models should plug in (next maximize)

| Gap | Model path |
|-----|------------|
| Turn stake → real patch | `model_router` + OpenRouter free / Gemini after claim, before contribute |
| Address CHANGES_REQUESTED | followup queues revise job that invokes router with review body + file context |
| CPPH text understanding | optional ranking assist |

Free-tier rules still apply (`docs/ops/ROUTING-ORCHESTRATION-MAP.md`): exhaustion → OpenRouter `:free` only.

**Do not** block claim/PR machinery on model quota.

Agent-Identity: Grok (Administrator)
