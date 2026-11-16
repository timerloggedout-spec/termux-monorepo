# Action Effectiveness → replay history importer

`history_from_action_effect_state()` is the read-only bridge between the existing Action Effectiveness ledger marker and evolutionary replay.

## Mapping

- each bounded `recent_events` entry becomes one terminal replay node;
- event ID becomes the stable node identity;
- event timestamp is parsed for validity;
- FOLLOWED_BY_COMMIT maps to exploratory score 1.0;
- NO_LATER_COMMIT_IN_RANGE maps to exploratory score 0.0;
- lag_minutes becomes replay cost;
- no relationship is interpreted as causal.

The score is intentionally a feature of the replay experiment, not an effectiveness verdict. Downstream ATES/WTCV/TCV and Action Effectiveness semantics remain authoritative for operational interpretation.

## Data-loss boundary

The current ledger marker is a bounded projection. The importer therefore does not pretend it has the complete historical event population. A future richer importer can consume the underlying correlation JSON when that source is persisted as a first-class artifact.