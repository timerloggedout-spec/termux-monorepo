---
type: object
cluster: knowledge
universe: live
status: initiated
entity: docs/ops/
verified_at: 2026-11-01
---

# Ops Records Estate

`docs/ops/` is the repository's operational records estate: the fleet's own ledgers, registers, matrices, program rules, and dated evidence records. At the Docs lane census it held **404 documents** (359 direct, plus sessions 14, generated 11, agent-coordination 6, corpus 3, session-notes 3, skills 2, tasks 2, and single-document subdirs). This card classifies the estate so a reader can route a record without treating every file as the same kind of thing. It does not enumerate the estate; per-file inbound/orphan data lives in the Docs lane's orphan-pass record.

## Classification boundary

| Class | How to recognize it | Treatment |
|---|---|---|
| generated | `docs/ops/generated/` and the table region of `DOCS-BRANCH-INDEX` | Machine-generated. Never hand-edit; regenerate through the owning process. |
| hand record — operational | Undated records (registers, matrices, program rules, monikers) | Living documents. Edit through their owning lane/process. |
| hand record — snapshot | Filename-dated records (`*-2026-10-27`, `*-2026-10`, dated matrices/censuses) | Point-in-time evidence. Archive candidates once a living successor exists; keep verbatim as history. |
| pointer stub | `docs/ops/foresight/` copies and similar stubs | Not records. Canonical contracts for FORESIGHT/FOSS live in `docs/research/` (PR #3259); follow the stub, do not classify or edit it as a record. |

The Docs T1 pointer taxonomy — {Certifications · Provider/dispatch · Fleet/AppID} — is a **reachability grouping** over this estate, not a content classification. The classes above are the content layer; the groups say which records a topic reaches first.

## Read when

- Looking for the fleet's record on an operational topic (start here, then follow the class to the owning record).
- Adding a new ops record: pick its class first (dated snapshot vs living record vs generated output) — the class decides naming, location, and edit path.
- Deciding whether an ops file may be hand-edited: generated class and pointer stubs may not.

## Connected to

- **classified-with:** the Workspace Artifact Estate card (same classify-before-reading discipline for `workspace/`).
- **owned-by:** the owning lanes named inside each record; the Docs lane maintains estate-level census and orphan data.
- **looks-like-but-is-not:** a single index — `DOCS-BRANCH-INDEX` is a generated reachability surface inside the estate, not the estate's classification.

## See

- Estate: [`docs/ops/`](../../../../docs/ops/)
- Sibling classification: [`workspace-artifact-estate.md`](workspace-artifact-estate.md)
