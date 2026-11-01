# live-2-prlane-tuning — classifier rule/threshold tuning (LIVE design)

First designed campaign over the Tier 1 classifier estate
(steward CHECK 2026-10-31: DoE coverage of classifier units was
∅). Subject: the vocab-v2 PR-lane classifier's rule set.

Method = replay over FROZEN snapshots, because the live series
is non-stationary (inflow 102→152 open PRs in 3 days; the
NEED_EVIDENCE balloon is inflow composition, not rule drift).
Current rules are the control; rule/threshold levels are the
factors; responses are outcome-consistency rates joined from
eventual PR outcomes. Phase 0 proves replay determinism before
anything is tuned. Rule changes, if a variant wins, land as the
steward lane's own PR — the campaign never edits rules.
