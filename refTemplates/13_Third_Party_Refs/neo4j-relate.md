# Neo4j Relate — refTemplates entry

- **What:** Relate — Neo4j's open-source, in-memory database for AI agents, built in Rust; runs in-process inside the agent's own application (no server round-trip).
- **Source:** Neo4j release, 2026-11-12 — https://www.businesswire.com/news/home/20261111833667/en/New-In-Memory-Database-Purpose-Built-for-AI-Agents
- **Status (owner order 2026-11-18):** ADOPTION + DoE score + evolution — adopted as a fleet surface, scored by DoE against incumbents, evolved through generations. Not intake-only.

## Fleet fits
1. **Staging index** (QUE #5309 staging design) — the interception-fed working set {item - class - rank - state - stage timestamps}; in-process reads for the watchdog and the drains, no Neon round-trip per read.
2. **Graph planes** — CEEL capability-evidence graph + the comment/context graph join (QUE #5640) + BRR branch/commit graph: traversals inside the agent.
3. **Brain working state** — under the brain.rs facade on the VM seat; typed-stage state held in-process.

## Bounds
- In-memory = RAM-bound: working sets only (VM ~8 GB), never archives.
- Persistence story verified at build time; the store of record stays the repo + Neon until DoE scores durability.

## DoE score + evolution
- Scored per generation against the incumbent per fit {staging: Neon reads + committed feeds - graphs: current traversal code - brain: in-process structures}.
- Criteria pre-registered at first build: read latency on the live working set - traversal depth/time on the #5640 join - memory footprint vs the 8 GB ceiling - durability behaviour across VM replacement.
- Evolution: winning fits promote per-surface; losing fits retire to this entry as evidence.
