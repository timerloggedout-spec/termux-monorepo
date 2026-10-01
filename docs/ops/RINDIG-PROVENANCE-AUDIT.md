# RinDig provenance audit

This report is generated from the canonical RinDig registry, GitHub branch heads,
and the submodule gitlinks committed in `termux-monorepo`.

## State model

- **aligned** — upstream head, owned-fork head, and committed submodule pin agree.
- **upstream-ahead** — the fork/pin agree, while RinDig upstream has moved.
- **pin-behind** — the fork has reached upstream, but the monorepo pin has not.
- **fork-and-pin-drift** — the fork and/or pin differs from upstream and requires review.
- **unresolved** — a head or gitlink could not be established.

The audit is evidence-only. It does not merge, synchronize, or mutate any repository.
