# Gitlink + Full Gource Evaluation

## D — Core_fork-Gource gitlink proposal

**Candidate path**: `third_party/Core_fork-Gource` or `vendor/acaudwell-Core` (gitlink).
**Source**: `https://github.com/timerloggedout-spec/Core_fork-Gource.git`
**When**: Only after dual-gate green on a thin PR that *needs* native SeekLog or related primitives.
**Default**: **Do not gitlink yet**. Python port covers the agentic surface.

Promote rule (adaptive-wait):
- Dual-gate (hygiene + portability + agentic termux smoke) SUCCESS
- Extract size, not mega
- Document why C++ is required over the Python SeekLog
- GPL-3 compliance note in the PR

## C — Full Gource evaluation

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| Fork full `acaudwell/Gource` | Own the custom-log emitters, captions, filters | Build deps (SDL2, Boost, GLEW, GLM…), OpenGL runtime | **Defer**. Not needed for agentic replay. |
| Use system/Docker Gource as black-box | Zero maintenance, already understands custom logs | External binary | Acceptable optional tool for human visual checks later |
| WASM (Posnet/gource-web) | Browser | Visualization Plane | Parked |

**Decision**: No full Gource fork in this window. Emit Gource-compatible custom logs from Python; consume only if an operator explicitly wants a visual replay.

## Placement in monorepo (EXTRACT)

Suggested thin extract (this package → feature branch):

```
docs/ops/OPS-EVENT-GOURCE.schema.json
docs/ops/GOURCE-CORE-AGENTIC.md
scripts/ops/ops_event_seeklog.py
tests/ops/test_ops_event_seeklog.py
```

Bridge points already in-repo:
- `docs/ops/ACTION-EFFECT-EVENT.schema.json`
- `docs/ops/EVIDENCE-ENVELOPE.schema.json`
- help-wanted evidence JSONL
- dual-gate / LANE-MATRIX SHAs

## LANE-MATRIX row (proposed)

| PR / lane | Status | Why |
|-----------|--------|-----|
| gource-core-agentic (this) | EXTRACT candidate | Seekable ops event IR + Python SeekLog for replay evaluations; Core_fork OBSERVE; no viz |

Refs: #175 hub, #523 Evaluations surface, Stepie 2087, adaptive-wait, evidence-led-monorepo-ops.
