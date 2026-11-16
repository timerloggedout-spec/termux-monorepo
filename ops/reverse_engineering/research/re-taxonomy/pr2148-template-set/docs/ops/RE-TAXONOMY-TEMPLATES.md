# Reverse Engineering — Taxonomy / Toolkit issue templates

The template set for the reverse-engineering taxonomy/toolkit category
(re-taxonomy/v1, `ops/reverse_engineering/taxonomy.json`). Sibling to the
APK cross-reference set (docs/ops/APK-XREF-TEMPLATES.md); same pattern:
family name prefix, chooser-safe field subset, one label, no target-brief
double-fire.

## Forms

| Form | File | Purpose |
| --- | --- | --- |
| Reverse Engineering — Taxonomy / Toolkit | `.github/ISSUE_TEMPLATE/reverse-engineering-taxonomy.yml` | Register or propose a category, tool, or toolchain node |
| Reverse Engineering — Taxonomy / Toolkit Record | `.github/ISSUE_TEMPLATE/reverse-engineering-taxonomy-record.yml` | File the validated placement + evidence record (Item ID + validator result) |

Label: `re-taxonomy` on both forms (the forms carry no other trigger label).

## Trigger

`.github/workflows/re-taxonomy-intake.yml` — `issues` opened/reopened/edited
carrying `re-taxonomy`, exactly one event per filing (no `labeled`, no
concurrency group; research-intake fix, PRs #2132/#2137). The workflow runs
`scripts/reverse_engineering/re_taxonomy_intake.py` from the trusted
default-branch checkout **with `--taxonomy ops/reverse_engineering/taxonomy.json`**,
so vocabulary, parent resolution, and toolchain tool refs validate against
the live registry, then comments the record back, sha256-hash deduped.
Re-trigger: edit, close/reopen, or a `<!-- request-research -->` comment is
NOT wired here — edit/reopen are the paths. No `pull_request_target`, no
provisioned secrets.

## Record: `re-taxonomy-intake/v1`

The `node` object carries exactly the fields
`ops/reverse_engineering/taxonomy.py validate()` consumes — `id`, `name`,
`kind` (category|tool), `parents` (polyhierarchy, >= 1, must resolve and
descend from `reverse-engineering`), `tags` (axis vocabulary only),
`description` — plus `toolchain` entries `{stage, tools, output}` in
`workflow_stages` order with tool refs that resolve to tool nodes, and
`outputs`. A record can therefore be validated mechanically before its node
lands in taxonomy.json.

Validation enforced at intake: slug ids; axis vocabulary verbatim from
taxonomy.json (target / format / architecture / method / objective /
tool_role / environment / evidence); tool nodes REQUIRE `tool_role` tags;
toolchain stage order; submitter in `Role{Moniker}` form; secret-looking
VALUES refused (names only).

`kind` is `filing` for the registration form and `record` when the Item ID /
Validator result headings are present.

## Placement rules (carried in the form help text)

Placed once by primary kind; overlap = extra parents + tags, never duplicate
nodes; kinds distinct (platform != discipline != credential != format).

## Seam

Field/vocabulary changes ping the reverse-engineering-toolkits lane
(d573ca2b) before merge, both ways — the same rule as the apk-xref seam.
The toolkit lane verifies the form vocabulary against taxonomy.json at
action time.
