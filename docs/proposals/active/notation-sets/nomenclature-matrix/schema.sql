PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS sources (
  source_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  url TEXT NOT NULL,
  source_type TEXT NOT NULL,
  authority TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS concepts (
  concept_id TEXT PRIMARY KEY,
  domain_id TEXT NOT NULL,
  preferred_label TEXT NOT NULL,
  definition TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('discovered','candidate','evidence_backed','reviewed','accepted','rejected','deprecated','superseded')),
  version INTEGER NOT NULL CHECK(version > 0)
);
CREATE TABLE IF NOT EXISTS concept_sources (
  concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  PRIMARY KEY(concept_id, source_id)
);
CREATE TABLE IF NOT EXISTS labels (
  label_id TEXT PRIMARY KEY,
  concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
  text TEXT NOT NULL,
  label_type TEXT NOT NULL CHECK(label_type IN ('preferred_formal','preferred_plain_language','alternative_synonym','colloquial','ad_hoc','jargon','abbreviation','symbolic_notation','historical','deprecated','misspelling','translation','analogy','near_synonym','related_term','external_identifier','hidden_search_alias')),
  language TEXT NOT NULL,
  audience TEXT NOT NULL,
  register TEXT NOT NULL,
  status TEXT NOT NULL CHECK(status IN ('discovered','candidate','evidence_backed','reviewed','accepted','rejected','deprecated','superseded'))
);
CREATE TABLE IF NOT EXISTS label_sources (
  label_id TEXT NOT NULL REFERENCES labels(label_id),
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  PRIMARY KEY(label_id, source_id)
);
CREATE TABLE IF NOT EXISTS mappings (
  mapping_id TEXT PRIMARY KEY,
  source_concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
  target_concept_id TEXT NOT NULL REFERENCES concepts(concept_id),
  relation TEXT NOT NULL CHECK(relation IN ('same_concept_label','exact_match','close_match','broad_match','narrow_match','related_match','explains','analogy_to','translates_to','supersedes','ambiguous_with','contradicts')),
  status TEXT NOT NULL CHECK(status IN ('discovered','candidate','evidence_backed','reviewed','accepted','rejected','deprecated','superseded')),
  confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 1),
  evidence_note TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mapping_sources (
  mapping_id TEXT NOT NULL REFERENCES mappings(mapping_id),
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  PRIMARY KEY(mapping_id, source_id)
);
CREATE INDEX IF NOT EXISTS idx_labels_concept ON labels(concept_id);
CREATE INDEX IF NOT EXISTS idx_labels_text ON labels(text);
CREATE INDEX IF NOT EXISTS idx_mappings_source ON mappings(source_concept_id);
CREATE INDEX IF NOT EXISTS idx_mappings_target ON mappings(target_concept_id);

CREATE TABLE IF NOT EXISTS evidence_records (
  evidence_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  assertion_type TEXT NOT NULL CHECK(assertion_type IN ('concept','label','mapping')),
  assertion_id TEXT NOT NULL,
  claim TEXT NOT NULL,
  evidence_locator TEXT NOT NULL,
  evidence_excerpt TEXT NOT NULL,
  retrieved_on TEXT NOT NULL CHECK(retrieved_on GLOB '????-??-??'),
  reviewer TEXT,
  status TEXT NOT NULL CHECK(status IN ('discovered','candidate','evidence_backed','reviewed','accepted','rejected','deprecated','superseded')),
  CHECK(status != 'accepted' OR (reviewer IS NOT NULL AND length(trim(reviewer)) > 0 AND length(trim(evidence_excerpt)) > 0))
);
CREATE INDEX IF NOT EXISTS idx_evidence_assertion ON evidence_records(assertion_type, assertion_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence_records(source_id);
