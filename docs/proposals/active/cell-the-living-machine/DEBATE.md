# DEBATE — cell-the-living-machine

## Term: cell-the-living-machine/1

**Driver:** ChatGPT  
**Status:** Open for Operator review.

## Decisions and proposed defaults

| Decision | Options | Proposed default | Review owner |
|---|---|---|---|
| Repository topology | Single MonoRepo product; dedicated game repo; three-plane network | Dedicated game repo + MonoRepo project profile + Research Astute/Search Astutely research planes | Operator |
| Cross-repository coupling | Symlink; copied files; API and manifest contracts | Versioned manifests and API contracts; local symlink convenience only | Development + Delivery Reliability |
| Project profile shape | New independent schema; existing ArchWiz profile contract + domain manifest | Existing `project-profile/v1` scope profile + game-specific project manifest + registry index | Orchestration & Quality Control |
| Search Astutely identity | Existing connector; GitHub organization; alternate account/org | Treat `search-astute-ly` as verified organization; validate runtime and account ownership | Operator + Research |
| Research Astute reuse | Direct import; links and references; selective licensed reuse | Reuse references and metadata first; approve content imports by source license and ownership | Research + Operator |
| Audience progression | Age bands; one difficulty ladder; knowledge lenses | Shared knowledge corpus with Field, Mechanism, Quantitative, Structural, and Research lenses | Game Design + Accessibility |
| Challenge model | More/less content; altered challenge conditions | Tune constraints, uncertainty, time, resource budgets, and system coupling | Game Design |
| Game shape | One exclusive genre; hybrid facets | Simulation + systems strategy + exploration + puzzle + RPG progression facets | Game Design |
| Engine | Godot; Unity; Unreal; browser runtime; other | Compare after target-platform and molecular-rendering prototype requirements are fixed | Development |
| iJEP media | Embed, adapt, or reproduce | Link as reference; record license and written permission before asset reuse | Research + Legal/rights reviewer |

## Design principles

- Knowledge access remains ubiquitous across audiences.
- Explanatory resolution and challenge parameters remain independently selectable.
- Evidence classes distinguish experimental, curated, computational, educational, and gameplay records.
- Specialist views expose quantitative detail, structure IDs, residue-level annotations, methods, and source literature.
- Accessibility includes readable labels, optional detail, text equivalents, adjustable motion, color-independent encoding, and input flexibility.

## Open questions for review

1. Which organization owns the dedicated game repository: `timerloggedout-spec` or `search-astute-ly`?
2. Which Search Astutely repository or service is the canonical aggregator?
3. Which Research Astute content is user-owned and approved for reuse?
4. Which initial organism and cell type should anchor the vertical slice?
5. Which target platform leads the first playable prototype?
