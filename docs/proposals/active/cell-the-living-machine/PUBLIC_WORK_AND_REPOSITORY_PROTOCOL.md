# Public Work, Private Repositories and Project Boundaries

## Default posture
Build and publish publicly by default. Use private repositories for designated confidential control planes, proprietary work, protected research, credentials, grant-restricted material and pre-release concepts with a documented confidentiality basis.

## Repository roles
- Public product repositories: game source, public issues, public roadmaps, contribution guides, release notes, public assets and approved documentation.
- Private organization reserve: one designated private repository per organization for confidential operations, credentials-by-reference, private project planning and protected records.
- Public research repositories: reusable scientific metadata, source references and curated records where rights and provider terms allow.
- Private research records: restricted datasets, unpublished findings, sensitive collaborations and protected data.
- Public mirrors and satellites: focused projects that consume shared schemas, packages, APIs and stable project references from the MonoRepo control plane.

The organization-level private repository allocation is a governance policy to verify against current plan entitlements. Repository creation uses the existing Repository Provisioner workflow and its authenticated Actions secret. The workflow verifies the authenticated owner and records the credential reference without exposing the token value.

## Confidentiality classification
| Class | Typical content | Default handling |
|---|---|---|
| Public | Source code, public roadmap, approved designs, public datasets with compatible terms | Public repository |
| Internal | Operational runbooks, internal coordination, non-sensitive planning | Organization control plane |
| Confidential | Partner contracts, grant terms, unpublished research, private project concepts | Designated private repository or restricted service |
| Restricted | Secrets, credentials, personal data, regulated data, safety-sensitive records | Secret manager or approved restricted system; repository stores references only |

## Cross-repository protocol
Each project has a stable project ID, repository manifest, owner, visibility, license, source-of-truth declarations, dependency versions and release links. Public satellites consume versioned schemas and APIs. Local symlinks are optional workspace conveniences; they never replace canonical repository references.

A public repository may reference private systems through opaque IDs and documented interfaces. It publishes only the public projection of project state. Access checks remain at the system that owns the protected resource.

## Publishing gate
Before publication, verify license and attribution, third-party asset rights, secrets scan, personal-data scan, partner/grant restrictions, source provenance, generated artifact metadata, issue templates and contribution policy. A public release is a deliberate project state transition with an immutable release record.

## Visibility transitions
Visibility changes use an owner-authorized GitHub Actions workflow, an explicit allowlist, a trusted-actor check and an audit receipt. The workflow records the requested repository and resulting visibility. Token values remain in Actions secrets and workflow logs contain only secret names/references.

## Current project allocation
- Product repository: timerloggedout-spec/cell-the-living-machine — planned public product repository; current visibility transition requires the owner-authorized workflow.
- Developer control plane: timerloggedout-spec/termux-monorepo — canonical development and tooling control plane.
- Reusable research: Research-Astute/molecular-biology-research — private while record reuse, provider terms and data rights are reviewed.
- Search aggregation: search-astute-ly — existing organization and repositories retain their current visibility while account lifecycle is resolved.
