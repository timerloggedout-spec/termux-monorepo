# SYNAPSE Proposal Lane

This directory is for design proposals that are not yet accepted implementation contracts.

A proposal must state:
1. the uncovered capability and the region/network analogy;
2. existing repository components that could be reused;
3. the smallest viable interface;
4. data and privacy boundaries;
5. authority and failure behavior;
6. alternatives, including doing nothing;
7. a measurable validation plan;
8. rollout, rollback, and retirement conditions.

Proposals must not create shadow routers, duplicate telemetry stores, or bypass existing repository governance. Prefer extending the manager, event, evidence, context-graph, SHE, and ATES/3L0 contracts.

Initial candidate proposals are indexed in [the neuro-inspired research lane](../research/neuro-inspired-patterns.md) and [the evolution roadmap](../roadmap/evolution-roadmap.md).
