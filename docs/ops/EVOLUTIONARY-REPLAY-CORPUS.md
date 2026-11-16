# Evolutionary replay → corpus projection

The replay simulator now has a narrow adapter into the repository's existing corpus EXPERIMENT contract.

## Boundary

DiscoveryHistory → ReplaySimulator → to_experiment_record() → corpus experiment record

The adapter is projection only:
- no provider or generated-code execution;
- no repository mutation;
- no Action→Effect causality inference;
- immutable baseline/candidate SHA anchors;
- treatment arm labeled replay;
- default status observed and confidence medium;
- online correctness and promotion remain behind existing gates.

Replay metrics are raw observations. Downstream ATES/WTCV/TCV/Action Effectiveness reducers retain their own null semantics and interpretation.

The next integration step is a separate read-only importer from Action Effectiveness observations into DiscoveryHistory, preserving temporal follow-through semantics.