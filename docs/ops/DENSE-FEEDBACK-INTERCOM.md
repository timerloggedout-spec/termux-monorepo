# Dense Feedback Intercom

**Status:** ACTIVE system pattern (not Paper2Agent-only)  
**Seed:** [GLM inference infrastructure / dense feedback](https://z.ai/blog/glm-built-its-inference-infrastructure)  
**Related:** `PAPER2AGENT.md` (one application) · dual-gate · evidence-led · adaptive-wait · OTEL · help-wanted · refTemplates continuous eval

---

## 1. Principle

Sparse end-to-end metrics (“throughput down 20%”, “check failed”) are not enough for agents or operators. Feedback must be:

1. **Local** — tied to path, job, kernel, slot, or change  
2. **Cheap & timely** — answer before a full redeploy when possible  
3. **Objectively verifiable** — reference, test, or controlled comparison  

This is the **intercom**: every major process should emit and consume dense signals so the next action is attributable.

---

## 2. Surface map (expand continuously)

| Process | Sparse (avoid-only) | Dense intercom |
|---------|---------------------|----------------|
| Dual-gate | red/green | which check, which path, log excerpt, hold reason |
| evidence-led | “receipt written” | inventory diff, SOURCE miss, smods vs .gitmodules |
| help-wanted | claim/PR exists | follow-up state, CHANGES_REQUESTED poll, tribute |
| adaptive-wait | timer fired | gate state + disjoint work progressed |
| OTEL / spanmetrics | alert fired | peer, span, sample density, contact point |
| credential-router | key missing | which env alias, free-catalog filter result |
| refTemplates score | tier letter | L0–L6 layer vector + ELO + commit-slice flags |
| Paper2Agent | “implemented paper” | local check set + dual-gate + evidence id |
| MCP / Vercel deploy | 403 | which secret empty, which project id |
| Codespace agent lane | smoke fail | which postCreate / which tool missing |

**Rule:** when adding a new lane, document its dense intercom row here or in that lane’s ops doc.

---

## 3. Laya — elevated priority

| Item | Value |
|------|-------|
| Surface | https://laya.convaiinnovations.com |
| Priority | **HIGH** — integrate early in Org/research watch + agent runtime eval |
| Slot path | `refTemplates/16_Org_Phased/laya/` (phase 1 metadata) + watch in `17_Papers` |
| Why | Operator-directed priority integration; complements dense-feedback / agent workspace research |
| Gate | Phase metadata now; live pin only after dual-gate + score |

Also watch: TypeSafe System One / JEV waitlist (email) — do not block Laya on it.

---

## 4. Expansion ownership

- **Paper2Agent** remains the paper→agent application of this pattern.  
- **Dense Feedback Intercom** is the cross-cutting SSOT for process feedback quality.  
- Continuous eval (refTemplates), dual-gate holds, and help-wanted follow-up must prefer dense reasons over binary flags in operator-facing reports.

**Agent-Identity:** Grok (Administrator) CXO  
