# Optional AMD-compatible inference

Match Impact Desk is fully functional without a model. Matching, exposure arithmetic, exception classification, and controller approval are deterministic. The optional OpenAI-compatible endpoint drafts a readable controller brief only.

## AMD Lemonade / local endpoint

For local development on a supported AMD Windows/Linux system, configure the local Lemonade OpenAI-compatible endpoint:

    MATCHDESK_INFERENCE_BASE_URL=http://127.0.0.1:13305/api/v1
    MATCHDESK_INFERENCE_MODEL=<model-id-from-local-model-catalog>

The local endpoint must be reachable from the app process. A Vultr-hosted process cannot reach a developer laptop's 127.0.0.1; use a private authenticated network if a remote AMD endpoint is deliberately operated. Never expose a local inference port directly to the public internet.

## Vultr Serverless Inference

    MATCHDESK_INFERENCE_BASE_URL=https://api.vultrinference.com/v1
    MATCHDESK_INFERENCE_MODEL=<model-id-from-live-catalog>
    MATCHDESK_INFERENCE_API_KEY=<runtime-secret>

Do not hard-code a model identifier or credential.

## Trust boundary

Only structured identifiers, totals, exception evidence, and deterministic recommendations are sent to the model. Raw documents and credentials are excluded. Model output cannot change a match, approve an exception, release payment, or post a ledger. The official Vultr Agent Rush Challenge 2 brief says Vultr GPUs are unavailable for this event and Serverless Inference is optional for that track. No AMD hardware provisioning or benchmark claim is made by this project.
