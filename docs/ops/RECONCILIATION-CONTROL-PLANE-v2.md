# Reconciliation Control Plane v2

The production reconciliation engine is an **observe-only** control plane. It accepts a candidate and baseline ref, resolves both to immutable SHAs, classifies their graph relationship, and records evidence. It does not mutate refs.

This separation is intentional: branch switching is useful for MVT/DOE, while promotion or repair must remain a separate reviewed operation.

## Graph states

- aligned
- candidate-ahead
- behind
- diverged

`behind` and `diverged` are stop states. No force-push, reset, automatic side selection, or evidence deletion is permitted.

## Compound workflow architecture

Shared primitives should own ref resolution, retry classification, evidence capture, graph classification, and validation. Thin orchestration workflows compose those primitives for PR production, MVT, recovery, and continuous operations. This avoids hard-coded PR branches and reduces workflow sprawl.

## Iteration

Every corrective cycle records the current SHA, waits for asynchronous providers, re-fetches state, and starts a new iteration if the SHA or evidence changes. Completion requires current evidence, not merely a successful dispatch.
