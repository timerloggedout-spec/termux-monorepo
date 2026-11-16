# GitHub App routes — programmatic map (companion: ops/github-apps/ROUTES.json)

Web *computer use* is an early-allowance workaround for single tests only.
The durable route is the **App Manifest flow**; everything after the
bootstrap is REST. Tool: `scripts/github_app_manifest.py` (stdin-driven).

## Bootstrap (creation)
| Step | Route | Auth | Programmatic? |
|---|---|---|---|
| Submit manifest | `POST https://github.com/settings/apps/new` — urlencoded form, one field `manifest` = manifest JSON | account web session | Form POST; no REST create endpoint exists. `github_app_manifest.py serve` hosts the form + catches the result locally |
| Convert code | `POST /app-manifests/{code}/conversions` | none — code is single-use, short-lived | ✅ Full API. Returns id, slug, client_id, client_secret, webhook_secret, **pem** (bootstrap key) |
| Install | `GET https://github.com/apps/{slug}/installations/new` | installing account's web consent | Web-only by GitHub design (consent). One click-through per account |

## Steady state (all API)
| Purpose | Route | Auth |
|---|---|---|
| App identity | `GET /app` | App JWT (RS256; iss = App ID; iat −60s; exp ≤ +10 min) |
| Installations | `GET /app/installations`, `GET /app/installations/{id}` | App JWT |
| Mint token | `POST /app/installations/{id}/access_tokens` | App JWT → token, ~1h, `expires_at` returned |
| Bucket check | `GET /rate_limit` | the token itself — per-installation bucket, independent of the PAT bucket (5000/h user) and the Actions `GITHUB_TOKEN` bucket (1000/h/repo) |
| Work | any repo-scoped route within granted permissions | installation token |

Tools: `scripts/github_app_token.py` (minter), `scripts/github_app_bucket_proof.py` (split proof).

## Web-only residuals (named, bounded)
1. Creation form POST — needs a signed-in session once per app. Served
   locally by the tool; the human surface is a single Create click.
2. Install consent — once per (app, account).
3. Key rotation after bootstrap — app settings UI. Bootstrap key arrives
   via the conversions response, so rotation is never needed to start.
4. Profile-picture upload — web-only (no API); cosmetic, once per app.

Everything else — identity, discovery, token minting, work, quota — is API.
