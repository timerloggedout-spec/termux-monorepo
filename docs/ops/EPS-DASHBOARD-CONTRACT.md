# EPS Dashboard Contract

The dashboard is a consumer of EPS, never its producer.

## Required primitives

- freshness and last observed event
- ingestion and validation rate
- volume by source/type/status
- provenance drill-down
- run and attempt timeline
- attribution-confidence distribution
- stale/partial/unverified evidence
- replay/duplicate rejection
- ML/Hex/Grafana derived links
- projection health including Gource/render adapters

Every panel declares: metric, EPS event types, reducer, freshness, provenance drill-down, and failure semantics.

Missing evidence must never silently become zero.

Gource, SHE/Vercel and future WebGL/WASM interaction consume the same EPS projections. A visual interaction may link to event IDs/source refs but cannot author telemetry.

## Acceptance

A dashboard feature is accepted only when its metric has an EPS source/reducer, missing/stale/partial evidence is visible, source evidence is reachable, replay does not inflate it, and a non-visual evidence path reproduces the finding.
