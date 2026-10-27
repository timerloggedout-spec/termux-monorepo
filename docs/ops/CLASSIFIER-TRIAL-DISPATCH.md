# Classifier Trial Dispatch — first execution surface for the observatory quartet

State before this landed (verified 2026-10-27): the Tier 1 classifier
quartet in `deepcli/deepcli/observatory/` (Mev producer, Jev judge, Kev
verifier, Laya merger, orchestrated by `trial.run_trial`) was tested but
had never executed — no workflow imported it, and the provider adapter
layer Mev routes to (`deepcli.llm.adapters.<provider>`) did not exist.

## What landed

- `deepcli/deepcli/llm/adapters/` — stdlib-only provider adapters
  implementing the contract Mev/Jev expect (`Adapter()` with a settable
  `.model`, async `ask(prompt)` returning text/tokens/cost). Credentials
  come from the environment only. First routes: `gemini`
  (GEMINI_API_KEY) and `openrouter` (OPENROUTER_API_KEY), both
  already-provisioned keys on free routes.
- `deepcli/deepcli/observatory/dispatch.py` — CLI entry point:
  parses `prov:model` endpoints, enforces the free-only policy, runs one
  trial, writes the full trial record JSON, and exits non-zero unless a
  real trial produced a winning artifact.
- `.github/workflows/classifier-trial-dispatch.yml` — workflow_dispatch
  surface. Inputs: prompt, producer endpoint, judge endpoint (must
  differ from the producer — Jev refuses self-judging), rubric JSON,
  optional Kev reference text, task label, and `free_only` (default
  true). The trial record is uploaded as the `classifier-trial-record`
  artifact on every run. HindSight persistence uses the provisioned
  HINDSIGHT_* secrets (mapped to trial.py's HS_REMOTE_URL /
  HINDSIGHT_API_KEY / HINDSIGHT_BANK_ID env).

## Free-only policy (owner rule)

Default routes are the Gemini free tier and OpenRouter free models
(`openrouter/free` or any `*:free` model). Any other provider or a paid
OpenRouter model makes the dispatch refuse before any call is made.
`--allow-paid` / `free_only: false` is the explicit escape hatch and is
owner-gated — Jev's paid use is never the default path.

## Execution evidence (2026-10-27, steward verification runs)

The adapter layer and dispatch were exercised against the real provider
APIs from Actions (runs 40504965897–40506393011). Established state:

- **The wiring works.** Run 40505817467 produced a real producer
  artifact through the OpenRouter free router (2,119-byte trial record):
  Mev called the API, parsed the completion, and the trial proceeded to
  the judge stage. The failures below are provider-side states, not
  code defects — each is recorded in the run's annotations and trial
  record.
- **Gemini route: blocked on entitlement, not code.** The provisioned
  GEMINI_API_KEY resolves and its model catalog is observed (see
  PROVIDER-FREE-INFERENCE.md), but generateContent returns HTTP 404 for
  both gemini-2.5-flash and gemini-2.0-flash, and no account-specific
  no-cost entitlement has been established. The fleet's own continuity
  path is catalog-only for Gemini for the same reason. Do not treat the
  Gemini adapter as verified until an entitlement is established and a
  bounded smoke succeeds.
- **OpenRouter specific `:free` model ids: not the verified path.**
  Direct chat calls to catalog ids (llama-3.3-70b:free, qwen3-coder:free,
  deepseek-r1:free) return HTTP 404. The fleet-verified path is the
  exact allowlisted model below, requested with provider-routing
  constraints (allow_fallbacks: false, zero max prices) — see
  PROVIDER-FREE-INFERENCE.md.
- **Allowlisted model: currently rate-limited.** The one allowlisted
  zero-price model, `liquid/lfm-2.5-2.6b:free`, authenticates with
  `is_free_tier: true` and verified zero pricing, but inference returns
  HTTP 429 — the same result as the fleet's production smoke
  (run 39432211461). Whether the limit is account-wide, daily,
  model-specific, or upstream capacity is not established.
- **Defaults.** The workflow defaults are now producer =
  `openrouter:liquid/lfm-2.5-2.6b:free`, judge =
  `openrouter:openrouter/free`. Acceptance condition for the first
  completed trial: a dispatch at a time when the allowlisted route is
  no longer rate-limited, preceded by the provider-batch workflow's
  read-only `diagnose_free_limits` check (unblocked 2026-10-27 by
  PR #1780, which repaired the contracts gate; diagnose run
  40508502147 completed successfully). Repeated inference retries
  against a 429 are not authorized by this evidence.
- **First completed trial — acceptance condition met.** Run
  40509162104 (2026-10-27, after PR #1782 set the verified defaults)
  completed successfully: producer `liquid/lfm-2.5-2.6b:free`, judge
  `openrouter/free`; Mev → Jev → Kev → Laya all executed and Laya
  ranked a winner (2,353-byte trial record). The route remains
  rate-limit-prone, so a failed future dispatch should be read against
  fresh diagnose evidence before any retry.

## Known follow-up

`trial.run_trial` filters failed Jev/Kev entries before zipping them
with artifacts in `laya.synthesize`, so a mid-list critique failure can
pair an artifact with another artifact's verdicts. Single-producer
dispatches are unaffected. Fix belongs in trial.py with a regression
test (steward backlog).

## System One decide stage

`observatory/decide.py` + `llm/adapters/systemone.py` connect the
quartet to the System One ecosystem (proposal
`system-one-classifier-census`, catalog
`docs/ops/SYSTEM-ONE-CATALOG.md`): any TypeSafe-compatible decision
server (self-hosted Kev, simple-jev, Ollaya, …) can verify a text.
The rubric maps to Score questions with criteria ["0", "1"] — the
server's interpolated score is the 0..1 field score — plus a Noul
fabrication check. Dispatch flags: `--decide` (verify the winning
text after the trial; endpoint from `--decide-url` or the
SYSTEMONE_BASE_URL env), `--decide-only` (run just the check on the
prompt). Workflow inputs: `systemone_url`, `systemone_model`. Local
servers need no credential; SYSTEMONE_API_KEY is optional.
