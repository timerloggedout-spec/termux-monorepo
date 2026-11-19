---
name: security-discipline
description: Use on every diff, every new endpoint, every change to a backend component. Treats security as a per-change reflex, not an audit phase. Catches IDOR/BOLA, mass assignment, injection, secret leaks, missing auth, and the everyday holes that ship while nobody is looking at "security". Apply this BEFORE marking a change as done.
---

# Security Discipline

Security is not a milestone. It is the question you ask of every diff you write: what does this expose, what does it trust, what could it leak. The reviews catch what they catch; the reflex catches the rest.

## The Per-Change Audit

Before considering a change done, answer four questions about the diff in front of you:

1. **What does this expose?** New endpoint, new field in a response, new admin path, new file accessible. Anything reachable from outside that was not reachable before.
2. **What does it trust?** Input from clients, claims in tokens, headers, payloads from third parties, ENV at startup. Each one is a defect waiting unless you say otherwise.
3. **What can leak through it?** Logs, error messages, response bodies, exception stack traces, file paths in 404s.
4. **Is the default closed?** New resource needs an explicit allow. New endpoint needs an explicit auth. New field needs an explicit "exposable" decision.

If you cannot answer all four, the change is not done.

## Deny By Default

Every gate is closed until something opens it.

- **New endpoint**: requires auth unless explicitly public.
- **New role / permission**: starts with empty scope, grows by explicit grant.
- **New field on an updateable model**: not in the allowlist for mass assignment unless you put it there.
- **New CORS origin / CSP source**: rejected unless on the allowlist.
- **New third party**: HTTPS, signature verified, timeout set, error handling decided before the first call.

The opposite ("allow by default, deny specifics") is how every multi-year breach starts.

## Common Failures By Context

Different components have different sharp edges.

**HTTP endpoints:**

- **BOLA / IDOR**: `/orders/:id` without checking the order belongs to the caller. The deepest most common vuln. Every per-id route must enforce ownership at the data layer.
- **Mass assignment**: `Model.update(req.body)` updates fields the user is not supposed to control (role, tenant_id, is_admin). Explicit allowlist of updateable fields.
- **SSRF**: backend fetches a URL the user controls. Treat user-supplied URLs as hostile; allowlist hosts or hop through a proxy that does.
- **Open redirects**: forwarding to a URL parameter. Allowlist or block external.
- **Parameter pollution**: arrays where a string is expected, duplicate query params. Validate at the boundary, normalize before use.

**Workers / consumers:**

- **Poison message executing arbitrary code**: a payload field that ends up in `exec`, `eval`, `os.system`, or a shell command.
- **Trusting source identity**: webhook receivers without signature verification.
- **Privilege escalation via job parameters**: a job that calls "send email as user X" where X comes from the payload without checks.

**Integrations:**

- **Outbound calls with secrets in URLs**: tokens in query strings end up in logs, proxies, and bug trackers.
- **Skipped TLS verification**: `verify=False`, `rejectUnauthorized: false`. A red flag every time.
- **No timeout**: an outbound call without a timeout is also a DoS vector when the remote degrades.

**CLIs / admin scripts:**

- **Privilege escalation by accident**: a script run as root touching user-supplied paths.
- **No audit trail**: who ran it, when, with what args.
- **Production secrets in the dev branch of the same script.** Separate config, never inline.

## Injection, Across Layers

Concatenated input is the family of vulnerabilities that never goes away. The discipline is uniform: parameterize.

- **SQL**: parameterized queries / placeholders. ORMs almost always do this; the danger is the raw escape hatch. `db.execute("SELECT ... WHERE id = " + user_id)` is a defect. Even inside an ORM, `f"WHERE name = '{name}'"` in a raw query is a defect.
- **Shell**: `subprocess.run([list, of, args])` with a list, not a string. Never `shell=True` with user input.
- **HTML in response bodies**: rely on the template engine's auto-escaping. Marking content "safe" is the dangerous knob.
- **Headers**: a CRLF in a user-controlled header value splits responses. Reject newlines at the boundary.
- **NoSQL**: Mongo accepts operator objects (`{"$ne": null}`). Validate types before passing user input to a query.

## Secrets and PII

