# Gource / Core — Agentic Replay & Process Refinement Lane

**Session**: 2026-09-21
**Agent-Identity**: Grok (Administrator)
**Skills**: adaptive-wait + evidence-led-monorepo-ops
**Mode**: BIUDL — dual-gate before promote, extract not mega, no YOLO

## Intent
Use the Gource/Core *event model* and SeekLog semantics to improve recursive ops:
- Replay evaluations of dual-gate, help-wanted, Stepie, catalog, and evidence trajectories
- Agentic refinement loops (critique → policy delta → new evidence)
- Not the OpenGL visualization plane (parked)

## Delivered in this extract package

| Path | What |
|------|------|
| `docs/ops/OPS-EVENT-GOURCE.schema.json` | Ops Event IR (Gource-compatible + monorepo bridges) |
| `scripts/ops/ops_event_seeklog.py` | SeekLog-compatible reader/writer (stdlib) |
| `tests/ops/test_ops_event_seeklog.py` | Unit tests |
| `docs/ops/GOURCE-CORE-FEATURE-AUDIT.md` | Core_fork-Gource feature map |
| `docs/ops/GOURCE-GITLINK-AND-EVAL.md` | Gitlink rules + full Gource decision |

## Mapping to existing SSOT
- Bridges `ACTION-EFFECT-EVENT.schema.json` and `EVIDENCE-ENVELOPE.schema.json`
- Colour / path / actor encode LANE-MATRIX lane, gate result, confidence
- Emit classic Gource custom log for optional human visual checks later

## Fork inventory
- `timerloggedout-spec/Core_fork-Gource` → OBSERVE (reference)
- Full `acaudwell/Gource` → no fork this window
- Native gitlink → only if Python SeekLog proves insufficient (dual-gate required)

## Next (stay busy under adaptive-wait)
1. Land this package as a thin feature-branch PR under dual-gate.
2. Wire one historical trajectory (help-wanted or dual-gate HOLD) through SeekLog → offline critique sketch.
3. Optional: LANE-MATRIX row + Stepie 2087 note.
4. Do **not** merge #523 mega or add C++ build until justified.

Refs: #175, #523 Evaluations, Stepie goal 2087, Core_fork-Gource, adaptive-wait, evidence-led-monorepo-ops.
