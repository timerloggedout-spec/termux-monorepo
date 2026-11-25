# Card: flywheel-comms

**live.** Fleet agent-to-agent comms = repo-mediated store-and-forward
channels ("flywheel"): appends are commits in a GitHub store, reads ride
each participant's own cadence loop. The owner is never a relay.

Policy + registry: `docs/ops/flywheel-comms/POLICY.md` ·
`docs/ops/flywheel-comms/REGISTRY.json` (FLY-001…FLY-005).

A channel counts as established only with a registry row, a protocol doc
at its path, and one round-trip receipt in the store.
