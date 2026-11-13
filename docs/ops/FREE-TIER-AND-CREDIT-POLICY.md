# Free-Tier + Credit Policy

Status: mandatory procurement gate
Owner: termux-monorepo platform stewardship

## Cost mandate
- Default every platform, CI job, feed, database, preview and deployment to a documented free tier.
- Apply verified referral, affiliate, sponsorship or promotional credits before cash spend.
- Record credit issuer, eligibility, amount, expiry, eligible services, billing account and remaining balance.
- Require explicit approval for paid plans, metered overages, paid add-ons, persistent disks and recurring charges.
- Keep production workloads within published free quotas and configure budget alerts where supported.
- Prefer static hosting, GitHub Actions free allowances, public APIs, local computation and cacheable read-only feeds.
- Publish an estimated monthly cost and free-quota envelope for each service.

## Platform matrix
| Platform | Default role | Free-first implementation | Gate |
|---|---|---|---|
| GitHub | Canonical source, issues, PRs, Actions, Pages | Existing repository and free public-repo features | Check current Actions quotas and org policy |
| Vercel | Observatory UI and previews | Hobby/free eligibility; static output | Confirm account eligibility, deployment limits and production domain |
| Render | Optional feed adapter | Free web service where currently eligible | Confirm spin-down, runtime, bandwidth and service quotas; use static GitHub feeds as fallback |
| GitHub Pages | Static mirror / fallback | Repository-hosted static pages | Enable after branch and custom-domain review |
| Local Termux | Portable execution | Python stdlib, shell, SQLite | Origin availability and device resources |

## Credit ledger
Store verified credit evidence in a private billing record. Publish only service, eligibility class, amount band, expiry and verification timestamp. Keep account identifiers, redemption tokens and billing secrets private.

## Architecture
GitHub remains canonical. Vercel and GitHub Pages serve static artifacts. GitHub public API feeds supply live read-only activity. Render adds optional caching only when its free-tier envelope improves reliability. The browser retains direct GitHub fallback.

## Provisioning gate
Before service creation, capture plan, region, runtime, sleep behavior, storage, bandwidth, build minutes, deploy frequency, credit eligibility, expiry, ownership and rollback. Obtain approval for each paid or credit-consuming action.
