# DeepAgent

Agent loop with direct in-process imports — no HTTP hop.

## Usage

    deepagent-cli [flags] "<task>"
    deepagent-cli --task-file <path> "<optional override>"

## Flags

| Flag | Effect |
|---|---|
| `--dry-run` | Print planned steps; no tool calls |
| `--fresh` | Ignore stored session; start new |
| `--task-file <path>` | Load task from file; path doubles as session key |
| `-h, --help` | Print usage |
| `-v, --verbose` | Trace tool dispatch |

## Environment

| Var | Default | Meaning |
|---|---|---|
| `AGENT_MAX_STEPS` | 16 | Step ceiling per run |
| `AGENT_AUTOFIX` | 1 | Enable auto-recovery |
| `AGENT_AUTO_FEEDBACK` | 0 | Emit feedback after reply |
| `HINDSIGHT_BASE_URL` | unset | Enables memory tools |
| `HINDSIGHT_BANK_ID` | unset | Target bank |
| `DSH_USE_DEEPAGENT` | 0 | Route /v1/agent through deepagent |

## Memory tools

When `HINDSIGHT_BASE_URL` is set, exposes three tools:
`hindsight_retain`, `hindsight_recall`, `hindsight_reflect`.
Unset → agent runs stateless.

## Sessions

Task identity = `sha256(path + first 500 chars)`.
Same task → same session. Ledger at `~/.deepcli/sessions.json`. TTL 30 days.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Completed (FINISHED marker present) |
| 1 | Recoverable error (retry) |
| 2 | Fatal (missing imports, bad task) |

## Invocation paths

    deepagent-cli "..."            # direct
    dsh run "..."                  # via /v1/agent SSE
    GH Actions @deepseek <comment> # via broker
