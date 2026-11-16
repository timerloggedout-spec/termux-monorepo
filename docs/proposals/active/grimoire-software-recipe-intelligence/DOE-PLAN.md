> Scope correction: evaluate SRM as a domain-model treatment within existing MOSAIC Brain/DoE governance, not as an independent GRIMOIRE component. See ../continuous-capability-evolution-lab/MOSAIC-BRAIN-SOFTWARE-RECIPE-MODEL.md.\n\n# MOSAIC Brain DoE Plan — versioned recipe intelligence competition

**Surface:** `mosaic_brain.recipe_model`  
**Version:** 0.1.0-draft  
**Status:** Proposed; no live traffic or production execution authorized.

## 1. Question

Does a canonical, provenance-aware software recipe representation improve capability discovery, classification, similarity, impact analysis, composition, and reproducibility over the existing repository/tooling baseline?

## 2. Arms

| Arm | Description | Admission state |
|---|---|---|
| A0 | Existing repository search and metadata | Baseline |
| A1 | SRM + deterministic extraction/rules | Candidate |
| A2 | A1 + TF-IDF/logistic regression | Candidate |
| A3 | A2 + typed graph and normalized structural/ingredient similarity | Candidate |
| A4 | A3 + embeddings and evidence-aware reranking | Candidate |
| A5 | A4 + isolated execution receipts and outcome evaluation | Requires separate safety admission |

Arms are separate versions, not a cumulative aggregate score. A5 is not eligible until sandbox and policy requirements are met.

## 3. Factors and levels

- Representation: file-centric, recipe-centric, hybrid.
- Feature family: lexical, structural, ingredient, contract, runtime, combined.
- Classifier: deterministic rules, logistic regression, decision tree, calibrated ensemble.
- Similarity: token, weighted ingredient overlap, AST, graph, embedding, hybrid.
- Provenance: minimal, full immutable lineage.
- Execution evidence: absent, static tests, isolated replay.

## 4. Blocking and randomization

Block by language, repository, capability family, difficulty, and source age. Randomize task assignment within blocks. Where leakage is possible, hold out entire repositories or later time windows. Do not randomly split near-identical files across train and test.

## 5. Primary outcomes

1. Top-k retrieval relevance (adjudicated ground truth).
2. Macro/micro F1 and calibration for multi-label classification.
3. Precision/recall for near-duplicate detection.
4. Contract compatibility precision and unsafe false-positive rate.
5. Change-impact precision/recall.
6. Reproducibility rate on eligible tasks.

Secondary outcomes: latency, token/compute use, cost, index size, graph build time, review burden, rework, abstention rate, and maintenance overhead.

## 6. Measurement contract

Every observation records:
- experiment ID, arm ID, recipe/schema/classifier versions;
- immutable repository/source SHA and corpus snapshot;
- task family, block, difficulty, assignment method;
- tool/provider/model version and configuration;
- start/end time, resource/cost metrics where available;
- output digest, evaluation record, exclusions and reason;
- source trigger and run URL/receipt.

No missing metric is silently converted to zero. Not-run, unavailable, partial, invalid, and excluded are distinct statuses.

## 7. Dataset and leakage controls

- Build an adjudicated corpus from repository artifacts and existing historical records.
- Deduplicate by immutable source identity before partitioning.
- Keep related revisions in the same split unless the experiment explicitly measures temporal generalization.
- Separate labels authored by humans from labels inferred by models.
- Publish class imbalance and coverage.
- Freeze preprocessing and feature extraction versions per run.
- Preserve false positives and false negatives for error analysis.

## 8. Analysis

Report per-arm outcomes, confidence intervals, class-specific performance, calibration, failure modes, and compute/resource cost. Use paired comparisons on the same tasks where feasible. Predeclare primary metrics and exclusions. Use held-out confirmation for any apparent winner. Avoid selecting a winner on a single aggregate metric.

## 9. Safety and stopping

Stop an arm on secret leakage, policy bypass, unauthorized external side effects, unbounded retries, provenance corruption, or material evaluation leakage. Any such event is a failed safety outcome, not a tradeable performance penalty. A5 execution remains disabled until separately admitted.

## 10. Promotion

Delphi admission is an admission signal only. DoE evidence determines whether the method met predeclared outcomes. A winner may be recommended for a bounded next trial; it is not automatically merged, deployed, or promoted. Preserve inconclusive and no-change outcomes.

## 11. Experiment sequence

- E0: corpus and task census; validate label quality.
- E1: deterministic SRM schema/extraction vs A0.
- E2: feature-family and classifier comparisons.
- E3: similarity and duplicate detection.
- E4: graph and change-impact analysis.
- E5: composition recommendation with contract checks.
- E6: reproducibility replay on safe eligible recipes.
- E7: held-out confirmation and decision record.

## 12. Acceptance

The experiment is complete only when immutable source snapshots, arm versions, task assignments, observations, exclusions, analysis, and decision records reconcile. No claim of superiority without held-out evidence.
