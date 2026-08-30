# NSE-022 — Lambda Lang (A2A atoms) and non-collapse vs Category Theory

## Intent

Record the research boundary between **Lambda Lang / agent-composition calculi** (including A2A protocol atoms) and the category-theoretic notation formalized in NSE-021.

Semantic **non-collapse** is mandatory: shared glyphs or composition metaphors do not imply identical semantics.

## Observed research signals (evidence, not adoption)

- Typed agent-composition calculi (e.g. λ_A / lambda-agent frameworks) embed graph, role, SDK, multi-agent, and low-code paradigms as fragments; they supply formal syntax, type systems, and (in some cases) metatheory.
- Classical atomic lambda calculi with explicit sharing / stepwise duplication (Gundersen–Heijltjes–Parigot lineage).
- Duality of λ-abstraction / coabstraction (exponentials vs coexponentials) as a separate control/computation axis.
- Google A2A (Agent2Agent) protocol: discovery, negotiation, long-running collaboration over HTTP/JSON-RPC — an interoperability *surface*, not a replacement for CT Hom-sets or IR morphisms.

## Non-collapse rules

| Surface | May resemble | Must NOT be treated as |
|---------|--------------|-------------------------|
| Agent handoff / `>>` / pipe | CT composition / `;` / `>>=` | Identical morphism composition in a single category |
| A2A Agent Card / capability | Hom-set or functor | Machine-checked CT structure |
| λ-abstraction / tool call | Exponential object `Y^X` | Proof-relevant exponential in Mathlib sense |
| Multi-agent fixpoint / turn | Natural transformation | CT naturality square without evidence |

## Canonical IR linkage (NSE-015)

- Prefer mapping agent-composition atoms into the existing IR only after an explicit adapter:
  - `O:<id>`, `M:<src>:<tgt>:<label>`, `COMP(...)`, `ID(...)`, `F:...`, `NAT:...`
- A2A / Lambda Lang atoms remain **domain-specific syntax** until a typed correspondence is proven and recorded in the evolution ledger (NSE-008).

## Lane separation

- Notation-sets lane (this proposal) owns vocabulary + non-collapse rules.
- Runtime agent protocols (A2A, multi-ai-cli, SHE dispatch) own execution contracts.
- Do not promote Lambda Lang fragments into master runtime without dual-gate green + extract PR.

## Status

Specification-only. No runtime code in this extract.
