# Inventory dry-run — addendum: PAT-integration map + classification + repo decision

[MUSEai]@{role:{appid-migration-plan}} · 2026-11-03 · completes the first-execution brief (8 Apps + installations + PAT-integration map; MATCH/DRIFT/UNREPLAYABLE + G4 receipts)

## Classification (per item, terminal vocabulary of the program)

- 8 Apps: **MATCH** ×8 (declared == observed permissions, firsthand custody-helper probes; artifact `inventory-2026-11-03.json`). DRIFT: none. UNREPLAYABLE: none.
- Read-model implementation: `ops/github-apps/control-plane/` (schema.sql + loader) over the lane-events Neon store, applied by `.github/workflows/appid-control-plane-inventory.yml` (dispatch-only); load receipt = the workflow's G4-shaped artifact; the dry-run itself is seeded as replay_runs row `inventory-dry-run-2026-11-03` (classification MATCH).

## PAT-integration map (names only — values never recorded)

| Route | Where it integrates | Role in the family |
|---|---|---|
| Vault PAT helper (`custom.github-pat`, MUSE_ADMIN_GH) | Lane-side canonical route (this seat + fleet lanes) | Primary where no App fits; fallback under G5 for every app route |
| `OPERATOR_GITHUB_TOKEN` (Actions secret) | 44 workflow files | Operator-interactive identity — identity-bound by design (MIG-08), NOT a migration target |
| `ARCHWIZ_GITHUB_TOKEN` (Actions secret) | 30 workflow files | Named-operator rider (ArchWiz surfaces) |
| `OPERATOR_TOKEN` · `RECON_INTEL_GITHUB_WRITE_TOKEN` · `VANTAGE_PAT_GH_SECRETS` | Scoped workflow/provisioning uses | Per-surface riders; VANTAGE = secrets-provisioning PAT |
| Default `GITHUB_TOKEN` | 1,000/h per-repo installation bucket | Per-repo automation (DevOps §5 census classes stay per plan dispositions) |

Retirement law (program): a PAT route retires **per item**, only after that item's migration is verified (oracle + G4 receipt), with the fallback path kept — no bulk retirement.

## Repo decision (on evidence, per main's stage order)

**No repo yet.** Evidence: the build so far = schema + loader + one dispatch workflow inside the monorepo + tables in the existing Neon project; nothing requires independent deploy, cadence, or access control. Revisit triggers: first scheduled (non-dispatch) refresh cadence, or control-plane code growth beyond the loader. When created, the repo takes the Registry-issued name (confer open: candidate `appid-registrar`) and this record migrates as its lineage seed.
