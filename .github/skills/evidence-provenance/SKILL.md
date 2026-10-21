# Evidence Provenance Skill

## Purpose
Provide one evidence vocabulary across GitHub, Actions, Linear, Notion, Hex, and Vercel.

## Evidence Envelope
Required fields: experiment_id, source, source_id, commit_sha, baseline_sha, observed_at, event_at, status, outcome, provenance, confidence, supersedes.

## Rules
- GitHub refs, commits, reviews, checks, and workflow runs are authoritative for repository state.
- Notion is a human-facing cockpit, never the Git ledger.
- Linear coordinates execution and issue/project linkage.
- Hex analyzes experiment evidence and comparisons.
- Vercel supplies deployment/preview evidence; deployment health is distinct from repository correctness.
- Preserve raw evidence before cleanup.
- Never fabricate missing timestamps, counts, runs, or historical telemetry.
- A superseded artifact remains traceable through its replacement and source SHA.
