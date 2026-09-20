# Laya — surface notes (IMPLEMENTATION)

**Site:** https://laya.convaiinnovations.com  
**Org:** ConvAI Innovations · Nandakishor Mukkunnoth  
**License posture:** Apache 2.0 open weights (per site)

## What it is

Sub-~35ms **System 1** decision engine: non-autoregressive, schema-typed outputs with **calibrated probabilities** (not free-text LLM confidences).

### Primitives

| Type | Role |
|------|------|
| `choice` | Pick one option + distribution + confidence |
| `score` | Ordinal rubric level + distribution |
| `noul` | Boolean P(true) calibrated |

### Checkpoints (HF hub `convaiinnovations/laya`)

| Id | Backbone | Strength |
|----|----------|----------|
| laya | ModernBERT-large ~421M | EN classification, guardrails, email |
| multilingual | mmBERT-base | 100+ languages |
| typed-decisions | ModernBERT-large | Agent observability, CS, security alerts |

Router: script/language detect before forward pass (confidence alone is unsafe cross-script).

### Research lineage

- arXiv:2503.23303 — sequence conversion trajectories / RL
- arXiv:2510.01237 — schema-based decisions + RL framework
- HF weights + datasets published; contrast narrative vs TypeSafe Jev (closed)

### Install (from site)

```text
pip install laya>=0.3.3
```

## Monorepo mapping

| Lane | Use |
|------|-----|
| Agent runtime / guardrails | Jailbreak / toxicity / route decisions in <40ms |
| help-wanted triage | Ticket queue choice + urgency score |
| credential / tool routing | noul gates before expensive LLM calls |
| dense intercom | Calibrated confidence as local signal (not token-confidence) |
| Termux / on-device | Prefer smaller multilingual path when hardware fits |

## Implementation next (I3+)

1. Thin adapter under `scripts/` or skill: `choice`/`score`/`noul` wrappers, **no secrets**.  
2. Unit test offline with mocked predict if HF download blocked in CI.  
3. Dual-gate any PR that adds runtime dep on `laya`.  
4. Cite arXiv ids in `17_Papers/citations/`.

**Dense rule:** never promote on “Laya integrated” binary — name checkpoint, latency budget, and failure mode (e.g. >20-way choice degradation).
