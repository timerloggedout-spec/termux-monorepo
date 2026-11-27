# Source — mesh-provider-lifecycle

## Owner request

2026-11-24: Fly.io and Koyeb reappeared in the mesh after their deployment paths had become blocked/dormant. Reconcile lifecycle, count actual mesh/VM architectures, distinguish function services from VM compute, use BRR to find related branches and commits, and fix the regression.

## Repository evidence

- `docs/ops/DEVOPS-REGISTER.md` §4 records Fly.io as blocked by the ended trial/card requirement and Koyeb as dormant-blocked by the absent `KOYEB_API_TOKEN`.
- `docs/ops/INTEGRATION-MESH-MATRIX.md` retains Koyeb as a dormant deploy vendor and Fly.io as a token-only deploy surface in its 2026-11-02 census.
- `.github/workflows/deploy-hindsight.yml` and `.github/workflows/fly-hindsight-config.yml` retain Fly deployment/configuration operations.
- `.github/workflows/koyeb-hindsight-deploy.yml` retains the Koyeb deployment path.
- `docs/DEPLOYMENT-LANES.md` owns Vercel project identity and hosting-surface classification.
- `docs/architecture/INFRASTRUCTURE-REGISTRY-DESIGN.md` and the P1 authority/writer matrix require reuse of existing authorities and source-specific evidence.
- `ops/mesh/REQUESTS-SCHEMA.md` defines compute request protocol v1; `ops/vm-backup/hark-sandbox-node.json` defines `resiliency-node/v1`; `ops/compute/ALLOCATION.md` identifies Muse VM and Hark VM.
- GitHub branch search on 2026-11-24 returned 27 mesh-named branches and 19 VM-named branches. These are branch names, not runtime counts.
- PR #5807 records Cloudflare Workers/D1 account inventory and six extended utilization candidates; PR #4020 contains an offline deployment-admission scaffold; PR #1626 records initial official provider evidence.
- PR #3908, #3628, and #2663 preserve the Fly/Koyeb Hindsight deployment and configuration lineage.
- PR #5630 hardens BRR's read-only regression and promotion boundary. Issue #5552 records the outstanding private 4,103-branch registry cycle and consumer acceptance. Issue #5640 explicitly requires BRR delta, commits export, regression suite, and the existing context-relationship graph to join through current substrates.

## Evidence limits

The current GitHub session cannot access the private BRR registry artifact or prove its full cycle/consumer read. PR #5807's Cloudflare account observations remain attributed to that PR's read-only evidence. Provider account teardown and credential changes remain human-only.
