# Hindsight SUCCESSes

Generated: 2026-10-02
Branch: feat/gh-actions/deepseek-integrates-itself

## Verified end-to-end

### F1 - Gemini to Hindsight retain to memory_units
- POST /v1/default/banks/<bank>/memories with N items
- Hindsight calls Gemini, extracts facts, writes to memory_units
- Verified: llm_requests shows provider=gemini, status=success,
  input_tokens and output_tokens populated, output body = {"facts": [...]}

### F2 - Multi-provider MVT lanes
- :8888 -> gemini-3.1-flash-lite (prefix termux-monorepo::mvt::gemini::)
- :8889 -> openrouter (prefix termux-monorepo::mvt::openrouter::)
- Same source, different extraction, compared at recall time

### F3 - Model rotation
- hs-stack.py probe caches limits.json
- pick_next() picks highest headroom
- restart_hindsight() reads live /proc/<api-pid>/environ
- Active model tracked in /tmp/hs-stack/active.json

### F4 - Sovereign seed loop
- sovereign-run.sh reads active.json, cycles source, runs mvt-seed.py
- mvt-seed batches items, bumps state.json on 200
- Aborts lane after 5 consecutive quota errors
- mvt-watchdog respawns rotator + sovereign every 5 min

### F5 - Schema-aware dashboards
- memory_units.context (NOT content)
- llm_requests.started_at (NOT created_at)
- Bank aggregates: COUNT(*) GROUP BY bank_id

### F6 - Live quota probes
- Gemini: 1-token generateContent -> 429 body has QuotaFailure
- OpenRouter: /api/v1/auth/key and /api/v1/credits

### F7 - Provenance journal
- hs_facts_journal table: ts, actor, op, bank_id, unit_id, before, after, reason
- hs-facts set-meta / del / hist all write to it
- Dashboard PROVENANCE reads last 10 entries

## Commands that work

    hs-facts count
    hs-facts count '%::mvt::%'
    hs-facts recent '%::mvt::%' 10
    hs-facts get    BANK UUID
    hs-facts set-meta BANK UUID '{"tag":"reviewed"}' "reason"
    hs-facts del      BANK UUID "reason"
    hs-facts hist     BANK UUID
    hs-db
    hs-dash
    hs-verify

## Doctrine

1. Termux has no /tmp - always TMPDIR.
2. Never paste Python/SQL/JSON at zsh prompt. Files + heredoc.
3. gh codespace ssh flags go before --. Nothing after -- reaches local shell.
4. Quote nesting greater than 2 levels breaks. Ship script, run script.
5. Content cols: memory_units.context, documents.text, llm_requests.output.
6. Token cols: only populated on status=success.
7. Bank rename requires dropping ALL FKs on documents + banks first.
8. Provider model names with / in URLs: strip / before bank segment.
9. Rotator restart must read env from /proc/<api-pid>/environ.
10. OpenRouter free models die without warning - always probe /api/v1/models
    and pick by context length, never hardcode.
