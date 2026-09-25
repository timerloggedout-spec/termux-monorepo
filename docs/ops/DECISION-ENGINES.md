# Decision Engines (not LLM providers)

**SSOT registry:** `scripts/decision_engines.py`

LLM routing stays in `provider_model_catalog` / `model_router` / OpenRouter free catalog.

Decision engines are **System-1 schema decision** tools used **before** expensive LLM invokes.

## Laya (IMPLEMENTATION)

| Surface | URL |
|---------|-----|
| Code | https://github.com/NandhaKishorM/laya |
| Demo | https://huggingface.co/spaces/convaiinnovations/laya-demo |
| Weights | https://huggingface.co/convaiinnovations/laya |
| Product | https://laya.convaiinnovations.com |

- Primitives: `choice`, `score`, `noul`
- Stub (CI): `scripts/laya_decision_stub.py`
- Slot: `refTemplates/16_Org_Phased/laya/`

### Workflow roles

1. Pre-LLM triage (department / urgency / churn)
2. Guardrail noul before agent tool use
3. Model/tool route **choice** (cheap gate)
4. help-wanted urgency **score**

Dense feedback required: checkpoint, confidence, `routing.reason`, latency budget — never binary "routed".

```bash
python3 scripts/decision_engines.py --list
python3 scripts/laya_decision_stub.py          # mock
python3 scripts/laya_decision_stub.py --live   # needs pip install laya
```
