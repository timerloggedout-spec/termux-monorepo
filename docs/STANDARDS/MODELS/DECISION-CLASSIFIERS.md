# System One Decision Classifiers

A model category distinct from LLM generators. Input = state + typed
questions. Output = typed decisions with calibrated probabilities.
Never generates text.

## Reference product

**Jev** — TypeSafe AI, closed. Primitives:

| Primitive | Returns |
|---|---|
| Choice    | one option + probability distribution |
| Noul      | yes/no as a probability |
| Score     | rating on a defined scale |

Pricing $0.042/M input tokens, output unmetered. Latency 70–500ms.

## Open clones — split by architecture, not role

| Model | Author | Architecture | Size |
|---|---|---|---|
| Laya | Convai Innovations | ModernBERT-large + decision head, PPO | 421M |
| Kev | Jared Palmer (Vercel) | LoRA + pointer readout on Qwen | 0.8B–9B |
| Mev | Mellow AI | Qwen3.5-4B fine-tune | 4.5B |
| SemIf | AlexWortega | Qwen3.5 + 3-class NLI classifier | 0.6B–4B |
| Bespoke Nimble | Bespoke Labs | LoRA on Qwen3.5-9B | 9B |
| Jevlike | community | byte-embedding option-attention | 40K |
| OpenJev | community | DiffusionGemma | — |

## Architectural families

- **Encoder-only (Laya)** — ModernBERT + decision head. Logits read
  directly, no text generation. Fastest, smallest.
- **LLM with decision head (Kev, Mev, SemIf, Bespoke Nimble)** — keep
  the base LLM, add a readout head or pointer structure so one pass
  serves multiple typed questions.
- **Token-classifier (SemIf)** — 3-class NLI on top of Qwen3.5.
- **Novel (Jevlike, OpenJev)** — byte embeddings, diffusion backbones.

## Where they fit in this stack

**Decision layer**, not extraction layer. The two layers do different
things:

| Layer | Job | Example models |
|---|---|---|
| Extraction | pull facts from text | Gemini, Llama, Qwen |
| Decision | score/judge/route/merge | Jev, Laya, Kev, Mev |

Current `observatory/` package uses mev/jev/kev/laya as role labels:

```

mev  -> producer
jev  -> critic / judge
kev  -> verifier
laya -> merger

```

That is a **borrowing** of the classifier names as namespace, not a
claim that the observatory roles correspond 1:1 with classifier
architectures.

## Implementation lanes

Each classifier is an independent axis. Every lane can be extended and
compared via the same MVT substrate used for LLM extraction:

### Lane A · Extend a classifier
- New head on an existing base (e.g. Kev-style LoRA on a different Qwen)
- New base with an existing head (e.g. Laya head on ModernBERT-XL)
- Full custom (OpenJev-style novel backbone)

### Lane B · Compare classifiers
- Same input state, same typed question, one classifier per bank
- Bank shape: `deepagent::mvt::decide::<classifier>::<comp>`
- Metrics: calibration (Brier, ECE), latency, per-question agreement

### Lane C · Stack with extraction
- Extraction model produces facts
- Classifier scores/filters/routes facts
- Two banks per pipeline cell:
  - `deepagent::mvt::extract::<provider>::<model>::<comp>`
  - `deepagent::mvt::decide::<classifier>::<comp>`

### Lane D · Wire as Hindsight callbacks
- Score filter — classifier gates which facts enter a bank
- Route select — classifier picks target bank per fact
- Merge scorer — classifier ranks competing merge candidates

## Extension template

New classifier entry in the observatory registry:

```python
class DecisionClassifier:
    name: str                # registry key, e.g. "mev-qwen4b-v1"
    family: str              # encoder_only | llm_head | nli | novel
    base: str                # hf model id
    head: str                # decision | pointer | nli_3class
    input_contract: dict     # {"state": str, "questions": list[dict]}
    output_contract: dict    # {"choices": [...], "probability": float}
    latency_ms_p50: int
    size_params: int

    def decide(self, state: str, question: dict) -> dict:
        """Return typed decision. Never return free text."""
        raise NotImplementedError
```

DO statements

· DO keep classifier banks separate from extraction banks.
  Namespaces: decide::* vs extract::*.
· DO measure calibration, not just accuracy. The value of a
  classifier is in the probability, not the argmax.
· DO one classifier per bank per comp_hash. MVT across classifiers
  is the comparison substrate.
· DO NOT use a classifier's output as if it were an extracted fact.
  They live in different namespaces for a reason.
  MD

echo "  wrote: $DOCS/MODELS/DECISION-CLASSIFIERS.md"

═══════════════════════════════════════════════════════════════

