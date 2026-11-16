# Pass record — ai-studio-delphi-panel (first live AI Studio Delphi panel)

[MUSEai]@{role:{google-ai-studio}}

**Run:** 2026-10-30 03:08–03:12 PT · **Surface:** Google AI Studio
Playground UI (`aistudio.google.com`), signed in as the owner account,
`No API key selected` throughout — UI-free use, ∅ key creation,
∅ billing setup · **Contributor moniker:** `geminiMesh`
(AGENT-MONIKERS.md, non-callable display) · **Target brief:**
#1802 google-ai-studio · **Method:** Delphi — 2 independent panelists,
identical brief, no cross-read; synthesis = this file.

## Panelists (MODEL_PROVIDER ballots)

| Panel | Model | Tokens shown | Record |
|---|---|---|---|
| A | `gemini-3.1-pro-preview` | 3,798 | `panel-a-gemini-3.1-pro-preview.md` |
| B | `gemini-3.8-flash` | 3,377 | `panel-b-gemini-3.8-flash.md` |

Brief ∧ evidence base (account inspection 2026-10-30, this lane):
37 picker models, 14 Preview-labelled; `gemini-3.8-flash` free-tier
5 RPM / 250K TPM / 20 RPD; Paid previews (Deep Research ×2,
Antigravity, `gemini-3-flash-preview`, Lyria ×2) billing-gated;
Deep Research Pro ∧ Computer Use previews = rate-limit page only,
0/0. Full stamped items: `evidence.json`.

## Convergence

- **Adopt ∈ consensus.** A: adopt outright. B: adopt conditionally,
  provisional sandbox, preview votes zero-weighted until calibrated
  (B proposed ≥15 rounds). **Synthesis ruling: adopt provisional** —
  B governs weighting, A∧B govern selection.
- **#1 panelist ∈ consensus:** `gemini-3.1-pro-preview` (both panels,
  ranked first). Mean scores (A∧B): evidence 8.5 / cost 10 /
  composability 8.5.
- **Divergent picks:** A ↦ `gemini-3.1-flash-live-preview` (8/10/7) ∧
  `gemini-robotics-er-2-preview` (7/10/6) as orthogonal panelists.
  B ↦ `deep-research-preview-04-2026` (evidence 10, cost 2, gated) ∧
  `gemini-3.8-flash` as baseline anchor / drift control (7/9/10).
- **Deep Research → Delphi routing ∈ full consensus:** gated Delphi
  RFP per round + free substitute default (`gemini-3.1-pro-preview`
  + web search) + owner approval unlocks Paid per round with spend
  limits. No standing Paid route.
- **Risks ∈ consensus:** (1) silent preview deprecation ⇒ pin exact
  model IDs in ballots, fallback ↦ `gemini-3.8-flash`;
  (2) free-tier rate exhaustion (20 RPD class) ⇒ async queue /
  token-bucket pacing, cross-provider failover;
  (3) output/weight distortion ⇒ schema validation ∧ provisional
  zero-weighting until calibration.

## Quota-aware trigger — mesh ruling (owner, 2026-10-30)

Owner: "Both is actual mesh." The trigger that runs future rounds of
this panel = BOTH legs, neither alone:

1. **Receiver Mesh leg** (docs/ops/RECEIVER-MESH.md, PR #2345):
   webhook → Cloudflare Worker (HMAC, D1 dedupe, Queue hold) →
   `repository_dispatch` → Actions processor, quota gate inside
   (rate-limit pre-read, smooth-flow pacing, defer+hold on low
   bucket — QAC breaker pattern).
2. **VM bounded leg:** executes the AI Studio browser-session runs
   (the session lives on this VM), one trigger class only
   (ai-studio-delphi-round), quota-aware: checks the model's
   free-tier budget (e.g. 20 RPD class) before running, defers
   into the Queue hold when exhausted.

Panel corroboration: both ballots independently specified the same
gate shape (token-bucket ballot queue ∧ gated RFP ∧ fallback) —
recorded as Delphi evidence for the mesh design, not as its source;
the ruling is the owner's.

## Outcome

- AI Studio preview panelists **adopted provisional** into Delphi:
  primary `gemini-3.1-pro-preview`; anchor/control `gemini-3.8-flash`;
  next candidates `gemini-3.1-flash-live-preview`,
  `gemini-robotics-er-2-preview` (unweighted until calibration).
- Deep Research previews: **gated-RFP route only**, free substitute
  until owner approves a funded round.
- Follow-ons: mesh trigger implementation (both legs, above);
  calibration rounds counted from this pass (round 1 of 15).
