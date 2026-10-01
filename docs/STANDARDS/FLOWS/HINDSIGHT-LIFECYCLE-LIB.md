
### Batching contract (v0.6.0)
- **HTTP batch**: up to `MVT_BATCH_SIZE` items per POST (default 8).
- **Content**: NEVER concatenated. Per-item `metadata` is preserved
  through extraction into every fact.
- **RPD cost**: unchanged — 1 LLM call per item.
- **Concurrency**: matches Hindsight `shared_slots` (8).
