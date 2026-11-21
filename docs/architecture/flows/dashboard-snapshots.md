# Dashboard, Snapshot and Surface Consumers

**Inputs:** historical corpus/CRG; validated EPS and ATES evidence where configured; operational feeds; Tribute JSON feeds.

**Snapshot path:** SHE pure reducers → snapshot builder → versioned read-only snapshot. Contract requires schema_version, snapshot_id, source_ref, source_sha, generated_at, coverage and corpus manifest SHA. Vercel is the primary interactive surface; Pages and Hex are optional consumers. Tribute consumes a separate committed feed family.

**Findings:** corpus → SHE reducers → snapshot → Vercel is documented. Pages/Hex require current deployment/import evidence. Tribute feeds are a separate projection silo; shared repository does not prove automatic synchronization. Display source_sha, generated_at, coverage and manifest SHA together. Historical views use immutable L2 snapshots.

**Sources:** [SHE architecture](../../ops/SHE-DASHBOARD-ARCHITECTURE.mmd) · [Snapshot contract](../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md) · [Tribute feed](../../ops/TRIBUTE-EVIDENCE-FEED.md)
