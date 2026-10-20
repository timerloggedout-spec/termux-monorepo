# Cost of Remembering — Filesystem Memory Evidence

**Source fork:** `refTemplates/smods/cost-of-remembering_fork`  
**Upstream:** https://github.com/RinDig/cost-of-remembering  
**Owned fork:** https://github.com/timerloggedout-spec/cost-of-remembering_fork  
**Pinned intent:** evidence + harness for ICM-style filesystem memory vs long-context.

## Claim (paper)

Filesystem memory (empty folder + filing conventions + agent that walks folders) matches long-context accuracy on LongMemEval while reading **97% fewer tokens** and costing **95% less** per question. No embeddings, no vector DB — Markdown files in directories.

## Why it belongs in the monorepo ICM surface

- Direct empirical validation of the same structural thesis that `docs/icm/` already applies (Layer-0 catalog, selective loading, one-way dependencies, human-inspectable state).
- Supplies the missing “number” for context-cost arguments already present in Content-Agent-Routing-Promptbase patterns.
- Harness (`lme-icm/`) and run artifacts are reference-only; they are **not** imported into runtime or CI control plane.

## Native use

| Surface | Role |
|---|---|
| `docs/icm/objects/knowledge/cost-of-remembering.md` (this card) | Operator-facing summary + citation |
| `refTemplates/smods/cost-of-remembering_fork` | Shallow submodule; read harness / brains / paper source when measuring memory cost |
| `docs/icm/_meta/method-coverage.md` | Coverage row |
| Future: `docs/icm/processes/memory-cost-probe.md` | Optional process card for local probe runs (out of this change) |

## Boundary

- No automatic execution of `run_cost.py` or paper rebuild inside monorepo gates.
- No LongMemEval data or API keys committed.
- Customizations stay in the owned fork; monorepo only advances the Gitlink after review.

## Citation

```bibtex
@misc{vanclief2026costofremembering,
  title  = {The Cost of Remembering: Filesystem Memory Against Long Context
            on {LongMemEval}},
  author = {Van Clief, Jake and McDermott, David and Kumar, Kay},
  year   = {2026}
}
```

Also cite Wu et al. (LongMemEval, ICLR 2025) and the ICM paper (arXiv:2603.16021).