The two things that should never appear in places they often do.

**Secrets:**

- Never in code. Never in commits. Never in PR descriptions.
- Loaded from environment, a secret manager, or a mount. Not from a config file in the repo.
- Never logged. A request body logger that captures `Authorization` headers is a breach in waiting.
- Rotated when an engineer with access leaves, or when a process exposes them.

**PII and sensitive data:**

- Not in logs by default. Use field redaction at the logger, not "I will remember to redact".
- Not in error messages returned to the client. Generic message externally, full context internally.
- Encrypted at rest where the regulation demands. Encrypted in transit always.
- Deleted on request. A GDPR delete that does not actually delete is a worse breach than not implementing it.

## Error Surfaces That Leak

Error responses are an information channel. Treat them as one.

- **Generic external, specific internal.** Return "Not found" to the client; log the full reason internally.
- **No stack traces in production responses.** A stack trace tells an attacker the framework, the version, the file paths, and sometimes the SQL.
- **No "user not found" vs "wrong password".** Both return the same response. Avoids enumeration.
- **No "this resource belongs to another tenant".** Return 404, not 403. Avoids enumeration of foreign IDs.

See [[error-handling-as-design]] for the broader error shape.

## Boring Security Headers

Every web app should have these by default. The framework usually has a one-liner.

- **`Strict-Transport-Security`** with a sensible max-age and `includeSubDomains`.
- **`Content-Security-Policy`** that at minimum forbids inline scripts, with a documented evolution.
- **`X-Content-Type-Options: nosniff`**.
- **`Referrer-Policy: strict-origin-when-cross-origin`** or stricter.
- **Cookies**: `Secure`, `HttpOnly`, `SameSite=Lax` (or `Strict` for sensitive flows).
- **CORS**: allowlist of origins, not `*` for credentialed requests.

If you ship without these, the boring scan tool the security team runs next quarter will find it.

## Light vs Deep Threat Modeling

Two modes, both worth running.

- **Light, per change.** The four questions above. Takes a minute. Covers most accidental holes.
- **Deep, at architecture time.** What is the trust boundary, what crosses it, who can authenticate as what, what is the blast radius of each compromise. Once per service or per major change. Document it.

Skipping light is how most flaws ship. Skipping deep is how a single flaw becomes systemic.

## Anti-Patterns

- **Security as a separate sprint.** A change that introduces a vuln on Monday and "we will security-review next month" is a vuln in production for a month.
- **Blacklist input.** "Block `<script>`". Five hours later, "Block `<scr` `ipt>`". Allowlist what is valid, reject everything else.
- **Echoing user input in errors.** "User `<script>...` not found" reflects content right back. Sanitize at the boundary.
- **JWT claims trusted as truth.** If the role is in the JWT, you still re-check at the data layer, because tokens leak, get reused, and tokens can be issued from an old role.
- **Auth at the top, no check at the bottom.** Route guard passes, then the handler fetches by an ID from the body without re-authorizing.
- **`if (user.role == 'admin')` scattered everywhere.** Centralize the check, audit one path.
- **TLS off in dev "to make it work".** Habits set in dev ship to prod.
- **Custom crypto.** Use the library. If you find yourself writing AES, stop.

## Quick Decision Guide

| Situation | Reflex |
|-----------|--------|
| New endpoint | Auth required by default, explicit public allowlist |
| Per-id resource access | Ownership check at the data layer, not just the route |
| Update endpoint | Explicit allowlist of updateable fields |
| User-supplied URL | Allowlist hosts, or proxy with controls |
| Outbound call with credentials | Header, not URL; verify TLS; set timeout |
| Webhook receiver | Verify signature, treat payload as hostile |
| Logging a request | Redact `password`, tokens, full PII; allowlist what is logged |
| Error response to client | Generic; details only in internal logs |
| Storing a secret | Secret manager / env, never in repo |
| Crypto | Use a library; never roll your own |

## See also

- [[auth-and-authorization]] for the deep treatment of authn/authz
- [[error-handling-as-design]] for what leaks via errors
- [[observability-by-default]] for what NOT to log
- [[think-before-coding]] Steps 3 and 4 invoke the security and auth questions
