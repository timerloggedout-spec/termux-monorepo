# AI Studio mesh trigger — quota-aware, both legs

[MUSEai]@{role:{google-ai-studio}}

Owner ruling (2026-10-30): **"Both is actual mesh."** The trigger
that runs AI Studio Delphi rounds = BOTH legs together; neither leg
alone is the mesh. Design context: `docs/ops/RECEIVER-MESH.md`
(PR #2345); first panel + full spec:
`docs/proposals/passes/ai-studio-delphi-panel/PASS.md` (PR #2485).

## Leg 1 — Receiver Mesh → Actions (quota gate)

`webhook → Cloudflare Worker (HMAC, D1 dedupe, Queue hold) →
repository_dispatch [ai-studio-delphi-round] →`
`.github/workflows/ai-studio-delphi-trigger.yml`

The workflow validates the envelope
(`trigger-envelope.example.json`, schema `ai-studio-delphi-round/v1`)
and runs `ops/ai-studio-mesh/quota_gate.py check <model>
ops/ai-studio-mesh/ledger.jsonl`:

- **ALLOW** (exit 0): the round is released to leg 2.
- **DEFER** (exit 3): fail-soft — the envelope stays in the mesh
  Queue/D1 hold and drains after the model's daily budget
  replenishes (smooth-flow: pace to the replenishment rate, never
  burst past it). Paid-labelled and budget-unverified models always
  DEFER (see the gate's tables; budgets are verified facts from the
  2026-10-30 rate-limit inspection, unknown is not unlimited).

## Leg 2 — VM bounded execution

Executes where the owner's AI Studio browser session lives (this
VM), one trigger class only: `ai-studio-delphi-round`. Per released
envelope: re-check the gate locally, run the panel in the AI Studio
Playground UI (no API key selected, no billing), append one ledger
row per completed run (`{"ts","model"}` JSONL), and land the ballots
by PR with `[MUSEai]@{role:{google-ai-studio}}` attribution.

Execution-adapter seam: the browser route is the current adapter.
**ChapitoAI[extended] (#1801, `multi-ai-cli/vendors/Chapito` —
browser-automation → local-proxy template wrapping AI Studio) is in
flight**; when its AI Studio adapter lands, leg 2 swaps browser →
Chapito behind this same envelope + gate contract, no contract
change. (Owner note, 2026-10-30: chats recently spooled to Web
investigate run on the browser-route workaround until then.)

## Ledger

`ops/ai-studio-mesh/ledger.jsonl` — append-only, one row per
completed panel run. Seeded with the 2026-10-30 first panel
(2 runs). The gate counts only rows from the current UTC day.
