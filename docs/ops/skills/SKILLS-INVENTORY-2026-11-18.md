# Skills and plugins inventory (2026-11-18)

Scope: the full skill and plugin set in the container mount, measured 2026-11-18.

## Totals

- SKILL.md files: 1,299 · bytes 13,559,638 (13.56 MB)
- Plugin directories: 1,216
- Namespaces: plugins 1,256 · examples 35 · public 8

## Export artifacts (produced in the container, delivered as files)

| File | Rows | Contents | Notes |
|---|---|---|---|
| skills-SKILL-md-all.tar.gz | 1,299 files | Every SKILL.md, paths preserved | 4.88 MB · sha256 prefix b2bfb4b5839bee93 |
| skills-inventory.csv | 1,299 | namespace, plugin_dir, skill_path, name, description (240 chars), bytes, sha1 (12) | per skill |
| skills-inventory.jsonl | 1,299 | Same fields as the CSV | JSON lines |
| plugins-inventory.csv | 1,216 | plugin_dir, namespace, skills, bytes, first_skill | per plugin |

## Placement decision

- Default: `vendor/skills-mirror/` for the mirror. Third-party quoted material sits under the Siglary §6.5 E2 exemption.
- Rejected: `skills/`. Siglary §1 binds `skills/**` at HARD severity, which would fail the mirror on day one.

## Clone steps (run on a machine with git and push access)

```
git switch docs/connector-audit-2026-11-17
mkdir -p vendor/skills-mirror docs/ops/skills
tar xzf skills-SKILL-md-all.tar.gz -C vendor/skills-mirror
cp skills-inventory.csv plugins-inventory.csv docs/ops/skills/
git add vendor/skills-mirror docs/ops/skills
git commit -m "vendor: mirror 1299 SKILL.md + inventories (2026-11-18)"
git push origin docs/connector-audit-2026-11-17
```

## Connector limit

Connector tools carry content in tool arguments. The archive (4.88 MB) exceeds that path. The connector path committed this summary only.
