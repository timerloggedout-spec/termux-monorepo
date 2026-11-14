# AMD + NVIDIA Skills Integration

**Status:** documentation/registry integration; no hardware execution is implied.

## Purpose
Make vendor skill workflows discoverable, gated, reproducible, and evidence-producing for `termux-monorepo` and the AMD AI League project. This contract does not copy vendor implementations, install external skills, add credentials, or claim benchmarks that have not run.

## AMD skills available in the assistant environment
- `hyperloom-workload-optimizer` — conditional optimization on supported AMD Instinct hardware; requires ROCm/GPU preflight.
- `serving-llms-on-instinct` — LLM serving on compatible AMD Instinct/ROCm infrastructure.
- `local-ai-app-integration` — local/offline integration using Embeddable Lemonade.
- `local-ai-use` — routes supported image/audio tasks through a configured local Lemonade server.
- `tracelens-analysis-orchestrator` — modular PyTorch profiler trace analysis.

These entries describe skill availability in the assistant environment, not installation or execution on a target machine.

## NVIDIA discovery
Upstream catalog: https://github.com/NVIDIA/skills/tree/main/skills. Catalog discovery is not installation. Before adopting any entry, verify exact path, commit/release, license, runtime prerequisites, and supported hardware. Keep NVIDIA optional unless it materially improves the project.

## Execution policy
1. Run AMD serving workloads only with a verified compatible AMD environment.
2. Run Hyperloom only after supported Instinct hardware, ROCm health, GPU availability, and workload preflight succeed.
3. Run local AI paths only after the Lemonade runtime is configured and health-checked.
4. Analyze profiler traces only when a real trace exists; sanitize traces before sharing.
5. Run NVIDIA/CUDA paths only with verified hardware or an explicitly documented remote environment.
6. Compare vendors only on matched tasks, comparable quality criteria, documented model/runtime versions, repeatable runs, and disclosed uncertainty.
7. No GPU-dependent test should be required on generic CI. Missing hardware produces a `BLOCKED` receipt, not false success.

## Evidence and privacy
Every execution receipt must identify the skill and upstream reference; status (`discovered`, `installed`, `selected`); execution state (`not_run`, `blocked`, `executed`, `validated`); timestamp; hardware/runtime fingerprint; workload/dataset; evaluation method; baseline; repetitions; metrics; exit/test results; artifact hashes; and limitations. Missing measurements are null/unknown, never inferred.

Do not publish credentials, prompts, completions, private source, arbitrary tool payloads, or unredacted profiler traces by default. Preserve the distinction between `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED`.

## AMD AI League application
The skills are an implementation lane, not the project itself. Select the challenge project through the repository's Delphi/Oracle Method process, then build a runnable demo with regression tests and sanitized evidence. Use AMD technology where available and relevant; include NVIDIA only if the measured benefit justifies added complexity.

## Rollout checklist
- [ ] Reconcile with existing registries before adding a duplicate canonical registry.
- [x] Add a receipt JSON Schema and deterministic vendor-registry validator.
- [x] Add focused tests for required registry fields, allowed states, discovery-only NVIDIA status, and sensitive-field-name rejection.
- [x] Add a least-privilege GitHub Actions workflow for JSON parsing, registry validation, and focused contract tests.
- [ ] Confirm the new workflow executes successfully on GitHub; a run was not yet visible at the time of this update.
- [ ] Run an AMD baseline in an approved environment or record the precise blocker.
- [ ] Add NVIDIA execution only after runtime access is verified.
- [ ] Record results in the repository's existing evidence lane.


## Validation implementation

- Receipt contract: `docs/ops/AMD-NVIDIA-SKILL-EXECUTION-RECEIPT.schema.json`.
- Deterministic registry checks: `scripts/ci/validate_vendor_skill_registry.py`.
- Focused regression tests: `tests/test_vendor_skill_registry.py`.
- CI entry point: `.github/workflows/amd-nvidia-skill-registry.yml` (read-only repository permission; no GPU workload is run).
- Vendor router skill entry points: `skills/vendors/amd/SKILL.md` and `skills/vendors/nvidia/SKILL.md`.

The validator checks registry structure and policy invariants without requiring a GPU or external dependency. The JSON Schema is committed as a contract; this workflow currently verifies that it is valid JSON and that its required receipt fields are present. Full standards-based instance validation should be added if a JSON Schema validator is adopted as a repository dependency.
