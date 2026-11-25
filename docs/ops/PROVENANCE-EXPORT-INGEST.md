# Provenance export ingest (#5555)

DO treat the VM batch export as the source of record: Jules corpus = 417 sessions ⇒ private store `timerloggedout-spec/muse-vm-workspace-backup` under `jules-harvest/2026-11-17/` (¬ re-harvest ∧ ¬ hand-copy). Muse side-chat cloned exports join the same pipeline as the message-export class (`muse-side-chat/<date>/`). Their namespace-scoped discovery classifier emits versioned topic labels for moniker, collision, marketing, naming, anon, 4n0nSEC, 4n∅N, 4n∅nSEC, and profiles; the digest aggregates term counts without exporting message excerpts.

## Pipeline
1. Route: VM `~/workspace/repo-exports/REQUESTS.jsonl` request line (#5549 drain) ⇒ VM publishes `jules-harvest/2026-11-17/` to the store.
2. Run `.github/workflows/provenance-export-ingest.yml` (`source_ns=jules-harvest/2026-11-17`).
3. `scripts/provenance/ingest_exports.py` explodes sessions ⇒ records {prompt ∨ plan ∨ agent message ∨ progress ∨ user turn}; classifies each AT ingestion: `{classifier_id, classifier_version, label, confidence, rule}` (chat_intent ∀ text records; `ml/pipelines/lanes/classify.py` ∀ PR-bearing records; `muse_side_chat_seo` only for `muse-side-chat/` namespaces).
4. Join to Actions runs (21-day window) by head_sha ∨ head_branch ∨ PR number ⇒ verdict {consistent ∨ claim-unevidenced ∨ no-claim}.
5. Publish records ⊕ digest ⊕ consumer-read receipt to the store at `provenance/<source_ns>/run-<run_id>/` (append-only).
6. `scripts/provenance/export_digest.py` = registered consumer (`ops/provenance/consumers.json`); its read receipt ⊢ utilization.

## Invariants
- Keep per-source namespaces distinct: `record_id = sha256(source_ns | origin | native_id | kind)`.
- Reduce credential-shaped strings to existence ∧ sha256.
- Keep public artifacts aggregate-only (digest); text excerpts stay in the private store. Muse discovery tags are versioned labels; the namespace gate keeps the taxonomy scoped to Muse side-chat exports.
- Read confidence as rule-tier weight ⊬ calibrated accuracy until the chat-intent labeled-outcome gate (n ≥ 30/class) is met.
