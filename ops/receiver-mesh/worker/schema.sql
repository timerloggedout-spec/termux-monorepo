-- Receiver Mesh — Cloudflare D1 schema. Design: docs/ops/RECEIVER-MESH.md
-- Apply at provision time: wrangler d1 execute tmx-receiver-mesh --file schema.sql
CREATE TABLE IF NOT EXISTS dedupe (
  delivery_id TEXT PRIMARY KEY,
  event TEXT,
  received_at TEXT
);
CREATE TABLE IF NOT EXISTS dead_letter (
  delivery_id TEXT PRIMARY KEY,
  event TEXT,
  envelope TEXT,
  failed_at TEXT,
  status INTEGER
);
