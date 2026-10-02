# Bank Naming Convention

## Structure

    <project>::<method>::<vendor>::<family>::<model>::<settings>::<role>::<comp>

## Slots

| Slot | Meaning | Examples |
|------|---------|----------|
| project | owning repo or tenant | termux-monorepo |
| method | how the bank is used | mvt, primary |
| vendor | LLM API provider | google, openrouter, anthropic, groq |
| family | model product family | gemini, qwen, llama, gemma, claude |
| model | specific checkpoint | gemini-3.5-flash-lite, qwen3.8-27b |
| settings | tier / variant / reasoning | flex, thinking, standard |
| role | pipeline role | producer, critic, verifier, merger |
| comp | composition hash (config snapshot) | base, abc123 |

## Examples

    termux-monorepo::mvt::google::gemini::gemini-3.5-flash-lite::standard::producer::base
    termux-monorepo::mvt::openrouter::qwen::qwen3.8-27b::free::producer::base
    termux-monorepo::mvt::openrouter::google::gemma::gemma-4-26b-a4b-it::free::critic::base
    termux-monorepo::primary

## Why vendor is separate from family

`gemini` is a Google product. `qwen` is an Alibaba product. When accessed
via OpenRouter, the vendor (who bills) is OpenRouter, but the family is
still Qwen. Both layers matter: vendor controls quota, family controls
behavior.

## Role names

- producer  — extracts facts from source text
- critic    — scores/judges produced facts
- verifier  — checks fact accuracy against source
- merger    — consolidates overlapping facts

Role names are NOT classifier model names. Mev/Jev/Kev/Laya are classifier
products (Qwen fine-tunes); they are not roles. A classifier may serve the
critic role, but the role is distinct from the model.

## Migration

Pre-doctrine banks used `deepagent::mvt::<provider>::<model>::<role>::<comp>`.
Renamed to `<project>::mvt::<vendor>::<family>::<model>::<settings>::<role>::<comp>`
in this revision.
