# QUE Report

One Report per executor turn that changes state. Stamp line first, machine block second.

`{live|degraded|down|blocked} {item} · verified receipt {PR, SHA, run} · owner action: {act ∨ none}`

<!-- que-report/v1
{
  "schema": "que-report/v1",
  "state": "progress",
  "summary": "{one line, plain words}",
  "receipt": ["{PR #, SHA, run id}"],
  "attention": null
}
-->

## state enum

| state | meaning | stamp |
| --- | --- | --- |
| progress | working, nothing needed | live |
| waiting | idle until a Trigger arrives | live |
| ready | result ready for review ∨ done | live |
| blocked | cannot continue without input | blocked |
| failed | tried ∧ failed; reported as failure | down |
| dropped | nothing to do (superseded, ¬ reproduces); ends silently | live |

## attention (one structured question, ∨ null)

```json
{"question": "{one concrete question}", "options": ["{a}", "{b}"], "default": "{a}", "owner": "LoggedOut Timer"}
```

Only this field counts toward the HITL rate. A question buried in `summary` does not count ∧ is a register violation.
