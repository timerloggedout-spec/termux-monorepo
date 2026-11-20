# HindSight extraction route — multi-arm fleet inference (#5553)

Route of record for HindSight fact extraction. Replaces the single-homed
OpenRouter credit pool (pool at 402; 326 payloads blocked; retain = 0) with
multi-arm routing over independent fleet providers. The exit changes the
inference route only — HindSight's data model and attribution-separation
invariants are unchanged (326/326 held during the outage).

## Arms (probe order)

| # | arm | provider | model | key (Actions secret) |
|---|-----|----------|-------|----------------------|
| 1 | cohere | cohere | command-a-03-2025 | COHERE_API_KEY |
| 2 | groq | groq | openai/gpt-oss-120b | GROQ_API_KEY |
| 3 | gemini | gemini | gemini-2.5-flash | GEMINI_API_KEY |
| 4 | mistral | mistral | mistral-small-latest | MISTRAL_API_KEY |
| 5 | openrouter | openrouter | meta-llama/llama-3.3-70b-instruct:free | OPENROUTER_API_KEY |

Extraction is small-model fact extraction; every arm fits free-tier capacity.
OpenRouter is one arm among many — last in probe order, never the sole route.

## Failover

`fly-hindsight-config.yml` action `apply` (arm `auto`, the default) probes
each arm's provider endpoint with a live chat completion, in table order.
The first live arm is written to the Fly app secrets (`hindsight-termux`),
the app restarts, and health is gated. A dead arm is skipped automatically —
the rotation is the failover, and the apply run log is its demonstration.
Action `probe-all` probes every arm and reports the table without changing
config (evidence run). A named arm can be forced with the `arm` input.

## Replay of the blocked payloads

After a successful apply, dispatch `telemetry-ingest.yml`: it regenerates
the retain payloads (`ops/telemetry/hindsight-payloads.jsonl`), runs its
state-gated retain PROOF (3 units, first spend = tested spend), then the
full retain. Results land as a refresh PR updating
`ops/telemetry/hindsight-retain-state.json` + `hindsight-retain-proof.json`;
`scripts/telemetry_ingest/hindsight_verify.py` reads back bank stats +
recall as the verification receipt.

## Surfaces

- Live route: Fly app `hindsight-termux`, configured by
  `.github/workflows/fly-hindsight-config.yml` (this route).
- `deploy/fly/fly.toml` (`hindsight-deepagent`) default env is aligned to
  arm 1 as the fallback default; applied secrets remain authoritative.
- Koyeb deploy workflow is a standby surface, not the live route; it still
  pins OpenRouter and is out of scope for this exit.
