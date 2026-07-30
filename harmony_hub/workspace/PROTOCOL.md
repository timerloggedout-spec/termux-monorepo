# Harmony Hub – Versioning Protocol

## Core Principle
All code changes originate from chat.deepseek.com conversation exports.
Local files are the source of truth; the hash index tracks provenance.

## Process
1. **Extract**: `synthegrate harvest <export.json>` → code blocks into workspace.
2. **Normalize**: Field adapter detects API shape changes and maps to canonical names.
3. **Sandbox**: Copied into `harmony_hub/workspace/<feature>/`; originals untouched.
4. **Patch**: CEDARscript diffs applied to sandboxed copies.
5. **Test**: `validate_refactor.py --project <name>` runs project-specific tests.
6. **Commit**: Success logged to `run_history` with hash, verdict, signature.
7. **ELO Update**: `elo_updater.py` recalculates agent ratings.
8. **Promote**: Only after passing tests, the sandboxed file moves to `harmony_hub/src/`.

## Iteration
- Registry `tools_fts` enables searching for existing solutions.
- `messages_fts` indexes conversation history for rapid retrieval.
- Failed attempts archived; successful patterns reinforced via ELO.

## Field Resilience
- `message_adapter.py` normalizes API responses to canonical field names.
- When the API changes, only the adapter needs updating, not every consumer.

