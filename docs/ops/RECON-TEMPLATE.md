# {TOPIC} RECON 🏅 — {one-line question} ({YYYY-MM-DD})

`[MUSEai]@{role:{lane-moniker}}` · Tasking: {owner/manager order, source chat or issue #, date} · Deliverable pattern: `docs/ops/RECON-TEMPLATE.md` (this template) · Exemplars: `docs/ops/QUOTA-ROUTES-RECON-2026-10-31.md` (PR #2859) · `docs/RECON.md` (2026-08-01 prototype)

**Date:** {YYYY-MM-DD} · **Recon window:** {start–end, TZ}
**Scope:** {what is in — surfaces, repos, accounts, time range} · {what is explicitly out}
**Rule of engagement:** firsthand evidence only — live API / landed content / primary records; expand existing docs, do not replace them; secret VALUES never read (names + last-used only); ∅ verdict from web-only absence — establishment = internal record first ∧ web second; re-read before claiming failure (mid-flight reads lie); writes stay on a `recon/*` ∨ task branch until reviewed.
**Sources:** {each source + how read: e.g. PAT API `GET /…`, `@master` blob, workflow run #, owner-UI census} · Rate/quota note: {bucket state if it bounded the recon}

**Question:** {the single question this recon answers, verbatim from tasking where possible}

---

## 1. Situation report

{State of the world as found, before analysis. Facts only — each row traceable to §2.}

| Fact | Detail |
|---|---|
| {surface / system} | {state @ recon time, w/ date} |
| {prior record} | {what the repo/docs already claimed, + where} |

## 2. Evidence

{Firsthand, claim→ref per #1734: every material claim carries its reference — blob SHA, PR #, run #, API route + response state, file:line. A claim without a ref does not ship.}

| # | Claim | Ref |
|---|---|---|
| E1 | {claim} | {`path` @blob `sha` / PR # / run # / `GET /route` → status} |
| E2 | {claim} | {ref} |

Negative evidence is evidence: record the probe, not just the result — `{route/query} → 404 / total_count 0 / ∅ hits`, with the exact slug/query tried.

## 3. Findings

{What the evidence shows, grouped. Separate observation from inference; label inference as inference. Counts are firsthand counts, never relayed numbers; a lane report is input, not evidence.}

- **F1 — {finding}:** {statement} (E1, E3)
- **F2 — {finding}:** {statement} (E2)

## 4. Verdicts

{One verdict per question/sub-question. Verdict vocabulary: `ESTABLISHED` · `VERIFIED` · `READY` · `BLOCKED {blocker}` · `NOT_ESTABLISHED` (§5) · `NEVER-EXISTED` (only w/ negative-evidence probes in §2).}

| Item | Verdict | Basis |
|---|---|---|
| {item} | {verdict} | {E# refs} |

## 5. NOT_ESTABLISHED register

{Everything material that could NOT be established, with why and the only route that could establish it. ∅ silent gaps — an unlisted unknown reads as a checked negative.}

| Item | Why not established | Establishing route |
|---|---|---|
| {item} | {no API route / owner-UI only / quota / access} | {exact surface or action} |

## 6. Proposals / next steps

{Each proposal: owner, cost/quota class, gating. A recon proposes; it does not execute beyond its tasking. End with the concrete next action, never homework for the reader.}

- **P1 — {proposal}:** {what + why} · Owner: {lane} · Gate: {none / owner word / quota window}
- **Next:** {single immediate step + who takes it}

---

*Filing: land as `docs/ops/{TOPIC}-RECON-{YYYY-MM-DD}.md` via PR; report = {PR # + merge SHA, oracle-verified: merge ∈ master history ∧ landed bytes == authored}. Stamp: `[MUSEai]@{role:{lane-moniker}}`.*
