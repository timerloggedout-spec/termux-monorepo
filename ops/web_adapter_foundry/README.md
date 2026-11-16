# Web Adapter Foundry — runtime core

Stdlib-only Python. One operation, defined once in a registry, callable
through CLI, JSONL stdin/stdout, an importable API, and (by facade) HTTP/MCP.

```bash
# Catalog of composed upstream tools (verified live 2026-10-22)
python3 -m ops.web_adapter_foundry.waf catalog

# Validate an operation registry
python3 -m ops.web_adapter_foundry.waf validate ops/web_adapter_foundry/examples/example.registry.json

# Bounded probe plan for one operation
python3 -m ops.web_adapter_foundry.waf plan-probes ops/web_adapter_foundry/examples/example.registry.json reports.list

# JSONL stdin transport — one request per line, one response per line
python3 -m ops.web_adapter_foundry.waf serve --registry ops/web_adapter_foundry/examples/example.registry.json
```

```json
{"id": "req-001", "operation": "reports.list", "account_ref": "workspace-a", "input": {"limit": 20}, "execution": {"mode": "auto", "deadline_ms": 15000}}
{"id": "req-002", "operation": "foundry.plan_probes", "input": {"operation_id": "reports.export"}}
```

Rules enforced by the core (not just documented): stdout = protocol only,
no credentials in request bodies (use `account_ref`), promotion moves one
step at a time, write operations never get automatic fallback, direct-http
execution is read-only and allowlist-bound, browser executors report their
external dependency (OpenCLI / rever-browser) honestly instead of faking it.

Full design: `docs/ops/WEB-ADAPTER-FOUNDRY.md` ·
Skill: `.agents/skills/web-adapter-foundry/SKILL.md` ·
Tests: `tests/test_web_adapter_foundry.py`

## APK cross-reference belt (apk_xref)

```bash
python3 -m ops.web_adapter_foundry.apk_xref acquire --source f-droid --package-id com.example.app --out artifacts/app
python3 -m ops.web_adapter_foundry.apk_xref extract app.apk --out extraction.json
python3 -m ops.web_adapter_foundry.apk_xref scan-repo /path/to/repo --out claims.json
python3 -m ops.web_adapter_foundry.apk_xref xref --extraction extraction.json --claims claims.json --target-id example --xref-issue '#2064' --submitter 'role{moniker}' --out report.json --markdown findings.md
```

Acquire (GitHub/Gitea Releases, F-Droid — never Play) → extract
(manifest/permissions/endpoints/providers/trackers, stdlib parsers)
→ cross-validate both directions → findings in the `apk-xref/v1`
template shape. Doc: `docs/ops/APK-XREF-TOOLKIT.md` ·
Tests: `tests/test_apk_xref.py`
