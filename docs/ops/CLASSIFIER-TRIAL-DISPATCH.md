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

## Known follow-up

`trial.run_trial` filters failed Jev/Kev entries before zipping them
with artifacts in `laya.synthesize`, so a mid-list critique failure can
pair an artifact with another artifact's verdicts. Single-producer
dispatches are unaffected. Fix belongs in trial.py with a regression
test (steward backlog).
