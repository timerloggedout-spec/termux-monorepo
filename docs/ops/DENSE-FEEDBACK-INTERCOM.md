# Dense Feedback Intercom

**Status:** ACTIVE system pattern (not Paper2Agent-only)
**Seed:** [GLM inference infrastructure / dense feedback](https://z.ai/blog/glm-built-its-inference-infrastructure)
**Related:** `PAPER2AGENT.md` · dual-gate · evidence-led · adaptive-wait · OTEL · help-wanted · refTemplates continuous eval

---

## 1. Principle

Sparse end-to-end metrics are not enough. Feedback must be:

1. **Local** — tied to path, job, kernel, slot, or change
2. **Cheap & timely** — answer before a full redeploy when possible
3. **Objectively verifiable** — reference, test, or controlled comparison

---

## 2. Surface map

| Process | Sparse (avoid-only) | Dense intercom |
|---------|---------------------|----------------|
| Dual-gate | red/green | which check, which path, log excerpt, hold reason |
| evidence-led | “receipt written” | inventory diff, SOURCE miss, smods vs .gitmodules |
| help-wanted | claim/PR exists | follow-up state, CHANGES_REQUESTED poll, tribute |
| adaptive-wait | timer fired | gate state + disjoint work progressed |
| OTEL / spanmetrics | alert fired | peer, span, sample density |
| credential-router | key missing | which env alias, free-catalog filter |
| refTemplates score | tier letter | L0–L6 vector + ELO + commit-slice flags |
| Paper2Agent | “implemented paper” | local check set + dual-gate + evidence id |
| MCP / Vercel deploy | 403 | which secret empty, which project id |
| Codespace agent lane | smoke fail | which postCreate / tool missing |
| **Laya decisions** | “routed” | checkpoint, confidence, routing.reason, latency budget |

---

## 3. Laya — IMPLEMENTATION (canonical)

| Item | Value |
|------|-------|
| **Repo** | https://github.com/NandhaKishorM/laya |
| Product | https://laya.convaiinnovations.com |
| Priority | **HIGH** |
| Phase | **IMPLEMENTATION** |
| Slot | `refTemplates/16_Org_Phased/laya/` |
| Adapter | `scripts/laya_decision_stub.py` (mock CI / optional live) |

Calibrated confidence is a **dense** signal; never treat token-style fake confidence as gate.

---

## 4. Ownership

- Paper2Agent = paper→agent application of this pattern
- This doc = cross-cutting SSOT for feedback quality

**Agent-Identity:** Grok (Administrator) CXO
