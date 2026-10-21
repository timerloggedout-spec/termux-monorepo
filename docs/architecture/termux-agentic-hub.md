# Termux Agentic Hub Architecture

## Purpose

The Termux Agentic Hub gives authorized agents useful Android administrative capability without exposing the phone as an unauthenticated public shell or allowing free-form commands to flow from repository events into Termux. It targets the BLU B160V as the first runtime and keeps its resource profile deliberately small.

## Runtime topology

```text
GitHub pull request / controlled job envelope
                 |
                 v
     hub_mcp schema + capability validation
                 |
                 v
      local Termux worker (single concurrency)
                 |
                 v
named, shell-free capability invocation
                 |
                 v
canonical Termux MCP server / Termux:API
                 |
                 v
redacted result envelope and repository audit trail
```

GitHub is the source, review, and CI coordination plane. The Android device is the execution plane. Tailscale management is a separate control-plane capability; it can report device state or manage permitted nodes but does not itself carry an MCP session from an isolated agent environment to the device.

## Adapter map

| Component | Role | Version-one status |
|---|---|---|
| `termux-mcp-server_fork` | Canonical device-side MCP server. | Executable only behind `hub_mcp` policy and authenticated OpenSSH. |
| `mcp-android-ssh_fork` | SSH adapter/reference. | Retained as a non-executable reference while host-key policy is hardened. |
| `term_mcp_deepseek_fork` | DeepSeek compatibility adapter. | Retained as a non-executable template; persistent-shell behavior is not exposed. |
| `hub_mcp` | Central policy, validation, replay prevention, and result-redaction package. | The only permitted route from a structured job to a local operation. |

No symlink is used as an execution policy. Adapters are referenced declaratively in `hub_mcp/adapters.py`, which makes role changes reviewable and testable.

## Capability model

| Level | Meaning | Version-one availability |
|---|---|---|
| Observe | Read state without changing it. | Active for battery, Wi-Fi, repository, and submodule status. |
| Operate | Run bounded, deterministic maintenance checks. | Active only for repository and Termux smoke gates. |
| Change | Modify device or tracked state. | Defined but inactive pending an auditable approval interface. |
| Critical | Delete, expose network services, modify tailnet policy, or send external communications. | Defined but always rejected by version one. |

The policy accepts a fixed capability identifier and zero or schema-defined arguments. It never accepts a caller-provided executable, command fragment, shell string, unbounded filesystem path, or network destination.

## Job protocol

A valid job includes a UUID, issue/expiry times, requested identity, named capability, arguments object, approval tier, and optional human approval marker. Validation rejects stale jobs, future-issued jobs, job lifetimes longer than 24 hours, unknown fields, unknown capabilities, insufficient privilege, and replayed UUIDs. A processed-job store is written atomically in untracked local state.

Results include the job digest, result digest, bounded output, exit state, and timestamps. Common credential-shaped values are redacted before serialization. Result envelopes are reviewed by CI before they are accepted as audit evidence.

## Transport boundary

The initial hub does not promise interactive remote MCP access. It can safely execute a structured job locally and report an auditable result over outbound HTTPS. A later direct transport may use a user-controlled private bridge or authenticated tunnel, but it must preserve key-only SSH, the SSH host-key pin, the same `hub_mcp` policy, and the single-worker limit.

## Explicit exclusions

The hub does not automate interactive account MFA, capture OTPs or second-factor secrets, reverse engineer user login sessions, publish a public SSH port, or run an unsupported Android GitHub Actions runner. Provider integrations must use provider-supported machine credentials and explicitly scoped permissions.
