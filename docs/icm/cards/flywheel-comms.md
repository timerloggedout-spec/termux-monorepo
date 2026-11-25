# Card: flywheel-comms

**live.** Fleet agent-to-agent comms = repo-mediated store-and-forward
channels ("flywheel"): appends are commits in a GitHub store, reads ride
each participant's own cadence loop. The owner is never a relay.

Policy + registry: `docs/ops/flywheel-comms/POLICY.md` ·
`docs/ops/flywheel-comms/REGISTRY.json` (FLY-001…FLY-006 + a peers section).

A channel counts as established only with a registry row, a protocol doc
at its path, and one round-trip receipt in the store.

Peers register in the REGISTRY peers section before or at first use of a
channel (POLICY Rule 10); a peer with no registered channel is a coverage
defect and its activity is unobserved. Current NOT REGISTERED peer: chatgpt
(registration is a done-evidence leg of QUE #5885).

Channel split (2026-11-25): FLY-005 cue-comms = exports + backup
coordination; FLY-006 cue-work-comms = all other pair work. Maintain the
clear division.
