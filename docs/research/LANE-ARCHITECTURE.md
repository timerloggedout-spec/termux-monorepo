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
7. Sponsored research is an opportunity and funding mechanism, not a source of authority over research conclusions or project roadmaps.
8. Public-good outputs retain their own license, provenance, governance, maintenance status, and downstream-use evidence.

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
- sponsored-research-public-goods

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

## Sponsored research and public goods
The `sponsored-research-public-goods` lane is governed by `docs/research/SPONSORED-RESEARCH-PUBLIC-GOODS-LANE.md`. It separates:
- opportunity intelligence and eligibility screening;
- disciplinary research and evidence synthesis;
- project incubation and partner formation;
- sponsor-specific proposal/application work;
- delivery of openly licensed public goods;
- independent evaluation, adoption, and sustainability.

A sponsor's scope, evaluation criteria, and reporting obligations are recorded as constraints for that opportunity. They do not silently become universal research policy. Funding status and technical/research validation are separate states.

## Evidence flow
source -> resource registry -> lane evidence -> radar classification -> procurement assessment -> hub digest -> management cockpit

For sponsored/public-good work, the extended flow is:
opportunity -> eligibility/fit screen -> domain model -> partner/capability map -> project brief -> funded or unfunded execution -> open artifact release -> adoption/effect evidence -> hub digest

## Required identifiers
Every evidence record has a stable `resource_id`; every digest item has `item_id`; every lane has a stable `lane_id`.

## Termux portability
Lane tooling should prefer Python/std-lib, POSIX shell, JSON/YAML, SQLite, Git, and HTTP interfaces. Heavy services are optional adapters.
