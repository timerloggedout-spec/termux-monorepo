# Decision Engines (comparative — not LLM providers)

**SSOT registry:** `scripts/decision_engines.py`  
**Quality matrix:** `docs/ops/DECISION-CRITERIA-MATRIX.md`

LLM routing stays in `provider_model_catalog` / `model_router` / OpenRouter free catalog.

Decision engines are **System-1 schema decision** tools used **before** expensive LLM invokes, for guardrails, routing, and completion evidence.

**Policy:** comparative only. **No primary.** Latency is low-value MoneyBall.

## Engines (phase tags)

| ID | Family | Phase | Host | Notes |
|----|--------|-------|------|-------|
| laya | laya | COMPARATIVE | self | Encoder family; multi-lang Router; typed-decisions checkpoint |
| kev-0.8b / kev-4b / kev-9b | kev | COMPARATIVE | self | Qwen3.5 + LoRA + pointer; System One wire; train/serve |
| jev | jev | REFERENCE | hosted | TypeSafe; never default under free-first |
| canny_pattern | policy | PATTERN | self | Facts hard-block; noul only advises (Reddit top-20 #19) |

## Commands

```bash
python3 scripts/decision_engines.py --matrix
python3 scripts/decision_engines.py --list
python3 scripts/decision_engines.py --id kev-4b
python3 scripts/decision_engines.py --select --lang multi --domain triage
python3 scripts/decision_engines.py --select --self-host --domain done
python3 scripts/laya_decision_stub.py          # mock
python3 scripts/laya_decision_stub.py --live   # needs pip install laya
python3 scripts/canny_completion_gate.py
python3 scripts/canny_completion_gate.py --demo-block
```

## Dense feedback contract

Every decision return must include (where applicable):

- `engine_id` / `checkpoint`
- `confidence`
- `routing.reason` (or `criteria_matched`)
- optional `latency_budget_ms` (informational only)

Never binary “routed” / “done” without evidence.

## RECON receipts

- logicrw/awesome-jev-projects (595+ commit-pinned, 17 categories) — radar + projects.json  
- Reddit r/LLMDevs 287→20 (Canny #19)  
- Laya HF + product; Kev HF + github.com/jaredpalmer/kev; TypeSafe docs  

See `DECISION-CRITERIA-MATRIX.md` for full quality dimensions and workflow mapping.

## Cadence rules

- Dual-gate before promote.  
- AVOID HITL YOLO YEET AUTOAPPROVE.  
- adaptive-wait on completion evidence (Canny-style).  
- Free-first: hosted Jev only when explicitly allowed.
