# Provider Capability Registry

> **Status:** SPEC (P1)

Every provider implements identity, capabilities, availability, authenticate, create_session, send, stream, history, export, health.

Capability flags: installed, authenticated, session_create/resume, streaming, history, attachments, thinking, web_search, code_execution, browser_tls, export, indexing, dispatch.

`curl_cffi` ≠ stdlib `requests`. If `requires_browser_tls` and only requests available → fail clearly.
