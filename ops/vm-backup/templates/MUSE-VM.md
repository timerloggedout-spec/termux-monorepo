# Muse VM — named collaborator context

**Profile ID:** muse-vm  
**Profile revision:** 1  
**Owner:** repository Operator  
**Scope:** Muse VM workspace, side-chat export intake, and provenance publishing

## Identity

Muse VM is the named execution environment for side-chat clones and workspace exports. Its platform identity, account identity, GitHub actor, provider/model identity, and execution adapter remain separate attribution fields.

## Role

- Maintain the VM workspace and its backup/export lifecycle.
- Publish side-chat message exports under a date-scoped `muse-side-chat/<date>/` namespace.
- Preserve source provenance and stable native message/session identifiers.
- Run the versioned Muse side-chat SEO classifier at ingest.
- Publish aggregate discovery-term counts while keeping message excerpts in the private store.

## Persona and execution assets

The VM's separately versioned `IDENTITY.md`, `SOUL.md`, `USER.md`, `PROACTIVE_PREFERENCES.md`, and `TOOLS.md` remain independent source files. Their content hashes and source paths are recorded by the VM backup manifest. This profile defines the named VM context and export contract.

## Provenance contract

Every export records its source namespace, origin, native ID, export class, timestamp, text hash, classifier IDs/versions, and Actions evidence join. Credential-shaped content is reduced to a hash before publication. Public digests contain aggregate counts and labels only.

## Revision policy

Increment this profile revision when the VM's role, source namespace contract, export behavior, or authority boundary changes. Preserve prior revisions and bind each export run to the profile revision and SHA-256 fingerprint.
