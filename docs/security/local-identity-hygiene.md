# Local identity hygiene (public)

**Policy:** personal legal names, private emails, and machine-local paths must never
live in tracked scripts that run on other developers' machines or in CI.

## Why this note exists

A pre-commit / scanner path was intended to stay **local** (`.gitignore`) but at
least one revision leaked operator identity into a tracked helper. That is a
hygiene bug, not a feature.

## Rules

1. Scanners that encode *your* identity belong under ignored paths, e.g.:
   - `.local/hooks/`
   - `scripts/private/`
   - anything matching `*_local*` already covered by `.gitignore` patterns
2. Tracked hooks must use **generic** placeholders (`OPERATOR`, `local-user`, `$USER`).
3. If history still contains the leak, treat cleanup as a **reviewed** history
   rewrite or `git filter-repo` pass — never silent force-push to `master` alone.
4. Rotate any tokens that shared a commit with the leak.

## Easter eggs (public, no PII)

Workflow skip/fallback comments may include harmless HTML markers such as:

```text
<!-- egg: low valleys often outrun peaks on free paths -->
```

These are breadcrumbs for multi-agent side-channels (Grimoire / CAVEMAN compression
path) — not credentials, not names.

## Checklist before commit

- [ ] `git grep -iE 'real.?name|full.?name'` on staged paths (operator-defined terms)
- [ ] No `*_api_key`, `*.pem`, session JSON under tracked trees
- [ ] Pre-commit scanner itself is either generic or gitignored

Related: AGENTS.md · SECURITY.md · #94 egg-brush · repository hygiene PRs.

Signed-off-by: Grok <grok@x.ai>
