# System One Catalog — classifier and decision-system map

This catalog describes external System One-compatible decision models and their serving ecosystem. The local `deepcli.observatory` modules use Mev/Jev/Kev/Laya as **role labels**. The external projects with overlapping names are independently authored models, runtimes, or services. The shared labels create a naming collision; they do not establish shared code, weights, ownership, or equivalent behavior.

## Four identity layers

| Layer | Identity | Example | What it means |
|---|---|---|---|
| Local role | A capability slot in a workflow | producer, critic, verifier, merger | A contract that can be implemented by multiple candidates |
| Local implementation | Repository code implementing a role | `observatory/mev.py`, `jev.py`, `kev.py`, `laya.py` | The current DeepCLI baseline implementation |
| External candidate | Independently maintained model or service | TypeSafe Jev, Jared Palmer Kev, ConvAI Laya, Mellow AI Mev | A candidate to discover, adapt, route to, and evaluate |
| Integration adapter | Protocol bridge to a candidate | `llm/adapters/systemone.py` | A transport/protocol integration; it does not imply role equivalence |

The tournament records these layers separately. Every candidate receives a stable candidate ID, a source/project identity, a version or immutable revision, an adapter identity, a capability declaration, and an evidence record.

## Catalog inventory

- Machine-readable catalog: `config/system_one_catalog.json`, schema `system-one-catalog/1`.
- Census source: `docs/proposals/active/system-one-classifier-census/`.
- The catalog currently reports 88 entries across four inventory layers: 61 model families, 16 adapters, 7 runtimes, and 4 directories. These are heterogeneous inventory entries, not 88 interchangeable classifiers.
- Fleet states: `referenced` → `catalogued` → `trial_candidate` → `evaluated`. Each transition requires its own evidence.

## Name-collision register

| Local role label | Local implementation contract | External name match in the catalog | Evidence-backed distinction |
|---|---|---|---|
| Mev | `mev.produce`: calls a text-generation adapter and captures response, tokens, latency, and cost | S1-04 Mev (recruiting); S1-05 mev (Mellow AI) | Two separate external entries. The local producer role is neither model. |
| Jev | `jev.critique`: sends artifact text and rubric to an LLM judge and parses rubric scores | S1-01 Jev (TypeSafe AI) | The local critic uses a generic chat adapter. TypeSafe Jev is a typed decision model/service. |
| Kev | `kev.verify`: computes exact/token-F1 comparison against a supplied reference | S1-02 Kev (Jared Palmer) | The local verifier is deterministic token/exact matching. External Kev is a learned decision-model family with a serving stack. |
| Laya | `laya.synthesize`: weighted rank of aligned artifact/Jev/Kev evidence | S1-03 Laya (ConvAI Innovations) | The local merger is a weighted reducer. External Laya is an encoder decision family. |

**Important correction to the integration story:** `llm/adapters/systemone.py` implements typed `decide(state, questions)`. Its `ask(prompt)` method deliberately raises `NotImplementedError`. Therefore System One-compatible servers can enter the dedicated decision/evaluation lane through `observatory/decide.py`; the adapter is not a generic text-generation adapter and does not make an external server a drop-in Mev producer or Jev chat judge. The current `decide_check` path is a post-trial check of a text (or a decide-only check), not yet a candidate-ID-aligned per-artifact Kev replacement or an interchangeable Laya merger.

## Evaluation lanes

1. **Generation lane:** text-producing models through Mev-compatible `ask(prompt)` adapters.
2. **Critique lane:** independent judges through Jev-compatible `ask(prompt)` adapters, with producer/judge independence recorded.
3. **Reference-verification lane:** deterministic and learned verifiers through an explicit verifier contract. The current local Kev is token-F1/exact; external decision models require an adapter that maps their typed output to the same versioned evidence schema.
4. **Typed-decision lane:** System One-compatible candidates through `decide(state, questions)`. Record model ID, endpoint/runtime, question schema, raw answers, calibration/evidence, latency, and provenance.
5. **Composition lane:** candidate graphs that combine these capabilities. Compare graph behavior against matched cohorts, rather than assuming similarly named components are equivalent.

## External candidates and infrastructure

The catalog and census preserve project attribution, source URLs, model/runtime/adapter layers, and fleet state. Examples include TypeSafe Jev, Jared Palmer Kev, ConvAI Laya, the two Mev entries, simple-jev, Ollaya, laya.cpp, sys1, and classifier.dev. Treat source descriptions and reported capabilities as discovery evidence; promote candidates only after a pinned artifact, reproducible setup, protocol check, and matched trial.

## Operational status: local Jev versus external Jev

"Active" requires a scope. The classifier-estate feed snapshot (generated
2026-11-02) marks the local observatory quartet live via dispatch. The
Tier-1 recon says the quartet is dispatch-only: a human starts a trial;
there is no standing trigger classifying repository LLM traffic.

| Candidate | Recorded state | Operational meaning |
|---|---|---|
| Local `deepcli.observatory.jev` | Incumbent role implementation; dispatch-only baseline | The local rubric critic participates when a trial is dispatched. It is not a continuously running classifier service. |
| External TypeSafe Jev (S1-01) | Catalogued in the machine catalog; blocked-paid in census trial records | The hosted route was not executed under the standing `free_only` gate. A paid-route owner decision is required before a trial. |
| External ConvAI Laya (S1-03) | Evaluated | Self-hosted simple-jev trial returned quality 0.7139 and grounding 0.7692 on the recorded trial state. These are trial-specific observations, not a general ranking. |
| External Jared Palmer Kev (S1-02) | Trial candidate | Checkpoints are PEFT LoRA adapters plus a classification head; a faithful trial requires the compatible serving stack or a deliberate composition shim. |
| External recruiting Mev (S1-04) | Referenced / not runnable | The census record identifies no runnable release. |
| External Mellow AI mev (S1-05) | Trial candidate / host blocked | A full model exists; the recorded local attempt was constrained by download egress and host memory. |

The detailed run evidence and paid-route gate live in
`docs/proposals/active/system-one-classifier-census/TRIALS.md`. The
candidate registry stores operational state separately from catalog
readiness, so "catalogued", "available adapter", "dispatch active" and
"evaluated" remain distinct facts.

## Tournament requirements

- Assign each local role implementation and external project a distinct immutable identity.
- Track name aliases as metadata; never use a display name as a unique key.
- Compare candidates on capability-specific task cohorts and retain raw outputs.
- Compare compositions separately from individual candidates.
- Distinguish protocol compatibility from semantic equivalence.
- Preserve unavailable, failed, and unmeasured evidence as explicit states.
- Keep source revision, model revision, runtime, adapter, prompt/rubric, and environment hashes in each trial receipt.
