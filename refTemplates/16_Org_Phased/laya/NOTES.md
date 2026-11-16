# Laya — implementation notes

**Canonical code:** https://github.com/NandhaKishorM/laya  
**Site:** https://laya.convaiinnovations.com  
**HF hub:** https://huggingface.co/convaiinnovations/laya  
**Stars (sampled):** ~3907 · Python · default `main`

## Repo layout (upstream)

- `laya/` — package (Router, load, primitives)
- `tests/` — unit coverage
- `research/` — benchmark harnesses
- `notebooks/` — demos
- `BENCHMARKS.md` — consolidated report
- `pyproject.toml` / `setup.py` — install as `laya`

## Primitives

| Type | Output |
|------|--------|
| `choice` | label + distribution + confidence |
| `score` | ordinal expected level + distribution |
| `noul` | calibrated P(true) |

## Checkpoints

| Key | Backbone | Use |
|-----|----------|-----|
| english (`laya`) | ModernBERT-large | EN |
| multilingual | mmBERT-base | 100+ languages |
| typed-decisions | ModernBERT-large | agent/CS/security workflows |

`Router(preload=True)` for production; script detect before forward pass (confidence alone fails cross-script).

## Research

- arXiv:2503.23303
- arXiv:2510.01237

## Monorepo mapping

| Lane | Use |
|------|-----|
| help-wanted / triage | `laya.triage_questions()` shape |
| guardrails | `laya.guard_questions()` before LLM |
| tool/model routing | `laya.router_questions()` |
| dense intercom | calibrated confidence gates |
| Codespace / Termux | mock stub in CI; live only when package+weights available |

## Adapter

`scripts/laya_decision_stub.py` — mock by default; `--live` requires installed `laya`.
