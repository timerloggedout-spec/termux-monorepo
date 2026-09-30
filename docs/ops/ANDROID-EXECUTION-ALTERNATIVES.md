# Android / Termux execution alternatives

Issue: #760

## Decision frame

Desktop Commander remains a useful compatibility target, but the hosted Remote Desktop Commander path is not the only execution plane. The Android hub should expose a stable internal execution contract and permit multiple adapters.

```text
                    DeepCLI / MCP clients
                             |
                    execution contract
                             |
              +--------------+--------------+
              |              |              |
          DC adapter     Termux MCP      Shizuku MCP
              |              |              |
              +--------------+--------------+
                             |
                    policy / audit broker
                             |
                  +----------+----------+
                  |                     |
               Termux                Shizuku
               shell                 rish UID
```

## Candidate matrix

| Candidate | Termux | Shizuku | MCP | Local-first | Tailscale fit | Primary role |
|---|---:|---:|---:|---:|---:|---|
| Desktop Commander upstream/local | yes | indirect | yes | yes | yes, via own transport | compatibility/reference |
| Desktop Commander *_fork | yes | adapter | yes | yes | yes | controlled compatibility fork |
| shizzgar/shizuku-mcp | yes | yes | yes | yes | yes | Android privileged adapter |
| termuxgpt/termux-mcp | yes | no/Termux API | yes | yes | yes | lightweight Termux execution |
| TecnicalBot/termux-mcp | yes | optional | yes | yes | yes | security-oriented Termux broker |
| mcpshell | yes | yes | yes | yes | yes | unified Android/Ubuntu/Shizuku surface |
| SSH over Tailscale | yes | no | adapter required | yes | native | durable transport fallback |
| purpose-built broker | yes | optional | yes | yes | native | canonical long-term control plane |

## Fork lane

The fork should be treated as a compatibility product rather than a permanent divergence:

1. Pin upstream commit/version.
2. Reproduce the Android/Termux failure before modification.
3. Repair dependency/package-layout failures first.
4. Add Android-specific CI/smoke coverage.
5. Make safety policy immutable from agent-facing tools.
6. Add MCP conformance tests.
7. Add Streamable HTTP behind Tailscale, not public exposure.
8. Add health/readiness and process recovery.
9. Keep upstream synchronization and patch provenance explicit.

A current upstream Android/Termux issue reports remote startup failure in v0.2.48 during Supabase configuration fetch with HTTP 403. Upstream also has an open MCP conformance report identifying handshake/version-negotiation failures. These are reasons to maintain a fork lane, not proof that the whole project is unsuitable.

## Recommended topology

Use a broker/adapter model:

```text
DeepCLI
  |
MCP execution contract
  |
Termux hub broker
  +-- DC adapter
  +-- Termux-MCP adapter
  +-- Shizuku-MCP adapter
  +-- SSH/Tailscale adapter
  |
policy gate
  +-- command allowlist
  +-- path roots
  +-- privileged-operation gate
  +-- audit/event ledger
  +-- credential redaction
```

The broker must distinguish:

- transport health
- shell execution health
- privileged Android health
- agent/session health
- evidence/telemetry health

No candidate becomes the canonical route until it passes the same smoke contract.

## 2FA boundary

Authentication secrets remain outside the general shell tool. The broker may request a narrowly scoped authentication assertion, but TOTP seeds, password-store contents, GPG private keys, and raw secrets must not enter agent telemetry or general command output.

## First experiments

1. Repair and pin the Desktop Commander fork.
2. Run shizzgar/shizuku-mcp locally with Shizuku + Termux:API.
3. Run termuxgpt/termux-mcp in native MCP/Streamable HTTP mode.
4. Evaluate TecnicalBot/termux-mcp for its default-deny, allowlist, sandbox and audit model.
5. Evaluate mcpshell as the unified shell + proot + rish candidate.
6. Establish SSH-over-Tailscale as the boring recovery path.
7. Compare all candidates with one identical execution smoke contract.

## Promotion rule

Do not replace Desktop Commander merely because it is currently broken. Promote an alternative only when it produces better evidence across reliability, security boundary, recovery, latency, Android capability coverage, and operational complexity.
