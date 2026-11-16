# ICM Map Maintenance Rules

## Scope boundary

The `docs/icm/` workspace is an **interpretation and routing layer**. It may add or update Markdown documentation, templates, `.gitkeep` files, and documentation-only ignore rules. It must **not** refactor, relocate, reformat, or otherwise modify application code, including Python files, as part of ICM maintenance.

## Canonical sources

Each fact has one home. A map card summarizes only what is needed to route an editor, then cites the owning source path and line range. If a card and the source disagree, the source wins; update the card or mark it `stale`.

## One-way references

Map documents may point to canonical sources. Canonical application or architecture sources do not need reciprocal links to every map consumer. Do not add circular navigation merely to make the graph feel symmetrical.

## Context loading

Load the maintenance catalog, the current stage contract, the stable factory file(s), and the smallest named source set. Do not load the full repository, generated mapper payloads, browser/session artifacts, or device state to update one card.

## Product policy

Per-update inventory, proposals, verification records, and promotion records belong in stage `output/` folders. They are working artifacts and remain untracked except for `.gitkeep`; durable decisions belong in the approved map documentation or proposal records.

## Human gates

A human reads and approves the proposed map change before verification and promotion. A map update never grants authority to merge, force-push, change branch protections, rotate credentials, or operate the device.

## External boundaries

ICM is the context and documentation structure. Existing CI, GitHub review, MCP adapters, and runtime code remain their own systems. Do not represent real-time collaboration, high-concurrency behavior, or automated branching as pure folder sequencing when a separate control system owns them.
