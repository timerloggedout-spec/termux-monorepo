# Software Recipe Intelligence — DoE Plan

**Status:** candidate experiment design; not preregistered or dispatched.  
**Canonical run record:** `docs/ops/corpus/EXPERIMENT.schema.json`

## Research question

Does a neutral, provenance-aware software recipe representation improve capability discovery, classification, retrieval, similarity, impact analysis, composition recommendations, and reproducibility over existing repository search and specialized recipe systems?

## Arms

| Arm | Treatment |
|---|---|
| A0 | Existing repository search, metadata, registries, and current recipe/replay systems |
| A1 | A0 + deterministic recipe extraction and explicit rules |
| A2 | A1 + statistical multi-label classification |
| A3 | A2 + structural extraction and CRG relationship projection |
| A4 | A3 + lexical/ingredient/contract similarity and evidence-aware embeddings |
| A5 | A4 + isolated execution evidence, only after separate safety admission |

A5 is not admitted by this plan.

## Factors

- Representation: file-centric, fragment-centric, capability-centric, hybrid.
- Feature family: lexical, structural, dependency, ingredient, API/contract, workflow, runtime, combined.
- Classifier: rules, Naive Bayes, logistic regression, decision tree, calibrated ensemble.
- Similarity: token, TF-IDF, weighted overlap, AST, graph, embedding, hybrid.
- Provenance: minimal versus complete immutable lineage.
- Evidence level: declared, extracted, static-validated, observed, independently verified.

## Design and leakage controls

Block by language, repository, capability family, difficulty and source age. Randomize within blocks where appropriate. Keep near-identical revisions in the same partition unless temporal generalization is the explicit target. Use held-out repositories or later time windows for confirmation. Separate human-authored labels from model-inferred labels. Freeze extractor, tokenizer, parser, embedding, classifier and index versions per arm.

## Outcomes

Primary:
1. Top-k retrieval relevance against adjudicated ground truth.
2. Macro/micro F1 and calibration for multi-label classification.
3. Precision/recall for near-duplicate detection.
4. Compatibility false-positive rate and unsafe recommendation rate.
5. Change-impact precision/recall.
6. Reproducibility on eligible, safely replayable tasks.

Secondary: latency, token/compute cost, index size, graph build time, review burden, rework, abstention rate, maintenance cost, and human intervention.

Do not collapse dimensions into one opaque winner score. Safety failures are non-tradeable. Missing metrics remain null/unavailable, never zero.

## Sequence

- E0: corpus, system, ownership and label-quality census.
- E1: deterministic schema/extraction versus A0.
- E2: feature-family and classifier comparisons.
- E3: similarity and duplicate detection.
- E4: structural/graph impact analysis.
- E5: contract-aware composition recommendations.
- E6: reproducibility tests on safe, already-authorized recipes.
- E7: held-out confirmation, uncertainty analysis and independent decision record.

Every run records baseline/candidate SHA, experiment ID, arm/treatment, source provenance, confidence, timestamps, outcome, metrics, evidence refs and status using the canonical schema.

## Stop conditions

Stop an arm on secret leakage, policy bypass, unauthorized side effects, unbounded retries, provenance corruption, evaluation leakage, unsafe compatibility false positives, or material resource overruns. Record failure as evidence; do not rerun solely to turn the result green.

## Promotion

A result may justify a bounded next experiment. It does not authorize merge, deployment, provider spending, production routing, or automatic promotion. Delphi admission and DoE evidence remain distinct gates.
