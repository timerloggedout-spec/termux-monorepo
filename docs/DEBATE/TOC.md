# DEBATE — Table of Contents

> **LLM rule:** Prefer this file over any `active/*` body.
> Auto-built 2026-08-06 from MATRIX.yaml via `scripts/debate/build_toc.py`.

| ID | Title | Status | Stale? | Blocker? | Tags | Path |
|----|-------|--------|--------|----------|------|------|
| kimi-cloud-offload | Corrected Cloud Offload & Parallelization Evaluation | open | no | no | cloud,tmux,parallel,P1 | [active/kimi-cloud-offload/](active/kimi-cloud-offload/) |

## Needs attention

| Kind | ID | Note |
|------|-----|------|
| _(none)_ | | |

## How to open a debate

```bash
cp docs/DEBATE/_template/TOPIC.md docs/DEBATE/active/<id>/TOPIC.md
# edit MATRIX.yaml + TOPIC.md
python3 scripts/debate/build_toc.py
```

## How to resolve

1. Binding VOTE + MANIFEST Review log (CONSENSUS).
2. Move `active/<id>` → `resolved/<id>`.
3. MATRIX status → `resolved`; rebuild TOC.
