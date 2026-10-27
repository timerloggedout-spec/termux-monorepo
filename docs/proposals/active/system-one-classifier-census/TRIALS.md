# System One census — tranche-1 trial records (2026-10-27)

Executed under the owner's order "Get them in our comparisons!" with the
free_only gate standing. Every claim below is firsthand from this lane's
runs; run ids and outputs are quoted so anyone can re-check them.
Hosted/paid rows were NOT executed — they are listed at the end as the
blocked-paid list for an owner ruling (proposal item SC-004).

## T1-LAYA — Laya via self-hosted simple-jev: EVALUATED

- Route: `simple-jev` hf-server (featherless-ai/simple-jev, cloned
  2026-10-27) serving `convaiinnovations/laya`, subfolder
  `typed-decisions`, CPU, at http://127.0.0.1:8000 — the fleet's own
  dispatch (`deepcli.observatory.dispatch --decide-only`, PR #1810)
  called it over the TypeSafe-compatible `POST /v1/systemone`.
- Dispatch result (verbatim):
  `task=laya-local-trial decide_ok=True scores={'quality': 0.7139, 'grounding': 0.7692} supported=0.2505`
  The Noul "supported" score of 0.2505 is the model judging the trial
  state's own claim ("the trial completed successfully…") as weakly
  supported by evidence inside the state — a sensible skeptical read.
- Raw wire response (direct POST, same state, two questions):
  `{"model": "convaiinnovations/laya", "answers": {"quality": {"type": "score", "probabilities": {"0": 0.1338, "1": 0.8662}, "confidence": 0.8662, "score": 0.8662}, "supported": {"type": "noul", "noul": 0.2924}}, "usage": {"input_tokens": 116, "output_tokens": 0}}`
  (Score differs from the dispatch run because decide_check words the
  rubric instructions differently; both are genuine Laya outputs.)
- Serving notes (reproducibility): torch must come from the PyTorch CPU
  index; a mismatched torchvision (0.29.1 vs torch 2.14.1+cpu) poisons
  every transformers import (`operator torchvision::nms does not exist`)
  — remove torchvision for this text-only stack. HF downloads must use
  the classic HTTP path (`HF_HUB_DISABLE_XET=1`); the XET path stalled
  mid-blob on this egress. Weights: 843 MB safetensors, unauthenticated
  HF fetch with resume.

## T1-DEMO — public simple-jev demo API: BLOCKED-EGRESS

- The hosted demo (https://simple-jev-demo-api.featherless.ai) refused
  every fleet surface tried: HTTP 403 from this sandbox (GET /v1/models
  and POST /v1/systemone), and HTTP 403 from GitHub Actions egress in
  classifier-trial-dispatch run **40517046438** (annotation verbatim:
  `systemone decide failed | HTTPError: HTTP Error 403: Forbidden`).
  The decide wiring itself is proven by T1-LAYA; the demo's edge policy
  excludes datacenter clients. Self-hosting (T1-LAYA) is the route.
- Same run, chat side: the allowlisted OpenRouter producer
  (liquid/lfm-2.5-2.6b:free) returned HTTP 429 this run — the free route
  is intermittent; it succeeded in run 40509162104. No retry was made
  (fleet doctrine: diagnose before retrying a 429).

## T1-KEV — Kev family: TRIAL_CANDIDATE (composition identified)

- Every Kev checkpoint on HF (jaredpalmer/kev-0.5b … kev-27b) is a
  **PEFT LoRA adapter + classification head** (`adapter_config.json`,
  `adapter_model.safetensors`, `head.pt`), not a standalone model —
  e.g. kev-0.5b: base `Qwen/Qwen2.5-0.5B`. There is no config.json;
  generic transformers serving refuses it ("Should have a model_type
  key in its config.json" — verified by attempting to serve kev-0.5b).
- A faithful Kev trial therefore needs Kev's own serve stack (which
  composes base + adapter + head) or a deliberate peft composition
  shim. Composing an approximation and reporting it as a Kev trial
  would misstate the evidence, so Kev is promoted only to
  trial_candidate with the composition recorded as the next step.

## T1-MEV — mev (Mellow AI): TRIAL_CANDIDATE (trial in flight)

- `stay-mellow-ai/mev` is a **full merged model** (2 safetensors shards,
  tokenizer, chat template) — directly servable via the simple-jev
  transformers backend, unlike Kev. A local serve + decide trial was
  started 2026-10-27; its record lands as a follow-up to this file.
- Mev (recruiting) (S1-04): no runnable release exists (a fine-tune
  described in a post only) — not-runnable; stays `referenced`.

## T2 — census rows on OpenRouter: BLOCKED-PAID

Checked against the live OpenRouter catalog 2026-10-27. The
decision-family ids present are all paid (nonzero pricing):
`inception/mercury-3`, `inception/mercury-2.5`, `inception/mercury-2`
(Mercury Decide kin), `upstage/solar-mini4` / `solar-pro4` /
`solar-pro-3` (Solar Decide kin). No `:free` decision-model ids are
listed. `typesafe/jev-router` is present with router pricing
(−1/−1 = varies) — Jev is a hosted paid route (see below).

## Blocked-paid list (owner ruling requested; SC-004)

Not executed under the standing free_only gate:

- **Jev — TypeSafe AI** (S1-01): hosted API; also listed on OpenRouter
  as `typesafe/jev-router` (varies pricing). The namesake hosted
  counterpart — the single most decision-relevant paid row.
- **Mercury Decide family** (S2, Inception): paid on OpenRouter.
- **Solar Decide family** (S2, Upstage): paid on OpenRouter.
- All other census rows whose only route is a paid hosted API or paid
  OpenRouter id — no free route exists for them today.

## Blocked-provisioning

- None of the census rows is blocked on a missing fleet secret after
  HUGGINGFACE_TOKEN landed (2026-10-27, dossier PR #1800). Gemini
  remains catalog-only for trials: its key 404s on generateContent
  (account no-cost entitlement unverified) — no census row depends on
  it in this tranche.
