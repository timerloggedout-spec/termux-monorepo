# Siglary — token-cost findings (A2A register)

Filed 2026-11-12 PT · evidence for SIGLARY-STANDARD.md §4 (Cost) · principle ⑤ (accuracy > compression).
🧾 data: [`data/siglary-token-cost.json`](data/siglary-token-cost.json) · 🧾 method: [`scripts/notation/siglary_token_cost.py`](../../../../scripts/notation/siglary_token_cost.py)

## Question
Owner, 2026-11-12: are CHORDS more efficient ∧ effective than OPERATORS for agent-to-agent (A2A) comms?

## Method
- Tokenizers: `o200k_base` (GPT-4o / o-series) ∧ `cl100k_base` (GPT-4 / GPT-3.5) via openai/tiktoken 0.14.0 [1].
- Each register entry (CAVEMAN-MICRO-DENSE-V2.md: Notation classes ∧ Shorthand Domains) is measured against its plain expansion, with a leading space (mid-sentence context).
- One A2A stamp is written in three registers with identical content and measured whole.
- Limits: Anthropic ∧ Google tokenizers are not public. Figures bind for the OpenAI families only and are expected to be directionally similar for other byte-level BPE vocabularies [2][3]. Re-run the script per target model when a tokenizer becomes available.

## Findings (o200k_base · cl100k_base)

| Class | n | form tok | plain tok | cheaper / tie / costlier |
|---|---|---|---|---|
| OPERATORS | 11 | 21 · 17 | 17 · 17 | 1/4/6 · 2/6/3 |
| GLYPHS | 11 | 27 · 29 | 12 · 12 | 0/1/10 · 0/1/10 |
| CHORDS | 30 | 49 · 49 | 31 · 31 | 1/11/18 · 1/11/18 |

| A2A stamp register | chars | tokens o200k · cl100k |
|---|---|---|
| chords ∧ glyphs | 74 | 44 · 42 |
| operators ∧ words | 106 | 32 · 30 |
| plain English | 123 | 31 · 31 |

1. **CHORDS lose on tokens.** Vowel-dropped codes split into sub-word pieces: `mrg` 2 vs `merge` 1, `qta` 2 vs `quota` 1, `wfl` 2 vs `workflow` 1. Only `chk` (1 vs `check run` 2) wins. Chords save characters, ¬ tokens. BPE merges frequent strings into single tokens, so common English words are already compressed [2][4].
2. **GLYPHS lose hardest.** Multi-byte emoji cost 2–3 tokens each, e.g. 🧾 3 vs `receipt` 1, ⛔ 3 vs `blocked` 1. Byte-level BPE encodes rare code points as several byte tokens [2].
3. **OPERATORS are close to parity on tokens and win on scope.** They tie or cost +1 on o200k ∧ are near parity on cl100k (∧ ¬ ∈ ⇒ cost 1). `x++` (2) beats `x stepped up once` (4) ∧ `∀` (1 on cl100k) beats `for all` (2). Their value is unambiguous logical scope (⑤ accuracy), ¬ raw size.
4. **The whole stamp confirms this.** The chords∧glyphs register costs +38% tokens on o200k (44 vs 32) ∧ +40% on cl100k (42 vs 30), against operators∧words, despite having 30% fewer characters. Operators∧words is roughly equal to plain English (32 vs 31 · 30 vs 31).

## Ruling proposed (Linguist ratifies; this file does not decree)
- **A2A machine register = OPERATORS ∧ plain one-token words.** Chords ∧ glyphs are excluded from A2A payloads.
- CHORDS ∧ GLYPHS remain valid in the **human-display register** (Owner chat, dashboards), where glance-speed ∧ character width matter more than tokens.
- `++` stays the step-up operator (Owner: "Operators+= ++").
- §4 Cost gains a token axis: compression is reported in tokens per target tokenizer as well as characters ∧ messages.

## Citations
[1] openai/tiktoken — BPE tokenizer, `o200k_base` ∧ `cl100k_base` encodings. https://github.com/openai/tiktoken
[2] Sennrich, Haddow, Birch (2016). *Neural Machine Translation of Rare Words with Subword Units.* ACL. https://aclanthology.org/P16-1162/
[3] Radford et al. (2019). *Language Models are Unsupervised Multitask Learners* (byte-level BPE, §2.2). https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
[4] OpenAI Cookbook — *How to count tokens with tiktoken.* https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
