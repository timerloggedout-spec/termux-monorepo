# External Reverse-Engineering Targets

Metadata-only register for externally published applications and services admitted through the repository's Reverse Engineering issue intake. This register records discovery provenance and scope; it does not assert that an artifact has been acquired or analyzed.

## Bixberry — Android

| Field | Value |
|---|---|
| Target ID | `bixberry-android` |
| Package ID | `ai.bixberry.app` |
| Google Play | https://play.google.com/store/apps/details?id=ai.bixberry.app |
| Publisher | CLOUDSQUAD, UAB (Google Play listing) |
| Intake issue | [#5810](https://github.com/timerloggedout-spec/termux-monorepo/issues/5810) |
| Intake state | OPEN · target intake #5810; APK-XREF request #5825 |
| APK-XREF queue | [#5825](https://github.com/timerloggedout-spec/termux-monorepo/issues/5825) · `apk-xref` · ordered acquisition alternatives filed |
| Scope | Public listing, public website, public support and privacy documentation |
| Mode | Read-only · observed evidence |
| Artifact state | NOT ACQUIRED · alternative-store acquisition queued |
| Acquisition order | `aurora-store` → `komistore` → `lizzyondroid` → `izzyondroid` → `f-droid` → `other-store` |
| Source repository | UNKNOWN / not established |

### Research boundary

The filing authorizes public-surface observation only. Preserve publisher statements as claims until independently observed. Record consent and controls, network/compute sharing behavior as publicly described, reward mechanics, data-safety disclosures, platform requirements, and public support/privacy documentation.

The APK cross-reference request is [#5825](https://github.com/timerloggedout-spec/termux-monorepo/issues/5825), paired with target intake [#5810](https://github.com/timerloggedout-spec/termux-monorepo/issues/5810). It carries the ordered alternative-store chain: Aurora Store fallback, KomiStore upstream releases, LizzyOnDroid/IzzyOnDroid, F-Droid, then the other-store fallback. The runner records the actual acquired channel and SHA-256 provenance. Aurora currently falls back to wired IzzyOnDroid/F-Droid repositories; KomiStore resolves to its upstream GitHub or Codeberg/Forgejo release assets; LizzyOnDroid is a form spelling alias for IzzyOnDroid. Direct Google Play scraping remains refused. Execution dispatch is held until a verified source repository URL is identified, preventing an empty-repository scan from producing misleading divergences.

### Source references

- Google Play listing: https://play.google.com/store/apps/details?id=ai.bixberry.app
- Official site: https://www.bixberry.com/
- Android setup guide: https://support.bixberry.com/hc/en-us/articles/30699820896668-Set-up-Bixberry-on-Android
- Platform support: https://support.bixberry.com/hc/en-us/articles/30699821367836-Which-platforms-does-Bixberry-support

### Evidence status

This is an intake record, not a reverse-engineering result. No APK extraction, endpoint observation, permission inventory, or independent behavior verification is claimed here.
