# Decision Engines — Selection & Quality Criteria Matrix (Comparative)

**SSOT intent:** comparative only. No primary. Latency is **low-value MoneyBall** (already established); quality, calibration, evidence density, and workflow fit dominate.

**RECON base (2026-09-23):**
- logicrw/awesome-jev-projects — 595 commit-pinned projects, 17 architecture categories
- Reddit r/LLMDevs “287 → top 20” (Canny = evidence-backed done gate)
- Open peers: Laya (encoder family), Kev (0.8B/4B/9B Qwen LoRA), hosted Jev reference
- Ports/ONNX/CoreML/GGUF, Lex/Kai/Nox specialists

Live radar: https://logicrw.github.io/awesome-jev-projects/en/
Catalog JSON: https://logicrw.github.io/awesome-jev-projects/projects.json

---

## 1. Quality dimensions (high value)

| Dimension | Why it matters | Measurement / evidence | Low → High notes |
|-----------|----------------|------------------------|------------------|
| **Calibration** | Probabilities must be usable as thresholds | ECE, Brier, temperature fit on hold-out; confident-error rate | Raw logits overconfident OOD; per-type or global T required |
| **Locked-suite accuracy** | Avoid marketing numbers | Same frozen items, commit-pinned harness, once-per-candidate locked test | Prefer reported locked test over “dev” only |
| **Option cardinality** | Choice >20 options degrades many open models | Banking77 / 50+ option stress | Hosted Jev stronger; open models need hierarchy or coarse→fine |
| **Zero-shot honesty** | Base vs fine-tuned | Explicit base ≈ random on typed-decisions for Laya family | Treat as foundation + fine-tune, not omniscient |
| **Multi-lang / script** | English-only traps | MASSIVE / non-Latin scripts; Router presence | Laya multilingual + Router; Kev English-first |
| **Fail-open vs hard-block** | Agent safety | Facts → code; judgments → engine (Canny rule) | Engine advises; only facts hard-block |
| **Evidence density** | Trust | Commit-pinned source of decision point; claimStatus reviewed | Prefer logicrw-style pinned evidence |
| **Wire compatibility** | Interchange | System One `/v1/systemone` shape | Kev serves it; Laya can; Canny points at any compatible |
| **Self-host / sovereignty** | Cost + data | Apache weights + local serve | Laya / Kev open; Jev hosted only |
| **Cost per decision** | Volume | $/decision or free self-host | Open wins at scale; hosted for peak accuracy |
| **Domain specialization** | Workflow fit | Invoice / SOC / agent-trace / coding-agent / browser | Fine-tuned checkpoints or specialist (Lex etc.) |
| **Dense feedback** | Ops observability | checkpoint + confidence + routing.reason + latency_budget | Never binary “routed” |

**Latency** remains secondary: useful for HF loops and games, not the ranking axis for monorepo quality gates.

---

## 2. Engine comparison matrix (comparative)

| Engine / family | Host | License | Backbone | Primitives | Calibration notes | Cardinality | Multi-lang | Self-host | Best-fit workflows |
|-----------------|------|---------|----------|------------|-------------------|-------------|------------|-----------|--------------------|
| **Laya** (en / ml / typed-decisions) | Self | Apache-2.0 | ModernBERT / mmBERT 322–421M | choice / score / noul | Strong post-temp ECE claims; base near-random zero-shot | Weak >20 opts | Strong (Router + 100+) | Yes | Pre-LLM triage, guardrails, multi-lang, CI offline |
| **Kev** 0.8B / 4B / 9B | Self | Apache adapter+head (Qwen base) | Qwen3.5 + LoRA + pointer | System One wire | Built-in T; strong OOD locked on 9B | Better than pure encoder on many suites | English-first | Yes (serve) | Coding-agent routes, local System One drop-in, train-your-own |
| **Jev** (hosted) | TypeSafe API | Closed | Proprietary | choice / score / noul | Published strong; third-party benches mixed | Stronger high-cardinality | Limited public matrix | No | Peak accuracy / long state when budget allows |
| **Canny pattern** | Any compatible | MIT (qkal/Canny) | N/A (policy + noul) | noul (advice) | N/A — deterministic facts | N/A | N/A | Yes | Dual-gate “done” evidence, adaptive-wait completion |
| Lex / Kai / Nox | Self | Apache | ~0.6B+ | same | Specialist claims | Task-specific | Varies | Yes | Operational workflows (invoice / SOC / CS) |
| Ports (ONNX / CoreML / GGUF / LiteRT) | Edge | Apache | Laya-derived | same | Match publisher within ε | Same limits | Same | Yes | Phone / browser / edge |

