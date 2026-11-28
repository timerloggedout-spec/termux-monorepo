# Central Player Identity and Cross-Game Profile

## Purpose
One player identity spans every game type, mode, project and owned experience in the ecosystem. Each game remains an independent product with its own save data, progression, controls and content, while the account-level profile supplies a consistent identity and portable history.

## Identity model
- player_id: stable opaque identifier shared across games and projects.
- account_id: authentication-provider identity reference, held by the identity service.
- profile_revision: version of the user's profile.
- public_handle: user-selected public display identity.
- private_identity: account and recovery data held by the identity service.
- game_profiles: game-specific state keyed by game_id.
- capability_profile: knowledge lenses, accessibility settings and interaction preferences.
- portfolio_refs: user-owned or user-authorized design, research, build and project references.
- consent_receipts: scopes for public sharing, telemetry, collaboration, portfolio publication and external services.

## Shared profile capabilities
1. One account and player identity across the game catalog.
2. Consistent avatar, display name, accessibility preferences and control mappings.
3. Portable knowledge-lens preferences and saved discoveries.
4. Per-game save slots, achievements, progression and scenario records.
5. Shared creator portfolio with explicit project-level visibility.
6. Team memberships and contribution history.
7. Skills and evidence records with issuer, assessment, date and verification status.
8. Equipment access and qualification references, with facility permissions held by the equipment system.
9. Export, import, recovery and account-deletion workflows.
10. Cross-game discovery and recommendations based on user-controlled preferences.

## Data ownership and boundaries
The player owns their profile content and controls public visibility. Public identity fields are separated from private account data, credentials, billing, personal contact details and protected project data. Game repositories store stable IDs and scoped references; the identity service owns account credentials and profile synchronization.

The central profile does not grant access to a private project, physical equipment, grant workspace, paid service or professional workflow. Each system checks its own authorization and consent scope.

## Portability and interoperability
Use a versioned JSON profile contract with schema migration, export/import, explicit field ownership and per-game extension namespaces. Public game clients authenticate through a common identity API; private projects use the same player ID with independent access checks. Offline play supports a local profile cache and later conflict-aware synchronization.

## Profile management
The profile dashboard exposes identity and recovery; games and save slots; skills, badges and evidence; portfolio and published designs; projects, teams and contributions; learning pathways and certifications; accessibility and controls; privacy, consent, export and deletion.

## Acceptance
A single test account signs into two different game types, preserves the same player_id, loads distinct per-game save data, shares a portfolio artifact with an explicit scope, and retains private account fields outside the public profile payload.
