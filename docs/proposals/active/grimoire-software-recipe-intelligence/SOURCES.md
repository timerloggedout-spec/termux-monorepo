# GRIMOIRE Sources, Inspirations and Evidence

This bibliography distinguishes external research inspiration, engineering standards/tools, and existing repository prior art. A source's existence does not establish that GRIMOIRE's proposed design is validated.

## A. Recipe classification and computational gastronomy

1. **Stack Overflow — “Algorithms used for programmatic classification of recipes” (2012).**  
   https://stackoverflow.com/questions/9265497/algorithms-used-for-programmatic-classification-of-recipes  
   Early practical framing: classify recipes from names, descriptions, methods, prep/cook times, ingredients and quantities. Answers discuss Bayesian methods, SVM, boosting, k-NN, neural nets, decision trees and feature engineering. The transferable lesson is to define the feature representation and avoid redundant signals before choosing a classifier. This is community Q&A, not a peer-reviewed benchmark.

2. **“What you use, not what you do: Automatic classification and similarity detection of recipes” (Data & Knowledge Engineering, 2018).**  
   https://doi.org/10.1016/j.datak.2018.04.004  
   Compares ingredient features with nouns extracted from free-text recipe instructions using logistic regression and decision trees; also evaluates similarity and near-duplicate detection. The study reports that feature combinations and corpus size materially affect results. Inspiration: separate ingredients from procedure, benchmark feature families, and evaluate classification and duplicate detection as different tasks.

3. **Bellingeri et al., “The recipe similarity network: a new algorithm to extract relevant information from cookbooks” (Scientific Reports, 2025).**  
   https://www.nature.com/articles/s41598-025-17189-6  
   Builds weighted recipe networks from shared ingredients; examines normalization, node centrality, thresholding and clique-based communities. Inspiration: ingredient overlap can become a graph, but normalization and thresholds change centrality and communities. Transfer to software must be tested; dependency counts alone can bias results.

## B. Software structure, build provenance and observability

4. **Tree-sitter — official documentation.**  
   https://tree-sitter.github.io/tree-sitter/  
   https://github.com/tree-sitter/tree-sitter  
   Incremental parser generator/library that produces concrete syntax trees and is designed to be fast and robust in the presence of syntax errors. Inspiration: structural extraction can be language-aware and incremental. Tree-sitter parse output is evidence about syntax, not proof of runtime semantics.

5. **SLSA v1.2 — Build terminology.**  
   https://slsa.dev/spec/v1.2/terminology  
   Defines build processes, steps, environments, external parameters, dependencies, outputs and provenance. It explicitly warns that “build recipe” can be ambiguous and uses more precise terms. Inspiration and caution: GRIMOIRE must not redefine SLSA terminology or conflate its general software recipe with a build platform's recipe/parameters.

6. **OpenTelemetry — Signals.**  
   https://opentelemetry.io/docs/concepts/signals/  
   Describes traces, metrics, logs and baggage as signals for observing system activity. Inspiration: connect recipe execution to runtime evidence through neutral telemetry rather than inventing a proprietary observability substrate.

7. **OpenTelemetry — Documentation.**  
   https://opentelemetry.io/docs/  
   Vendor-neutral observability framework for instrumentation, collection, processing and export. Potential integration surface, not a required dependency.

## C. Existing repository prior art — internal

8. **DoE Component Registry** — `docs/ops/DOE-COMPONENT-REGISTRY.md`, `ops/doe/component-registry.json`.  
   Current master registry documents separate algorithmic surfaces for Markov trellis lab, Bayesian routing, Kahn DAG planning and Gantt dependency phases. GRIMOIRE should be registered as its own component and evaluated individually; do not collapse components into one aggregate score.

9. **Delphi RFP gate** — `docs/ops/DELPHI-ORACLE-RFP-GATE.md`; form `.github/ISSUE_TEMPLATE/delphi-rfp.yml`.  
   Existing process: issue with `delphi:rfp` → sourced oracle → blind panel → signed ledger and admission disposition. Gate score is an admission signal, not proof of production utility. Use the existing filing shape and avoid unsupported quota claims for an internal component.

10. **DoE segmentation** — `ops/delphi/rfp-segments.json`.  
    Existing `doe-components` segment treats components individually, with role fitness, live evidence feeds, and separation as evaluation criteria. GRIMOIRE should follow this discipline if accepted.

11. **Commit Replay work** — PRs #3711, #3725, #3734, #3749.  
    Existing work includes fragment indexing, composition, symbol-level resolution, surgical recipe operations and extraction/lineage. This is a direct overlap warning and an integration opportunity. GRIMOIRE is not a replacement for Commit Replay or Repo Replay; it models higher-order software capability contracts and lifecycle evidence.

12. **QUE/SIE lifecycle task** — issue #5389 and PR #5390.  
    Existing repository work connects OBSERVE → TRIAGE → RESEARCH → RFP → DELPHI → DESIGN → CLAIM → IMPLEMENT → VERIFY → PROMOTE → LEARN. GRIMOIRE should use this pipeline rather than inventing a parallel admission/claim authority.

13. **Proposal package binding** — issue #5156 (QD-039).  
    Documents a requirement to bind RFP awards to complete proposal-package content digests, with immutable source refs and a later manifest ref. This proposal package should adopt that contract when the implementation is available; this draft does not claim that the current RFP form/gate already enforces package digest binding.

## D. Research hypotheses — not established facts

- Recipe decomposition may improve retrieval and impact analysis.
- Multi-view features may outperform lexical-only classification.
- Graph similarity may expose capability families missed by text search.
- Provenance-rich recipes may reduce stale or ambiguous reuse.
- Execution receipts may improve confidence in compatibility and reproducibility.

Each hypothesis requires an explicit benchmark and may be rejected by the DoE results.
