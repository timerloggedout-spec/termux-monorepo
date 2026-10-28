-- challenge participants mirror: append-only mirror of the participant
-- lists in ops/challenge/coordinator.json (the repo JSON is the source
-- of truth; design: docs/ops/CHALLENGE-PARTICIPANT-MIRROR.md).
-- Idempotent: event_key = sha256('challenge-participants'|<event>|<participant>).
-- Rows are never updated or deleted (trigger below). Safe to re-run.
-- Credentials (repo secrets, names only — same Neon route as
-- lane_events / delphi_ledger): LANE_EVENTS_DATABASE_URL or NEON_API_KEY.

-- One row per sync of the source file. sync_key keys the batch so the
-- current view can mirror the source exactly (incl. removals) while
-- history stays append-only.
CREATE TABLE IF NOT EXISTS participant_syncs (
  sync_key   text PRIMARY KEY,                 -- sha256(source_ref)
  source_ref text NOT NULL,                    -- git SHA of coordinator.json at sync
  counts     jsonb NOT NULL DEFAULT '{}'::jsonb, -- {event_id: participant count}
  synced_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS participant_events (
  event_key       text NOT NULL,               -- sha256(challenge-participants|event_id|participant_key)
  sync_key        text NOT NULL,
  event_id        text NOT NULL,               -- coordinator event id (D0..D5)
  participant_key text NOT NULL,               -- first of id/handle/username/name/url, else sha256(record)
  payload         jsonb NOT NULL,              -- the participant record verbatim
  recorded_at     timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (sync_key, event_id, participant_key)
);

CREATE INDEX IF NOT EXISTS participant_events_event_ix
  ON participant_events (event_id, participant_key);

CREATE OR REPLACE FUNCTION participant_mirror_append_only() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'participant mirror is append-only (% blocked)', TG_OP;
END $$;

DROP TRIGGER IF EXISTS participant_events_no_mutation ON participant_events;
CREATE TRIGGER participant_events_no_mutation
  BEFORE UPDATE OR DELETE ON participant_events
  FOR EACH ROW EXECUTE FUNCTION participant_mirror_append_only();

DROP TRIGGER IF EXISTS participant_syncs_no_mutation ON participant_syncs;
CREATE TRIGGER participant_syncs_no_mutation
  BEFORE UPDATE OR DELETE ON participant_syncs
  FOR EACH ROW EXECUTE FUNCTION participant_mirror_append_only();

-- Current participants = the newest sync batch, exactly mirroring the
-- source file at that sync (a participant removed from the source
-- leaves the current view; their history rows remain).
CREATE OR REPLACE VIEW participants_current AS
SELECT e.event_id, e.participant_key, e.payload, e.recorded_at
FROM participant_events e
JOIN (SELECT sync_key FROM participant_syncs ORDER BY synced_at DESC, sync_key DESC LIMIT 1) latest
  ON e.sync_key = latest.sync_key;

-- ===== MoneyBall expansion (2026-10-28): judges, signals, podium =====
-- The sync row also carries the events' core fields (id/name/prizes)
-- so views can join prizes without a second source.
ALTER TABLE participant_syncs ADD COLUMN IF NOT EXISTS events jsonb NOT NULL DEFAULT '[]'::jsonb;

-- Judges per event (coordinator events[].judges[]): same batch pattern
-- as participants. Payload verbatim (persona, org, judging_history,
-- public_criteria, statements, sources, plus any signal fields).
CREATE TABLE IF NOT EXISTS judge_events (
  event_key   text NOT NULL,                   -- sha256(challenge-judges|event_id|judge_key)
  sync_key    text NOT NULL,
  event_id    text NOT NULL,
  judge_key   text NOT NULL,
  payload     jsonb NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (sync_key, event_id, judge_key)
);
CREATE INDEX IF NOT EXISTS judge_events_event_ix ON judge_events (event_id, judge_key);

DROP TRIGGER IF EXISTS judge_events_no_mutation ON judge_events;
CREATE TRIGGER judge_events_no_mutation
  BEFORE UPDATE OR DELETE ON judge_events
  FOR EACH ROW EXECUTE FUNCTION participant_mirror_append_only();

CREATE OR REPLACE VIEW judges_current AS
SELECT e.event_id, e.judge_key, e.payload, e.recorded_at
FROM judge_events e
JOIN (SELECT sync_key FROM participant_syncs ORDER BY synced_at DESC, sync_key DESC LIMIT 1) latest
  ON e.sync_key = latest.sync_key;

-- Entity signal snapshots: APPEND-ONLY rows, never overwritten. One
-- row per snapshots[] entry ever observed on a participant or judge
-- record (comments/likes/followers/project engagement readings);
-- snapshot_key dedupes re-observation of the identical reading.
CREATE TABLE IF NOT EXISTS entity_snapshots (
  snapshot_key text PRIMARY KEY,               -- sha256(kind|event|entity|canonical snapshot)
  sync_key     text NOT NULL,
  entity_kind  text NOT NULL,                  -- participant | judge
  event_id     text NOT NULL,
  entity_key   text NOT NULL,
  snapshot     jsonb NOT NULL,
  recorded_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS entity_snapshots_entity_ix
  ON entity_snapshots (entity_kind, event_id, entity_key);

DROP TRIGGER IF EXISTS entity_snapshots_no_mutation ON entity_snapshots;
CREATE TRIGGER entity_snapshots_no_mutation
  BEFORE UPDATE OR DELETE ON entity_snapshots
  FOR EACH ROW EXECUTE FUNCTION participant_mirror_append_only();

-- Past wins across both entity kinds, from the current payloads
-- (past_wins[]{event, place, prize, project}; placements ride the
-- same extraction when present as wins-shaped entries).
CREATE OR REPLACE VIEW entity_past_wins AS
SELECT 'participant' AS entity_kind, c.event_id AS listed_in_event,
       c.participant_key AS entity_key,
       w->>'event' AS win_event, w->>'place' AS place,
       w->>'prize' AS prize, w->>'project' AS project
FROM participants_current c,
     jsonb_array_elements(CASE WHEN jsonb_typeof(c.payload->'past_wins') = 'array'
                               THEN c.payload->'past_wins' ELSE '[]'::jsonb END) w
UNION ALL
SELECT 'judge', c.event_id, c.judge_key,
       w->>'event', w->>'place', w->>'prize', w->>'project'
FROM judges_current c,
     jsonb_array_elements(CASE WHEN jsonb_typeof(c.payload->'past_wins') = 'array'
                               THEN c.payload->'past_wins' ELSE '[]'::jsonb END) w;

-- Recruitment state per entity (recruitment{candidate, pipeline_state},
-- states identified->profiled->engaged->in_talks->collaborator|passed),
-- mirrored as current entity state from the newest batch.
CREATE OR REPLACE VIEW recruitment_current AS
SELECT 'participant' AS entity_kind, event_id, participant_key AS entity_key,
       payload->'recruitment'->>'candidate' AS candidate,
       payload->'recruitment'->>'pipeline_state' AS pipeline_state
FROM participants_current WHERE payload ? 'recruitment'
UNION ALL
SELECT 'judge', event_id, judge_key,
       payload->'recruitment'->>'candidate',
       payload->'recruitment'->>'pipeline_state'
FROM judges_current WHERE payload ? 'recruitment';

-- Events of the newest sync (id/name/prizes) for the podium join.
CREATE OR REPLACE VIEW challenge_events_current AS
SELECT e->>'id' AS event_id, e->>'name' AS name, e->'prizes' AS prizes, e->'opportunity_cost' AS opportunity_cost
FROM participant_syncs s,
     jsonb_array_elements(s.events) e
WHERE s.sync_key = (SELECT sync_key FROM participant_syncs
                    ORDER BY synced_at DESC, sync_key DESC LIMIT 1);

-- Podium: prizes x competitors x profiles x judges per event — for
-- each prize tier, the competitor whose recorded past win matches
-- this event (by id or name) at that place, and the event's judges.
CREATE OR REPLACE VIEW event_podium AS
SELECT ev.event_id, ev.name AS event_name,
       tier->>'place' AS place, tier->>'award' AS award,
       pw.entity_key AS competitor, pw.project AS project,
       (SELECT jsonb_agg(j.judge_key ORDER BY j.judge_key)
          FROM judges_current j WHERE j.event_id = ev.event_id) AS judges
FROM challenge_events_current ev
CROSS JOIN LATERAL
     jsonb_array_elements(CASE WHEN jsonb_typeof(ev.prizes->'tiers') = 'array'
                               THEN ev.prizes->'tiers' ELSE '[]'::jsonb END) AS tier
LEFT JOIN entity_past_wins pw
  ON pw.entity_kind = 'participant'
 AND (pw.win_event = ev.event_id OR pw.win_event = ev.name)
 AND pw.place = tier->>'place';

-- Engagement touchpoints are EXECUTED logs (owner correction,
-- 2026-10-28): engagement is autonomous — there is no draft/approval
-- state anywhere in this schema or its writer, by design. Each
-- participant record's engagement.touchpoints[] entries
-- ({surface, at, content_ref}) are first-class mirror data, exposed
-- here as rows over the current batch.
CREATE OR REPLACE VIEW participant_touchpoints AS
SELECT c.event_id, c.participant_key,
       t->>'surface' AS surface,
       t->>'at' AS at,
       t->>'content_ref' AS content_ref
FROM participants_current c,
     jsonb_array_elements(
       CASE WHEN jsonb_typeof(c.payload->'engagement'->'touchpoints') = 'array'
            THEN c.payload->'engagement'->'touchpoints' ELSE '[]'::jsonb END) AS t;

-- ===== Opportunity cost (2026-10-28) =====
-- events[].opportunity_cost{} rides the sync events core; extracted here.
CREATE OR REPLACE VIEW event_opportunity_cost AS
SELECT ev.event_id, ev.name AS event_name,
       ev.opportunity_cost->>'outcome' AS outcome,
       (ev.opportunity_cost->'top_award'->>'value')::numeric AS top_award_value,
       ev.opportunity_cost->'top_award'->>'form' AS top_award_form,
       (ev.opportunity_cost->>'gross_foregone')::numeric AS gross_foregone,
       (ev.opportunity_cost->'win_probability'->>'estimate')::numeric AS win_probability_estimate,
       ev.opportunity_cost->'win_probability'->'basis' AS win_probability_basis,
       (ev.opportunity_cost->>'expected_value_foregone')::numeric AS expected_value_foregone,
       ev.opportunity_cost->'non_monetary_foregone' AS non_monetary_foregone,
       ev.opportunity_cost->>'computed_at' AS computed_at
FROM challenge_events_current ev
WHERE ev.opportunity_cost IS NOT NULL;

-- Migration (2026-10-28 fix): the v1/v2 PK was event_key alone, so a
-- participant's row could never re-bind to a newer sync batch and
-- participants_current went empty on the second sync. PK is the
-- (sync_key, event, entity) composite; event_key stays the stable
-- identity hash. Idempotent for databases created by the old schema.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'participant_events_pkey'
             AND pg_get_constraintdef(oid) LIKE 'PRIMARY KEY (event_key)') THEN
    ALTER TABLE participant_events DROP CONSTRAINT participant_events_pkey;
    ALTER TABLE participant_events ADD PRIMARY KEY (sync_key, event_id, participant_key);
  END IF;
  IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'judge_events_pkey'
             AND pg_get_constraintdef(oid) LIKE 'PRIMARY KEY (event_key)') THEN
    ALTER TABLE judge_events DROP CONSTRAINT judge_events_pkey;
    ALTER TABLE judge_events ADD PRIMARY KEY (sync_key, event_id, judge_key);
  END IF;
END $$;