No ranking as “primary”. Selection is criteria-driven.

---

## 3. Workflow → criteria mapping (monorepo cadence)

| Workflow / cadence | High-value criteria | Suggested comparative set | Notes |
|--------------------|---------------------|---------------------------|-------|
| Pre-LLM triage (dept / urgency / churn) | Calibration, dense feedback, self-host | Laya (typed or en) vs Kev-4B | Offline stub mandatory |
| Guardrail / jailbreak noul | Fail-open, evidence density | Laya noul + Canny-style policy | Facts block; engine advises |
| Model / tool route choice | Wire compat, cost, locked accuracy | Kev or Laya vs hosted Jev when free_only=false | Feed model_router |
| Help-wanted urgency score | Score primitive, multi-lang | Laya multilingual | Score weakest primitive for many engines |
| Dual-gate / adaptive-wait “done” | Canny rule (facts only hard-block) | Canny pattern + any noul engine | Ledger append-only |
| Context GC / compaction | Keep/drop without rewrite | Pattern from fast-jev-compaction | Engine scores relevance; code keeps text |
| PR / code-review stage | Staged scores + evidence | Jev-Review style + Canny | Never YOLO |
| High-frequency / games | Latency secondary; determinism | Kev small or Laya | Local only preferred |
| Browser / computer-use action | Choice over candidates | jev-ultrafast pattern | Separate generation |

---

## 4. Selection function (sketch)

```text
select(engines, {
  free_only: true|false,
  self_host_required: true|false,
  lang: "en"|"multi"|...,
  max_options: N,
  domain: "triage"|"guardrail"|"route"|"done"|"score"|...,
  min_locked_acc: float|null,
  require_dense_feedback: true,
  allow_hosted: false  # default under free-first policy
}) → ranked list with reason strings
```

Dense feedback required on every return: `engine_id`, `checkpoint`, `confidence`, `routing.reason`, `criteria_matched[]`.

---

## 5. Awesome radar categories (logicrw) → monorepo affinity

| Category (logicrw count) | Affinity | Cherry-pick patterns |
|--------------------------|----------|----------------------|
| Security & Guardrails (~45) | High | Canny, jev-guard, actiongate |
| Model Routing (~40) | High | Codex router, LiteLLM Jev, complexity class |
| Context GC (~31) | High | fast-jev-compaction, Winnow |
| MCP & Integrations (~32) | High | typesafe-mcp, jev-mcp |
| Evaluation & Observability (~29) | High | Dual-gate evidence receipts |
| Browser & OS Action (~39) | Medium | jev-ultrafast, cua |
| CLI & Pipelines (~34) | High | SemDecide |
| SDK & Decision Frameworks (~97) | Medium | Wire-compat clients |
| High-Frequency / Games (~41) | Low (latency secondary) | Kev demos |
| Domain Tools (~41) | Medium | Invoice / SOC specialists |

---

## 6. Implementation status

- Registry: comparative Laya + Kev family + Jev reference + Canny pattern
- `scripts/canny_completion_gate.py` production stub for dual-gate / adaptive-wait
- Dual-gate before promote; no YOLO / YEET / AUTOAPPROVE
