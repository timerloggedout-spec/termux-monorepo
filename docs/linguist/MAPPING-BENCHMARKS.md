# Linguist Mapping Benchmarks

## Purpose

The mapping benchmark suite evaluates whether Linguist can retrieve, classify,
translate, and compose mappings between independently governed customs.
It complements the repository's codec and notation tests with a reproducible
corpus/query/relevance-judgment experiment.

The dataset-generation pattern is informed by Google's DeepMind LIMIT notebook:
a reproducible seed, generated queries, a corpus, explicit relevance judgments,
controlled candidate overlap, and conflict-aware candidate assignment. LIMIT is
an information-retrieval dataset-generation example; this suite adapts its
experimental shape to cross-custom mapping evaluation rather than treating
LIMIT as a notation dataset.

Reference: [LIMIT dataset generation notebook](https://github.com/google-deepmind/limit/blob/main/code/generate_limit_dataset.ipynb).

## Benchmark lanes

| Lane | Input | Evaluation role |
|---|---|---|
| External dataset-generation pattern | LIMIT-style corpus/query/qrels construction | reproducible retrieval experiment design |
| Cross-custom notation | Fleet notation ⇔ Lean/Mathlib | exact, approximate, and domain-qualified mapping |
| CedrLang / Grimoire | SYMBOL_MAP, MAPPINGS, LEET_MAP, canonical tokens | codec compatibility and round-trip |
| `zipfs-law_fork` | natural-language word-frequency corpus | rank/frequency skew and common-to-rare lexical coverage |
| `zipf_fork` | programming-language corpus (Flask study) | code-token frequency, abbreviation pressure, identifier-tail coverage |
| `twitter_sentiment_analysis_part3_fork` | sentiment-analysis corpus | domain vocabulary and polarity-label crosswalk stress |
| `hypemergence_fork` | multi-source social time-series features | feature-name normalization and cross-source alignment |
| Nomenclature matrix | concept, label, and mapping seed records | relation, confidence, provenance, lifecycle |
| Cedar pointer maps | pointer command registry and expansion | pointer integrity and reconstruction |

The four research repositories above are registered in
`docs/proposals/active/notation-sets/ITEMS.md` as reference corpora. Their
adapters remain a follow-on ingestion task; this PR establishes the common
benchmark contract first. Zipf/ZIPFS corpora measure token-frequency behavior
and act as distributional stress lanes. Frequency similarity alone does not
establish semantic equivalence.

## Mapping record contract

Each mapping record carries:

- `mapping_id`: stable unique identifier;
- `source_custom` and `target_custom`: independently named notation systems;
- `source_form` and `target_form`: observed forms;
- `semantic_id` and `domain`: semantic identity and scope;
- `relation`: relation asserted by the source record;
- `grade`: `exact`, `approximate`, `analogue`, or `lossy`;
- `kernel`: explicit information lost or extra assumptions required;
- `provenance`: source path plus a stable locator.

The benchmark preserves grades and kernels as supplied. It does not promote
analogies to equivalences or infer missing mappings.

## Dataset shape

`linguist-mapping-benchmark/v1` contains:

- `corpus`: mapping records keyed by `mapping_id`;
- `queries`: generated cross-custom retrieval tasks;
- `qrels`: positive mapping IDs for each query;
- `candidates`: pair-scoped candidates, including hard negatives;
- `conflicts`: identical source surfaces with distinct semantic/domain keys;
- `stats`: corpus, query, relevance, conflict, and grade counts.

Query identity includes source custom, target custom, domain, and semantic ID.
This makes overloaded symbols such as `∘` separable by domain. Competing
interpretations remain visible as hard negatives instead of being collapsed.

## Reproduction

Generate the fixture benchmark with:

```sh
python scripts/linguist/mapping_benchmark.py \
  --input experiments/linguist/mapping-benchmarks/fixtures/fleet-lean-mappings.json \
  --output /tmp/linguist-mapping-benchmark.json \
  --seed 42
```

Run focused tests with:

```sh
python -m pytest tests/test_linguist_mapping_benchmark.py -q
```

The generator uses the Python standard library. Dataset output is deterministic
for a fixed input and seed.

The evaluator exposes `evaluate_rankings(dataset, rankings)` for macro
precision@k, recall@k, mean reciprocal rank, and nDCG. It validates query and
mapping identifiers and treats an omitted query ranking as an empty result.

## Evaluation dimensions

1. **Retrieval:** recall@k, precision@k, mean reciprocal rank, and nDCG.
2. **Semantic fidelity:** exact/approximate/analogue/lossy grade agreement.
3. **Domain discrimination:** correct handling of overloaded symbols and
   same-surface collisions across customs.
4. **Round-trip:** exact reconstruction for reversible mappings, with named
   kernels for lossy mappings.
5. **Composition:** relation composition and preservation of direction/order.
6. **Provenance:** mapping source, locator, version, and evidence survive
   every transformation.
7. **Distribution robustness:** common/rare-token strata from ZIPFS corpora,
   reported separately from semantic accuracy.

## Repository integration boundary

This suite is additive. Existing runtime mappings remain authoritative in
their current sources of record, including CedrLang, phase codec, Grimoire,
nomenclature, routing notation, and Cedar pointer commands. The benchmark
fixture is a small sourced cross-custom seed; it is not a replacement registry.

The existing Linguist panel feed remains a runtime-source projection.
Benchmark datasets are experiment artifacts and should be generated in a
separate path with explicit provenance. Private pointer payloads and secrets
remain outside public fixtures and generated artifacts.


## Expanded first-party mapping lanes

The fixture now incorporates the canonical Fleet ⇔ Lean/Mathlib matrix and vector-store crosswalk plus the 14 concept links currently recorded in the nomenclature seed.

- **Fleet ⇔ Lean/Mathlib:** source rows retain their recorded exact/approximate grade and named kernel. P-001 supplies a proof-verified function-composition row; P-002 supplies a proof-verified matrix-identity row. Other rows remain marked `spec-level` until their own proof or runtime verification exists.
- **Nomenclature seed:** all 14 source mappings are included as `analogue` retrieval records with their original relation, confidence, evidence note, source IDs, and `candidate` status. Candidate relations remain provisional; the benchmark preserves them as retrieval material rather than upgrading them to semantic equivalence.
- **Gaps stay gaps:** transpose, ANN top-k, persistence, sqlite-vec, and other rows without a target mapping remain outside the corpus.

The dataset therefore measures retrieval over recorded assertions at multiple evidence states. Report `evidence_status` alongside every score, and interpret candidate-seed results as provisional retrieval coverage rather than adjudicated semantic accuracy.
