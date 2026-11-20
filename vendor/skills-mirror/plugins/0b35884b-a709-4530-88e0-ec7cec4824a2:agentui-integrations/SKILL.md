---
name: agentui-integrations
description: Connect an AgentUI app to third-party APIs — browse and use the workspace's installed integrations, or author a brand-new one in a single JSON spec (`agentui integration new/check/test/publish`). Use when the user wants their app to talk to Stripe, Slack, Google, HubSpot, a bank, an ERP or any HTTP/GraphQL API; when an integration is disconnected or erroring; or when the API they need is not on the platform yet and the alternative is writing raw request code by hand.
---

# Integrations

## Use what is already there — first

```bash
agentui integrations list                        # workspace integrations
agentui integrations list --authenticated        # only the connected ones
agentui integrations list --platform stripe
agentui integrations info <id>
agentui integrations docs <platform>             # docs pulled from skills + prompts
agentui integrations alerts                      # auth expired, rate limits, recent failures
```

Config, tokens and auth state are **never returned** — only the type and whether it is
connected. If something the app needs is not authenticated, say so and hand the user
`agentui open integration <provider>` — a link to the connect screen for that
provider. You cannot connect it from here.

Before writing HTTP calls by hand, check `agentui guide external-api` and
`agentui integrations docs <platform>`. The platform handles credentials, encryption,
token refresh, retries and the proxy — hand-rolled request code in app source gets none
of that, and puts the user's key in a place it does not belong.

## Build a new integration

One JSON file. No request code. Published once, installable by every builder in one
click.

```bash
agentui integration guide                 # the whole playbook, offline
agentui integration new "Polygon.io"      # scaffolds <slug>.integration.json
agentui integration check                 # offline, ~40ms — run it constantly
agentui integration check --fix           # apply every machine-applicable fix
agentui integration test                  # real calls through the real proxy
agentui integration publish               # uses the spec's own visibility
```

Each step refuses to run until the previous one is green. The publish gate is precise:
**at least one endpoint must have an executed test and no test may have failed** — it is
not per-endpoint coverage, so an untested endpoint can still ship. `--skip-tests`
publishes with no passing run at all; it exists for an API that genuinely cannot be
reached from the platform, and if you use it, say so in the description.

Before authoring anything, check whether it already exists:

```bash
agentui integration list --search stripe
agentui integration pull <id> --fork      # start from someone else's instead of scratch
```

The spec:

```jsonc
{
  "name": "Polygon.io",
  "description": "Stock, option and crypto market data.",
  "apiType": "rest",                      // or "graphql"
  "baseUrl": "https://api.polygon.io",    // no trailing slash
  "visibility": "public",
  "auth": {
    "type": "api_key",                    // none | api_key | bearer | basic | oauth2
                                          // custom | hmac | oauth1 | digest | session
    "credentialFields": [
      { "name": "apiKey",                 // read BY NAME at call time
        "label": "API Key",
        "help": "Dashboard → Keys",       // where the installer finds it
        "location": "query",              // header | query | url
        "headerName": "apiKey" }          // what it is called on the wire
    ]
  },
  "endpoints": [
    { "id": "listTickers",
      "method": "GET",
      "path": "/v3/reference/tickers",
      "description": "Lists tradable tickers. Call it before any per-ticker lookup.",
      "parameters": [{ "name": "limit", "in": "query", "type": "number",
                       "description": "How many to return (1-1000)." }],
      "test": { "query": { "limit": 1 }, "expectStatus": 200 } }
  ],
  "errorMap": [
    { "status": 401, "message": "The API rejected the key.",
      "fix": "Regenerate it under Dashboard → Keys, then reconnect." }
  ]
}
```

## Non-negotiables

- **Credentials never go in the spec.** The spec is published; the key is not. Put it in
  `.agentui-credentials.json` (created gitignored by `integration new`) or pass
  `--credential apiKey=…`. `check` refuses a spec carrying anything that looks like a
  live key.
- **`publish` is public by default if the spec says so.** Confirm the visibility with
  the user before publishing; `--public` / `--private` override and are written back to
  the spec so a later plain `publish` cannot silently flip it.
- Pulling someone else's integration always forks — you can only publish your own copy.
- `check`, `test` and `publish` print a 0–100 readiness score across spec validity,
  endpoints proven against the real API, test coverage, how well another builder's AI
  could choose between your endpoints, and whether a failure is recoverable from your
  `errorMap`. Write endpoint descriptions for the AI that will have to choose — that is
  a scored dimension, not decoration.
