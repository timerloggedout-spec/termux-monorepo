-- Domain Composition Matrix. SQLite-compatible relational contract.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL, description TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS domain (domain_id TEXT PRIMARY KEY, name TEXT NOT NULL, parent_domain_id TEXT REFERENCES domain(domain_id), description TEXT NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS entity_type (entity_type_id TEXT PRIMARY KEY, domain_id TEXT REFERENCES domain(domain_id), name TEXT NOT NULL, kind TEXT NOT NULL, description TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS operation (operation_id TEXT PRIMARY KEY, canonical_name TEXT NOT NULL, semantic_family TEXT NOT NULL, description TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS notation (notation_id TEXT PRIMARY KEY, operation_id TEXT REFERENCES operation(operation_id), domain_id TEXT REFERENCES domain(domain_id), language TEXT, surface TEXT NOT NULL, canonical_form TEXT, description TEXT NOT NULL, status TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS composition_rule (rule_id TEXT PRIMARY KEY, domain_id TEXT NOT NULL REFERENCES domain(domain_id), source_entity_type_id TEXT NOT NULL REFERENCES entity_type(entity_type_id), operation_id TEXT NOT NULL REFERENCES operation(operation_id), target_entity_type_id TEXT NOT NULL REFERENCES entity_type(entity_type_id), result_entity_type_id TEXT, notation_id TEXT REFERENCES notation(notation_id), precedence INTEGER, associative INTEGER, identity_required INTEGER, valid INTEGER NOT NULL, status TEXT NOT NULL, confidence REAL, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS constraint_rule (constraint_id TEXT PRIMARY KEY, rule_id TEXT NOT NULL REFERENCES composition_rule(rule_id), constraint_kind TEXT NOT NULL, expression TEXT NOT NULL, description TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence (evidence_id TEXT PRIMARY KEY, rule_id TEXT NOT NULL REFERENCES composition_rule(rule_id), source_ref TEXT NOT NULL, source_kind TEXT NOT NULL, locator TEXT, claim TEXT NOT NULL, observed_at TEXT, confidence REAL);
CREATE TABLE IF NOT EXISTS projection (projection_id TEXT PRIMARY KEY, rule_id TEXT NOT NULL REFERENCES composition_rule(rule_id), target_surface TEXT NOT NULL, target_path TEXT NOT NULL, generated INTEGER NOT NULL, source_sha TEXT, generated_at TEXT);
CREATE INDEX IF NOT EXISTS idx_rule_domain ON composition_rule(domain_id);
CREATE INDEX IF NOT EXISTS idx_rule_operation ON composition_rule(operation_id);
CREATE INDEX IF NOT EXISTS idx_rule_status ON composition_rule(status);
CREATE INDEX IF NOT EXISTS idx_evidence_rule ON evidence(rule_id);