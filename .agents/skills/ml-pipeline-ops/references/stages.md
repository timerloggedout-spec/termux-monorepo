# Stages

| id | halt |
|----|------|
| 00_recon | FAILED |
| 10_ingest | FAILED |
| 20_features | FAILED |
| 30_train | FAILED |
| 40_evaluate | FAILED |
| 50_deploy | FAILED (must not promote without dual-gate) |
| 60_monitor | FAILED |

Deploy writes a promote packet only when `contracts.gate.assert_promotable` succeeds.