2 · Verify ingest/redirect wiring — read-only

═══════════════════════════════════════════════════════════════

echo
echo "=== WIRING PROBE ==="
_TMP="${TMPDIR:-/data/data/com.termux/files/usr/tmp}"
cat > "$_TMP/wire.sh" <<'W'
#!/usr/bin/env bash
set -u
echo "########## 1 · pipeline state ##########"
pgrep -af 'sovereign-run|mvt-seed' | head -4
echo "--- mvt-seed.log tail ---"; tail -12 /tmp/mvt-seed.log 2>/dev/null
echo "--- retain-timing (any bank) last 5 ---"
grep 'retain-timing' /tmp/hs.log 2>/dev/null | tail -5

echo
echo "########## 2 · public URL + auth ##########"
_p=$(pgrep -f 'hindsight-api --port 8888' | head -1)
_k=$(tr '\0' '\n' < /proc/$_p/environ | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)
for url in \
  "http://localhost:8888/health" \
  "https://hs-0345-7vj97vj49jp9cg45-8888.app.github.dev/health"
do
  code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>/dev/null || echo 000)
  echo "  $url -> $code"
done

echo
echo "########## 3 · banks :8888 (public, bearer) ##########"
curl -sS --max-time 8 -H "Authorization: Bearer $_k" 
  https://hs-0345-7vj97vj49jp9cg45-8888.app.github.dev/v1/default/banks 2>/dev/null 
 | python3 -c "
import json,sys
try:
d=json.load(sys.stdin)
for b in sorted(d.get('banks',[]), key=lambda x: x['bank_id']):
print(f"  {b['bank_id']}  facts={b.get('fact_count',0)}")
print(f'  total={d.get("total",0)}')
except Exception as e: print('  err:',e)
"

echo
echo "########## 4 · cloud endpoint reachable? ##########"
curl -sS -o /dev/null -w '  cloud /health -> %{http_code}\n' 
  --max-time 8 https://api.hindsight.vectorize.io/health 2>/dev/null || echo "  cloud DEAD"

echo
echo "########## 5 · git substrate ##########"
echo "  branch: $(git -C ~ branch --show-current 2>/dev/null)"
echo "  memory-bank branch:"
git -C ~ ls-remote origin memory-bank 2>/dev/null | head -2

echo
echo "########## 6 · Actions workflows present ##########"
ls -la ~/.github/workflows/hindsight.yml ~/.github/workflows/mirror-openrouter.yml 2>/dev/null

echo
echo "########## 7 · pending/ (FROZEN writes) ##########"
ls -la ~/.deepcli/pending/ 2>/dev/null || echo "  no pending dir"

echo
echo "########## 8 · hs-parity recent ##########"
tail -6 ~/.deepcli/logs/hs-parity.jsonl 2>/dev/null
W
chmod +x "$_TMP/wire.sh"
gh codespace cp -c "$_cs" -e "$_TMP/wire.sh" remote:/tmp/wire.sh >/dev/null 2>&1
gh codespace ssh -c "$_cs" -- bash /tmp/wire.sh 2>&1 | head -80

═══════════════════════════════════════════════════════════════

3 · Commit doc

═══════════════════════════════════════════════════════════════

cd ~ || exit 1
git add "$DOCS/MODELS/DECISION-CLASSIFIERS.md"
git -c user.name="timerloggedout" -c user.email="timerloggedout@gmail.com" 
  commit -m "docs(hindsight): decision classifier taxonomy + implementation lanes

System One decision models are a distinct category from LLM generators.
Jev (TypeSafe AI) reference + 7 open clones (Laya, Kev, Mev, SemIf,
Bespoke Nimble, Jevlike, OpenJev) documented with architecture, size,
and four implementation lanes (extend, compare, stack, wire-as-callback).

Corrects conflation: observatory mev/jev/kev/laya role labels are a
naming borrowing, not architecture identity. Decision layer separated
from extraction layer in bank naming (decide:: vs extract::)." 2>&1 | tail -2
git push origin HEAD:feat/gh-actions/deepseek-integrates-itself 2>&1 | tail -1

echo
echo "=== DONE ==="

## Decision record schema

Every classifier invocation writes one record. Selection alone is
insufficient — the probability scale is the signal. Schema lives at
`docs/STANDARDS/MODELS/decision-record.schema.json`.

Required fields: ts, classifier, family, bank_id, input_state_hash,
question, selection, probability, distribution, calibration,
latency_ms, comp_hash.

Calibration ledger: `~/.deepcli/logs/decisions/<classifier>.jsonl`.
Aggregate nightly: Brier, ECE, temperature rescale.
