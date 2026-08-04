# Provider Capability Registry

> **Status:** SPEC (P1)
> **Depends on:** Session SSOT

## Interface (target)

Every provider implements:

```
Provider
├── identity
├── capabilities
├── availability()
├── authenticate()
├── create_session()
├── send()
├── stream()
├── history()
├── export()
└── health()
```

Result object:

```
ProviderResult
├── provider
├── account
├── session_id
├── message_id
├── status
├── response
├── error
├── usage
└── provenance
```

No provider invents its own session-ID semantics.

## Capability flags

```
ProviderCapabilities
├── installed
├── authenticated
├── session_create
├── session_resume
├── streaming
├── history
├── attachments
├── thinking
├── web_search
├── code_execution
├── browser_tls          # curl_cffi-class transport
├── export
├── indexing
└── dispatch
```

Example truth rows (generate; do not hand-maintain forever):

| Provider | installed | auth | session | stream | history | browser_tls | status |
|----------|-----------|------|---------|--------|---------|-------------|--------|
| deepcli  | ✓ | ? | ✓ | ✓ | ✓ | ✓ | active |
| mistral  | ? | ? | ? | ? | ? | ? | active |
| claude   | ? | ? | ⚠ | ? | ⚠ | ? | incomplete |
| colab    | ? | ? | ⚠ | ? | ⚠ | ✗ | incomplete |
| gemini   | ? | ? | ? | ? | ? | ? | scaffold |
| openai   | ? | ? | ? | ? | ? | ? | scaffold |

## Transport note (PR #10)

`curl_cffi` ≠ stdlib `requests`.

```
Transport:
  curl_cffi  — preferred; feature set: browser TLS
  requests   — compatibility fallback; standard HTTP

Operation declares: requires_browser_tls = true|false
If true and only requests available → fail clearly, do not pretend equivalence.
```

## Anti-patterns (from TER-9 bug farm)

- Session ID precedence bugs that drop caller-provided IDs
- Undeclared dependencies that fail at import
- Cookie paths crossing provider boundaries
- Mutating persistent session headers with one-off auth
- Shadowing builtins (`list` as Click command)
- Package dir `multi-ai-cli` vs import `multi_ai_cli` mismatch
