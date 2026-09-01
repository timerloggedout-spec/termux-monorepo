# Iteration Protocol

## Recon

Collect current PR/branch/ref state, current master SHA, review/thread state, checks, workflow runs, generated-index state, and relevant history. Use timestamps from the source platform and keep the source identifiers.

## Plan

Group findings by graph drift, source recovery, generated evidence, validation, security, documentation, and external-provider state. Prefer one bounded change per commit.

## Implement

Use the smallest evidence-backed forward correction. Reuse existing scripts and workflows. Do not duplicate orchestration logic when a shared primitive can carry the context.

## Commit

Commit to the intended branch. Include the source SHA or issue/experiment identifier in operational evidence where useful.

## Wait

Allow Actions and review providers to reach terminal states. Do not infer success from a dispatch request, skipped provider, or an old SHA.

## Validate

Re-fetch the current head and all relevant evidence. Run the canonical repository gates where appropriate. Re-check the graph because master may have advanced during the wait.

## Repeat

If the head changed, reviews changed, checks failed, or the graph diverged, start a new iteration. If all stop criteria are satisfied, publish the evidence and allow the separate promotion/merge gate to decide.
