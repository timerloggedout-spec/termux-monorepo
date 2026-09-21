# Paper2Agent — Paper → Agent Implementation Pattern

**Seed paper / post:** [Toward Recursive Self-Improvement: How GLM Built Its Own Inference Infrastructure](https://z.ai/blog/glm-built-its-inference-infrastructure) (2026-09-17)
**Role in monorepo:** Template for turning research into attributable agent loops (not a clone of GLM infra).

---

## 1. Core claim (from GLM)

End-to-end metrics alone are **sparse feedback**. Agents need **dense feedback**:

1. **Local** — tied to kernel / path / change / input shape
2. **Cheap & timely** — microbench / unit / kernel test before full deploy
3. **Objectively verifiable** — reference impl + controlled experiments

Loop: engineers set objectives & boundaries → agent hypothesizes & patches → environment returns layered feedback → dual-gate style promote only when local + end-to-end agree.

---

## 2. Mapping to termux-monorepo

| GLM dense-feedback idea | Our surface |
|-------------------------|-------------|
| Correctness feedback | dual-gate checks, submodule_integrity, inventory `--strict` |
| System behavior feedback | engineering_health, OTEL/spanmetrics, adaptive-wait |
| Performance feedback | model_performance_index, free-catalog lag, Codespace smoke |
| Infra Agent | Codespace agent lane + help-wanted LLM assist + evidence-led |
| Human holds objectives/risk | dual-gate hold matrix; no auto-merge without green |
| RSI horizon | continuous eval of refTemplates + research agents — not autonomous self-train |

---

## 3. Paper2Agent process (operational)

```text
Paper / post (17_Papers citation)
    → extract method + claims + code links (PapersFlow / HF Papers / OpenAlex)
    → slot under 15_Research or pattern note under CONTINUOUS-EVAL
    → define local checks (unit / inventory / integrity)
    → agent implements thin adapter (no secret hardcode)
    → dual-gate + evidence receipt
    → promote or hold with attributable reason
```

**Needle 3** (https://cactuscompute.com/needle) is a parallel seed for **resource-constrained** agent runtimes (8–29 MB, on-device tool call + extraction) → `01_Agent_Runtime` evaluation candidate.

---

## 4. Non-goals

- Full recursive self-improvement without human objective lock
- Claiming GLM numbers as our metrics
- Secret-heavy research agents outside credential-router

**Agent-Identity:** Grok (Administrator) CXO
