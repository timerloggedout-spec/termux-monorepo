# Secret naming convention

**Status:** live announcement 2026-09-19 20:55 PDT  
**Owner:** Grok Administrator  
**Related:** #184 (use credentials; last-used), #175 (priority matrix), #337 (team MVT)

Do **not** paste secret values into issues, PR bodies, or skill files. Record names and routing only.

## Canonical names used by workflows

| Provider / purpose | Canonical Actions secret | Accepted aliases (resolver only) |
|---|---|---|
| Hugging Face Inference Providers | `HUGGINGFACE_TOKEN` | `HUGGING_FACE_HUB_TOKEN`, `HF_API_TOKEN` |
| Felo / OX Alpha | `FELO_AI_API` | none |
| OpenRouter | `OPENROUTER_API_KEY` | none |
| Omni | `OMNI_API_KEY` | none |
| Operator GitHub PAT | `OPERATOR_GITHUB_TOKEN` | `ARCHWIZ_GITHUB_TOKEN`, `GH_PAT` |

## Why aliases exist

Hugging Face Hub, Transformers, and Inference Providers historically used different env names. Workflows that read only one Hugging Face secret name can report `missing_secret` even when a valid token exists under another configured name. The resolver accepts the three existing names without requiring a synthetic fourth name.

## Rule for agents

1. Use the existing Hugging Face Actions secret names; do not invent or require an unconfigured fourth name.
2. Workflows may resolve aliases at runtime (see `scripts/provider_model_catalog.py`).
3. Prefer free/zero-price or documented trial routes. Felo 200/day credits are a quota, not a license to skip catalog refresh.
4. If a lane skips with `missing_secret`, check naming first — do not assume the token is absent.
5. Never write token values into git, issues, or dashboards.

## Verification (presence only)

- Actions → Secrets: confirm one of the existing Hugging Face secret names is present (`HUGGINGFACE_TOKEN`, `HUGGING_FACE_HUB_TOKEN`, or `HF_API_TOKEN`); last-used timestamp is the only status that belongs on #184.
- Team MVT lane `e-huggingface` should stop skipping for `missing_secret` once the canonical name or an alias is present in the job env.
