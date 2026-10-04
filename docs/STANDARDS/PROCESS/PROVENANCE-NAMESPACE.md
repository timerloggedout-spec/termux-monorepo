# Provenance namespace

Every attributed action carries a namespace string that identifies
the layer that produced it, following the same shape as the bank
naming convention.

## Form

    provider::modelfamily::model::settings::role{moniker}

Fields:

| Field        | Values                                            |
|--------------|---------------------------------------------------|
| provider     | deepseek, google, openrouter, anthropic, ...      |
| modelfamily  | deepseek-v4, gemini, qwen, llama, ...             |
| model        | v4-pro, flash-lite, 3.5-flash, 27b, ...           |
| settings     | default, thinking, instant, lite, standard, ...   |
| role         | recon, plan, forge, sentinel, rollup,             |
|              | hygienist, scribe, orchestrator                    |
| {moniker}    | optional short tag; same as role when omitted     |

## Examples

    deepseek::deepseek-v4::v4-pro::thinking::forge
    google::gemini::flash-lite::lite::recon
    openrouter::qwen::27b::free::sentinel
    deepseek::deepseek-v4::v4-pro::thinking::orchestrator

For sub-lane distinction, append `#{moniker}`:

    deepseek::deepseek-v4::v4-pro::thinking::forge#chat
    deepseek::deepseek-v4::v4-pro::thinking::forge#dispatch-42

## Where it appears

1. **Git commit trailer** (in the message body, not the Author field):
       Provenance-Role: forge
       Provenance-Namespace: deepseek::deepseek-v4::v4-pro::thinking::forge#chat

2. **provenance.jsonl row** — the `namespace` field.

3. **mvt-score trial** — `attribution.namespace`.

4. **bank naming** — the same convention as
   `termux-monorepo::mvt::<vendor>::<family>::<model>::<settings>::<role>::<comp>`,
   applied to provenance events rather than memory.

## Why moniker-only

The email channel is a shared PAT. It cannot distinguish lanes.
The namespace string does. Every writer uses the same credential;
the namespace is the only honest distinguishing signal in the
artifact itself.

## Never in the namespace

- personal email addresses
- token prefixes
- raw session ids longer than 8 chars (use prefix)

## Parser contract

A provenance parser reads:
- git trailer `Provenance-Namespace`
- provenance.jsonl `namespace` field
- mvt-score trial `attribution.namespace`

All three use identical format. Any tool that emits attribution
must produce this string. Any tool that consumes attribution
parses this string. One shape.
