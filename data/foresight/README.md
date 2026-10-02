# Foresight Data

Canonical evidence records live in `resource-registry.jsonl`.

Records are append-oriented. Revisions use the same `resource_id`; consumers
deduplicate to the latest observation.

Never store credentials, cookies, tokens, private keys, or session secrets.

Retrieval agents are responsible for finding sources. The registry is
responsible for preservation, validation, fingerprinting, filtering, and export.
