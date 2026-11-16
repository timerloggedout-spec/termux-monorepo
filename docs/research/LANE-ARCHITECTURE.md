# Research Lane Architecture

Status: IMPLEMENTED design contract
Owner: termux-monorepo management hub
Integration model: lanes may live in sibling organizations (for example Research-Astute) and publish normalized evidence to the hub.

## Principles
1. Research lanes are independent workspaces, not required to live inside the monorepo.
2. The hub consumes evidence, not vendor dashboards.
3. Every resource keeps canonical provenance, observed date, version/commit, evidence status, confidence, and unresolved questions.
4. H0-H3 is a horizon signal, not a truth score.
5. FOSS procurement decisions are explicit and reversible.
6. Malware/reverse-engineering research is authorized defensive/research work only; samples stay isolated from production paths.
7. Cloud emulators are development/test surfaces, not production substitutes or security oracles.
8. Upstream projects with explicit read-only contribution policies remain read-only; independent extensions belong in our own repositories.

## Lane families
- foresight-radar
- ai-technology
- science-research
- foss-developer-tools
- emerging-technology
- agent-observability
- multi-agent-evaluation
- reproducible-environments
- local-edge-arm-android
- agentic-security
- malware-reverse-engineering
- provenance-supply-chain
- accelerators-materials-energy
- procurement-opportunities
- cloud-emulator-fidelity

## Org separation
Each lane may be hosted by a separate GitHub organization/repository. The hub registry records:
- org/repository
- lane id
- maintainer
- evidence feed
- schema version
- synchronization timestamp
- integration status

The hub must never require write access to a research organization merely to ingest its public evidence.

## Evidence flow
source -> resource registry -> lane evidence -> radar classification -> procurement assessment -> hub digest -> management cockpit

## Required identifiers
Every evidence record has a stable `resource_id`; every digest item has `item_id`; every lane has a stable `lane_id`.

## Termux portability
Lane tooling should prefer Python/std-lib, POSIX shell, JSON/YAML, SQLite, Git, and HTTP interfaces. Heavy services are optional adapters.

## Cloud emulator fidelity lane
The `cloud-emulator-fidelity` lane studies local cloud emulation as an agent feedback substrate. It composes existing research lanes rather than replacing them:
- `reproducible-environments` owns Docker/CI environment parity.
- `agent-observability` owns execution telemetry and environment fingerprints.
- `multi-agent-evaluation` owns controlled manager/agent comparisons.
- `agentic-security` owns sandbox, credential, and tool-permission boundaries.
- `cloud-emulator-fidelity` owns emulator/API-contract coverage, behavioral fidelity evidence, and real-cloud differential validation.

The lane's initial AWS sources are the public AWS Emulator, AWS API Models (Smithy JSON AST), and AWS Emulator Evaluation Suite. The two user-owned forks are upstream tracking mirrors until a separately reviewed local extension is proposed. Neither fork is treated as an upstream contribution channel: the upstream emulator README says it does not accept PRs, and the evaluation-suite README says it is read-only.

The lane publishes normalized evidence to the management hub; it does not create a second experiment ledger, event bus, scheduler, provider router, or merge authority.
