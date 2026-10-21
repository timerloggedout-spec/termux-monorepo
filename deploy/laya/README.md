# Laya deployment lanes

GitHub Actions is the canonical automated live smoke and CADENCE sweep lane. It pins Laya 0.3.5, uses Python 3.12, disables TensorFlow probing, caches Hugging Face weights, and publishes receipts.

Render is the long-lived HTTP adapter lane and requires enough memory for the selected checkpoint. The HTTP adapter exposes:
- `GET /healthz`: unauthenticated platform health probe.
- `POST /decide`: JSON object containing a dictionary `state` and non-empty dictionary `questions`; request body is capped at 256 KiB.

## Hosted API security

Set a strong `LAYA_API_TOKEN` secret in the Render service environment. When configured, `POST /decide` requires `Authorization: Bearer <token>`; comparisons are constant-time. Set `LAYA_REQUIRE_AUTH=1` to fail closed if the token is missing. Do not expose a public decision endpoint without authentication. The adapter returns generic engine errors and does not include exception details in HTTP responses.

Keep the health endpoint unauthenticated for platform probes. Use TLS at the hosting platform, rotate tokens, and avoid placing sensitive customer data in request logs or benchmark artifacts.

Colab is the GPU/large-memory benchmark lane: install laya 0.3.5 and run `USE_TF=0 python scripts/laya_sweep.py --live`.

Hugging Face supplies the upstream weights used by the pinned package. The Hub metadata currently reports the `hf-inference` provider as errored for this model, so the repository's local Python Router path is the intended live smoke until provider inference is independently verified.

Vercel should host observation/control UI or a proxy, not model residency.

The GitHub `laya-live` environment is the place for optional deployment credentials. Secret values never belong in the repository. Mock/contract tests verify wiring only; they are not evidence of model accuracy or a successful live inference.
