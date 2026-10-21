# Briefing Evidence Registry

This directory is the append-only evidence surface for the daily foresight digest.

- `resources.jsonl`: source/resource observations.
- `procurement.jsonl`: inspectable FOSS procurement records.
- `radar.jsonl`: H0-H3 foresight records.
- `briefings/YYYY-MM-DD.json`: validated five-item briefing snapshots.

Do not treat a dashboard, vendor database, or model response as canonical. Canonical
records preserve source URL, observation date, evidence status, horizon, confidence,
version/commit where applicable, and unresolved questions.

The registries are intentionally append-only: corrections add a new observation rather
than rewriting historical evidence. Secrets and raw credentials are prohibited.
