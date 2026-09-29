# Gemini Interactions API integration

Status: implemented as an additive adapter. Existing generateContent and Gemini CLI paths remain unchanged.

## Why this lane exists

The repository already has GEMINI_API_KEY wired into Gemini CLI workflows and a native Gemini generateContent backend. The Interactions API adds a separate execution surface for stateful conversations, observable execution steps, and request-level storage control.

Google documents the Interactions API as the current API for new Gemini applications. It supports previous_interaction_id, store, execution steps, labels, and usage metadata.

## Repository surface

- llm-api-hub/server/gemini_interactions.py
  - OpenAI-compatible local adapter on 127.0.0.1:8788
  - outbound endpoint: Gemini /v1beta/interactions
  - credential: GEMINI_API_KEY only
  - no secret persistence or prompt/response logging
- llm-api-hub/tests/test_gemini_interactions.py
  - payload/state/normalization contract tests
- .github/workflows/gemini-interactions-smoke.yml
  - manual smoke test using the repository secret
  - never prints the API key or prompt/response body
  - emits only interaction ID, status, and token counts
- Existing .github/workflows/gemini-review.yml and gemini-dispatch.yml
  - remain on Gemini CLI and are not silently migrated by this change.

## Storage policy

GEMINI_INTERACTIONS_STORE defaults to false in the local adapter so a new deployment does not silently persist prompts/responses.

Set it to true when the project intentionally wants stateful interactions and AI Studio logging. A request can also set store=true.

If previous_interaction_id is supplied, store=true is required because server-side conversation state depends on stored interactions.

Treat stored interactions as sensitive operational data. Do not put credentials, tokens, browser sessions, or other Class 3/4 artifacts into prompts merely because the API can store them.

## AI Studio settings

The supplied screenshots show the Interactions API project toggle disabled and a 55-day retention selector. That means the project is configured not to store Interactions by default in AI Studio. Request-level store=true is the explicit API override supported by Google.

Controlled rollout:

1. Keep the project-level default off while validating the adapter.
2. Use store=true only for intentionally observable experiments.
3. If stateful-by-default behavior is desired, enable Interactions API storage in AI Studio and set GEMINI_INTERACTIONS_STORE=true in the deployment environment.
4. Revisit retention deliberately. Paid-tier project logs support 7, 14, 28, or 55-day retention.

## Verification

Local contract tests:

    python3 -m unittest discover -s llm-api-hub/tests -p 'test_gemini_interactions.py'

Manual smoke:

    Actions -> Gemini Interactions API Smoke -> Run workflow

Required secret:

    GEMINI_API_KEY

The smoke workflow sends a deliberately non-sensitive probe, requests store=true, and reports the returned interaction ID/status without printing request or response content.

## Integration contract

Consumers that already speak OpenAI Chat Completions can point the adapter at:

    http://127.0.0.1:8788/v1

and use a model such as:

    gemini-interactions/gemini-flash-latest

For stateful continuation, pass:

    previous_interaction_id: <prior interaction id>

The normalized response includes provider_metadata.interaction_id. The HTTP response also carries X-Gemini-Interaction-ID.

This gives the ADE telemetry layer a stable provider-side interaction identity without copying prompt/response bodies into repository telemetry.
