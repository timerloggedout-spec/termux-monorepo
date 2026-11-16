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
| Correctness feedback | dual-gate checks, submodule_integrity, inventory strict |
| System behavior feedback | engineering_health, OTEL/spanmetrics, adaptive-wait |
| Performance feedback | model_performance_index, free-catalog lag, Codespace smoke |
| Infra Agent | Codespace agent lane + help-wanted LLM assist + evidence-led |
| Human holds objectives/risk | dual-gate hold matrix; no auto-merge without green |
| RSI horizon | continuous eval of refTemplates + research agents — not autonomous self-train |

---

## 3. Paper2Agent process (operational)

Paper / post (17_Papers citation)
    → extract method + claims + code links
    → slot under 15_Research or pattern note under CONTINUOUS-EVAL
    → define local checks
    → agent implements thin adapter (no secret hardcode)
    → dual-gate + evidence receipt
    → promote or hold with attributable reason

Needle 3 is a parallel seed for resource-constrained agent runtimes → 01_Agent_Runtime evaluation candidate.

---

## 4. AlphaEvolve + Dream-RSI extension

The repo now adds a bounded **evolutionary replay** layer at scripts/agent_evolution/replay_simulator.py and documents it in docs/ops/EVOLUTIONARY-REPLAY.md.

The integration adopts two research mechanisms:

- **Evaluator-first evolution:** AlphaEvolve combines program proposals with automated evaluation and evolutionary selection. Here, the evaluator is an explicit experiment contract; it is not allowed to become an implicit model-quality score.
- **History-as-simulator:** Dream-RSI replays alternative exploration policies against realized discovery trees, avoiding repeated online executions for the offline policy-selection phase. Here, replay is deterministic and read-only over recorded outcomes.

The incumbent policy remains in every candidate set. This provides a replay-level non-regression invariant while preserving the existing online dual gate. A replay improvement is therefore **candidate evidence**, not production proof.

The resulting extended process is:

research source
    → method extraction
    → thin replay/evaluator adapter
    → local dense feedback
    → replay cohort / incumbent control
    → bounded policy evolution
    → fresh online cohort
    → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE
    → dual gate
    → promote / hold
    → append new discovery history

External references:
- AlphaEvolve: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- Dream-RSI paper: https://arxiv.org/abs/2609.14858
- Dream-RSI report/demo: https://dream-rsi.com/

---

## 5. Non-goals

- Full recursive self-improvement without human objective lock
- Claiming GLM, AlphaEvolve, or Dream-RSI numbers as our metrics
- Secret-heavy research agents outside credential-router
- Executing generated source code inside the replay simulator
- Treating replay score as correctness or as an intelligence ranking

**Agent-Identity:** Grok (Administrator) CXO
