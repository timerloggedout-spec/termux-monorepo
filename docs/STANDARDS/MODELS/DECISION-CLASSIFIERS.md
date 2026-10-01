# System One Decision Classifiers

A model category distinct from LLM generators. Input = state + typed
questions. Output = typed decisions with calibrated probabilities.
Never generates text.

## Reference product

**Jev** — TypeSafe AI, closed. Primitives:

| Primitive | Returns |
|---|---|
| Choice | one option + probability distribution |
| Noul   | yes/no as a probability |
| Score  | rating on a defined scale |

Pricing $0.042/M input tokens, output unmetered. Latency 70-500ms.

## Open clones — split by architecture, not role

| Model | Author | Architecture | Size |
|---|---|---|---|
| Laya | Convai Innovations | ModernBERT-large + decision head, PPO | 421M |
| Kev | Jared Palmer (Vercel) | LoRA + pointer readout on Qwen | 0.8B-9B |
| Mev | Mellow AI | Qwen3.5-4B fine-tune | 4.5B |
| SemIf | AlexWortega | Qwen3.5 + 3-class NLI classifier | 0.6B-4B |
| Bespoke Nimble | Bespoke Labs | LoRA on Qwen3.5-9B | 9B |
| Jevlike | community | byte-embedding option-attention | 40K |
| OpenJev | community | DiffusionGemma | - |

## Architectural families

- Encoder-only (Laya) — ModernBERT + decision head. Logits read
  directly, no text generation. Fastest, smallest.
- LLM with decision head (Kev, Mev, SemIf, Bespoke Nimble) — keep
  the base LLM, add readout head or pointer structure so one pass
  serves multiple typed questions.
- Token-classifier (SemIf) — 3-class NLI on top of Qwen3.5.
- Novel (Jevlike, OpenJev) — byte embeddings, diffusion backbones.

## Where they fit

Decision layer, not extraction layer:

| Layer | Job | Example models |
|---|---|---|
| Extraction | pull facts from text | Gemini, Llama, Qwen |
| Decision | score/judge/route/merge | Jev, Laya, Kev, Mev |

observatory/ package uses mev/jev/kev/laya as role labels:

  mev  -> producer
  jev  -> critic / judge
  kev  -> verifier
  laya -> merger

That is a borrowing of classifier names as namespace, not a claim
that observatory roles correspond 1:1 with classifier architectures.

## Implementation lanes

Each classifier is an independent axis. Every lane extends and
compares via the same MVT substrate used for LLM extraction.

### Lane A - Extend a classifier
- New head on existing base (Kev-style LoRA on a different Qwen)
- New base with existing head (Laya head on ModernBERT-XL)
- Full custom (OpenJev-style novel backbone)

### Lane B - Compare classifiers
- Same input state, same typed question, one classifier per bank
- Bank shape: deepagent::mvt::decide::<classifier>::<comp>
- Metrics: calibration (Brier, ECE), latency, per-question agreement

### Lane C - Stack with extraction
- Extraction model produces facts
- Classifier scores/filters/routes facts
- Two banks per pipeline cell:
  - deepagent::mvt::extract::<provider>::<model>::<comp>
  - deepagent::mvt::decide::<classifier>::<comp>

### Lane D - Wire as Hindsight callbacks
- Score filter — classifier gates which facts enter a bank
- Route select — classifier picks target bank per fact
- Merge scorer — classifier ranks competing merge candidates

## Extension template

class DecisionClassifier:
    name: str                # registry key
    family: str              # encoder_only | llm_head | nli | novel
    base: str                # hf model id
    head: str                # decision | pointer | nli_3class
    input_contract: dict     # {state, questions}
    output_contract: dict    # {choices, probability}
    latency_ms_p50: int
    size_params: int

    def decide(self, state: str, question: dict) -> dict:
        # Return typed decision. Never return free text.
        raise NotImplementedError

## DO statements

- DO keep classifier banks separate from extraction banks.
  Namespaces: decide:: vs extract::.
- DO measure calibration, not just accuracy. The value of a
  classifier is in the probability, not the argmax.
- DO one classifier per bank per comp_hash. MVT across classifiers
  is the comparison substrate.
- DO NOT use a classifier output as if it were an extracted fact.
  They live in different namespaces for a reason.
