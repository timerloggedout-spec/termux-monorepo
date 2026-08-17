# Source — ICM Architect Integration

On 2026-08-17, the operator requested that `RinDig/ICM-Architect` be forked as `timerloggedout-spec/icm-architect_fork`, then brought into `timerloggedout-spec/termux-monorepo` as a customization-friendly Git submodule with documentation.

The implementation follows the existing `refTemplates/smods/*_fork` convention already present on `master-staging`. The pinned submodule is intentionally shallow and tracks the fork’s `main` branch for explicit, reviewable updates. No upstream code is copied into the monorepo; the Gitlink preserves a specific source revision while the fork provides the customization boundary.
