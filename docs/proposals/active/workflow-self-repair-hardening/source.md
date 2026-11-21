# Source — workflow-self-repair-hardening

## Scope origin

This proposal is derived from the live failure evidence in issues #5316, #5361 and #5363, inspected on 2026-11-15. It is a narrow implementation lane for those incidents, not a generic authorization for autonomous workflow rewrites.

## Candidate implementation

- #5476 implements SRH-001.
- #5477 implements SRH-002.
- #5478 implements SRH-003.

Each candidate remains a draft pending exact-head validation, independent review, and the self-repair acceptance requirements recorded on its owning issue.

## Safety invariants

Preserve these invariants: CI must never be falsely green; missing data remains unknown rather than zero/success; API quota is never bypassed; paid fallback, credential mutation, production dispatch expansion and auto-merge remain prohibited.
