# multi-ai-cli

`multi-ai-cli` provides a lightweight CLI surface for the repository’s existing provider runtimes. The `providers` commands add a **non-secret, resumable checklist** for selecting providers and completing their provider-owned local connection paths.

> The checklist does not store or print credentials, browser profiles, cookies, provider-session identifiers, or raw provider responses. Existing runtimes remain responsible for their own local session state.

## Start a connection checklist

Run commands from the repository root, substituting your preferred Python entrypoint where necessary.

```bash
python3 multi-ai-cli/cli.py providers select deepseek mistral gemini claude colab
python3 multi-ai-cli/cli.py providers status
python3 multi-ai-cli/cli.py providers next
```

Select only the providers you intend to use. The order supplied to `select` becomes the resume order.

| Command | Purpose |
|---|---|
| `providers list` | Display the catalog, capability classification, and local checklist state. |
| `providers select <ids...>` | Choose an ordered provider subset. |
| `providers next` | Display the next provider and its manual connection guidance. |
| `providers begin <id> [--account alias]` | Mark a provider as being connected and print its provider-owned local steps. |
| `providers complete <id>` | Record that the user completed the local provider flow. |
| `providers skip <id>` | Defer a provider without removing it permanently. |
| `providers retry <id>` | Return a skipped or failed provider to the queue. |
| `providers account <id>` | Show the provider’s account-return page and mark it for later resumption. |
| `providers status` | Render the selected provider states and the next action. |

## Returning to skipped providers

A skipped provider remains in the local checklist. When ready, use:

```bash
python3 multi-ai-cli/cli.py providers retry mistral
python3 multi-ai-cli/cli.py providers begin mistral
```

The checklist is written under `~/.multi-ai-cli/` with restrictive local permissions. Use `--state-dir <directory>` for a test or an alternate non-secret checklist location.

## DeepSeek integration boundary

The `deepseek` catalog entry delegates browser-session lifecycle ownership to the selected `deepcli` runtime. The checklist may show the pre-existing user-run import helper, but it does not invoke the helper, alter its request mechanics, inspect its output, or duplicate its session state. See [the web-wrapper lineage decision](../docs/DEEPSEEK-IMPLEMENTATION-REVIEW-2026-08-14.md) and [the hub proposal](../docs/proposals/active/multi-ai-webwrapper-hub/source.md).

## Development checks

```bash
cd multi-ai-cli
python3 -m unittest tests/test_provider_checklist.py -v
```
